use super::{Completion, IdExhausted, LatestRequest, RequestId};

#[test]
fn starts_empty() {
    let state = LatestRequest::<u32>::default();
    assert_eq!(state.active(), None);
    assert_eq!(state.value(), None);
}

#[test]
fn ids_increase_and_cancellation_does_not_reuse_them() {
    let mut state = LatestRequest::<u32>::new();
    let first = state.begin().unwrap();
    state.cancel();
    let second = state.begin().unwrap();
    assert_eq!(first.get(), 1);
    assert_eq!(second.get(), 2);
    assert_eq!(state.active(), Some(second));
}

#[test]
fn current_completion_commits_once() {
    let mut state = LatestRequest::new();
    let id = state.begin().unwrap();
    assert_eq!(state.complete(id, 42), Completion::Applied);
    assert_eq!(state.active(), None);
    assert_eq!(state.value(), Some(&42));
    let before = state;
    assert_eq!(state.complete(id, 99), Completion::Ignored);
    assert_eq!(state, before);
}

#[test]
fn stale_completion_cannot_overwrite_newer_result() {
    let mut state = LatestRequest::new();
    let old = state.begin().unwrap();
    let current = state.begin().unwrap();
    assert_eq!(state.complete(current, 20), Completion::Applied);
    let before = state;
    assert_eq!(state.complete(old, 10), Completion::Ignored);
    assert_eq!(state, before);
}

#[test]
fn stale_completion_cannot_clear_a_pending_newer_request() {
    let mut state = LatestRequest::new();
    let old = state.begin().unwrap();
    let current = state.begin().unwrap();
    let before = state;
    assert_eq!(state.complete(old, 10), Completion::Ignored);
    assert_eq!(state, before);
    assert_eq!(state.active(), Some(current));
}

#[test]
fn superseding_a_request_preserves_the_last_committed_value() {
    let mut state = LatestRequest::new();
    let first = state.begin().unwrap();
    assert_eq!(state.complete(first, 7), Completion::Applied);
    let next = state.begin().unwrap();
    assert_eq!(state.value(), Some(&7));
    assert_eq!(state.active(), Some(next));
}

#[test]
fn cancel_is_idempotent_and_revokes_pending_completion() {
    let mut state = LatestRequest::new();
    let first = state.begin().unwrap();
    assert_eq!(state.complete(first, 7), Completion::Applied);
    let pending = state.begin().unwrap();
    state.cancel();
    let cancelled = state;
    state.cancel();
    assert_eq!(state, cancelled);
    assert_eq!(state.complete(pending, 99), Completion::Ignored);
    assert_eq!(state, cancelled);
    assert_eq!(state.value(), Some(&7));
}

#[test]
fn unissued_id_does_not_change_state() {
    let mut state = LatestRequest::<u32>::new();
    let before = state;
    assert_eq!(state.complete(RequestId(1), 1), Completion::Ignored);
    assert_eq!(state, before);
}

#[test]
fn stale_failure_cannot_replace_current_success() {
    let mut state = LatestRequest::<Result<u32, &'static str>>::new();
    let old = state.begin().unwrap();
    let current = state.begin().unwrap();
    assert_eq!(state.complete(current, Ok(42)), Completion::Applied);
    let before = state;
    assert_eq!(state.complete(old, Err("late")), Completion::Ignored);
    assert_eq!(state, before);
}

#[test]
fn active_failure_is_a_committed_result() {
    let mut state = LatestRequest::<Result<u32, &'static str>>::new();
    let id = state.begin().unwrap();
    assert_eq!(state.complete(id, Err("failed")), Completion::Applied);
    assert_eq!(state.value(), Some(&Err("failed")));
    assert_eq!(state.active(), None);
}

#[test]
fn highest_id_is_usable_and_exhaustion_is_atomic() {
    // An internal boundary fixture avoids iterating through 2^64 starts.
    let mut state = LatestRequest {
        last_issued: u64::MAX - 1,
        active: None,
        value: Some(5_u32),
    };
    let last = state.begin().unwrap();
    assert_eq!(last.get(), u64::MAX);
    let before = state;
    assert_eq!(state.begin(), Err(IdExhausted));
    assert_eq!(state, before);
    assert_eq!(state.complete(last, 9), Completion::Applied);
    let completed = state;
    assert_eq!(state.begin(), Err(IdExhausted));
    assert_eq!(state, completed);
}

#[test]
fn every_three_request_completion_order_preserves_latest_wins() {
    for order in [
        [0, 1, 2],
        [0, 2, 1],
        [1, 0, 2],
        [1, 2, 0],
        [2, 0, 1],
        [2, 1, 0],
    ] {
        let mut state = LatestRequest::new();
        let ids = [
            state.begin().unwrap(),
            state.begin().unwrap(),
            state.begin().unwrap(),
        ];
        let values = [10, 20, 30];
        for index in order {
            let before = state;
            let result = state.complete(ids[index], values[index]);
            if index == 2 {
                assert_eq!(result, Completion::Applied);
            } else {
                assert_eq!(result, Completion::Ignored);
                assert_eq!(state, before);
            }
        }
        assert_eq!(state.value(), Some(&30));
    }
}

#[test]
fn bounded_event_sequences_preserve_freshness_and_monotonic_ids() {
    // Enumerate every prefix through depth 6 over Start, Cancel, and four
    // possible completion IDs. This is bounded testing, not a formal proof.
    fn visit(state: LatestRequest<u32>, remaining: u8, count: &mut u32) {
        *count += 1;
        if remaining == 0 {
            return;
        }
        let mut started = state;
        let id = started.begin().unwrap();
        assert_eq!(id.get(), state.last_issued + 1);
        assert_eq!(started.value(), state.value());
        visit(started, remaining - 1, count);

        let mut cancelled = state;
        cancelled.cancel();
        assert_eq!(cancelled.active(), None);
        assert_eq!(cancelled.value(), state.value());
        assert_eq!(cancelled.last_issued, state.last_issued);
        visit(cancelled, remaining - 1, count);

        for raw_id in 1..=4_u64 {
            let mut completed = state;
            let result = completed.complete(RequestId(raw_id), 100);
            if state.active() == Some(RequestId(raw_id)) {
                assert_eq!(result, Completion::Applied);
                assert_eq!(completed.value(), Some(&100));
                assert_eq!(completed.active(), None);
                assert_eq!(completed.last_issued, state.last_issued);
            } else {
                assert_eq!(result, Completion::Ignored);
                assert_eq!(completed, state);
            }
            visit(completed, remaining - 1, count);
        }
    }
    let mut count = 0;
    visit(LatestRequest::new(), 6, &mut count);
    assert_eq!(count, 55_987);
}
