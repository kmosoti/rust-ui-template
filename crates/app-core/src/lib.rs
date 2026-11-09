//! Framework-independent state for a latest-request-wins interaction.
//!
//! The adapter starts work and supplies a returned [`RequestId`] on completion.
//! This crate performs no I/O, does not schedule work, and has no dependencies.
//! Starting a newer request revokes the previous request's right to commit.
//!
//! ```
//! use app_core::{Completion, LatestRequest};
//!
//! let mut state = LatestRequest::new();
//! let old = state.begin().expect("request IDs available");
//! let new = state.begin().expect("request IDs available");
//! assert_eq!(state.complete(new, 20), Completion::Applied);
//! assert_eq!(state.complete(old, 10), Completion::Ignored);
//! assert_eq!(state.value(), Some(&20));
//! ```
//!
//! IDs are unique only within one tracker lifetime, not across trackers,
//! processes, resets, persistence, or sessions. Keep an async completion bound
//! to its originating tracker/owner. An ID is not an authorization credential.

#![no_std]
#![forbid(unsafe_code)]

/// A request identifier issued by one [`LatestRequest`] instance.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[must_use]
pub struct RequestId(u64);

impl RequestId {
    /// Numeric representation for diagnostics, not for constructing authority.
    #[must_use]
    pub const fn get(self) -> u64 {
        self.0
    }
}

/// The finite identifier space is exhausted. The tracker was not changed.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct IdExhausted;

/// Whether a completion was allowed to change the committed result.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[must_use]
pub enum Completion {
    Applied,
    Ignored,
}

/// Latest-request-wins state with a retained last committed value.
///
/// `T` may be `Result<Value, Error>`; success and failure then obey the same
/// freshness rule. Cancellation invalidates pending work but does not stop I/O.
/// The adapter owns cancellation, scheduling, and reactive-owner cleanup.
/// Cloning is useful for snapshots; do not treat a clone as a fresh ID namespace.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct LatestRequest<T> {
    last_issued: u64,
    active: Option<RequestId>,
    value: Option<T>,
}

impl<T> LatestRequest<T> {
    #[must_use]
    pub const fn new() -> Self {
        Self {
            last_issued: 0,
            active: None,
            value: None,
        }
    }

    /// Reserve a new ID and supersede pending work, retaining the last result.
    ///
    /// # Errors
    /// Returns [`IdExhausted`] before changing any state when another ID cannot
    /// be represented. IDs never wrap and are never reused within this tracker.
    pub fn begin(&mut self) -> Result<RequestId, IdExhausted> {
        let next = self.last_issued.checked_add(1).ok_or(IdExhausted)?;
        let id = RequestId(next);
        self.last_issued = next;
        self.active = Some(id);
        Ok(id)
    }

    /// Commit exactly once, and only for the currently active request.
    ///
    /// Stale, cancelled, and duplicate completions leave the tracker unchanged.
    /// An ignored value is dropped normally; side effects of `T::drop`, if any,
    /// are outside the state-transition contract.
    pub fn complete(&mut self, id: RequestId, value: T) -> Completion {
        if self.active != Some(id) {
            return Completion::Ignored;
        }
        self.active = None;
        self.value = Some(value);
        Completion::Applied
    }

    /// Revoke pending work's right to commit without erasing the last result.
    ///
    /// This does not cancel a network request or timer. Do that in the adapter.
    pub fn cancel(&mut self) {
        self.active = None;
    }

    #[must_use]
    pub const fn active(&self) -> Option<RequestId> {
        self.active
    }

    #[must_use]
    pub const fn value(&self) -> Option<&T> {
        self.value.as_ref()
    }
}

impl<T> Default for LatestRequest<T> {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests;
