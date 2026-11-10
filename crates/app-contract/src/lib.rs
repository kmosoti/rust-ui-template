//! Versioned, serializable host boundary. No UI, browser, or native authority.
use serde::{Deserialize, Serialize};

pub const SCHEMA_VERSION: u16 = 1;

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct InfoRequest {
    pub schema_version: u16,
}

impl InfoRequest {
    pub fn validate(&self) -> Result<(), HostError> {
        if self.schema_version == SCHEMA_VERSION {
            Ok(())
        } else {
            Err(HostError::UnsupportedVersion)
        }
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AppInfo {
    pub schema_version: u16,
    pub name: String,
    pub version: String,
    pub platform: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum HostError {
    Unsupported,
    UnsupportedVersion,
    InvocationFailed,
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn accepts_current_schema_and_rejects_other_versions() {
        assert!(
            InfoRequest {
                schema_version: SCHEMA_VERSION
            }
            .validate()
            .is_ok()
        );
        assert_eq!(
            InfoRequest { schema_version: 0 }.validate(),
            Err(HostError::UnsupportedVersion)
        );
        assert_eq!(
            InfoRequest {
                schema_version: u16::MAX
            }
            .validate(),
            Err(HostError::UnsupportedVersion)
        );
    }
    #[test]
    fn rejects_missing_unknown_and_invalid_input_fields() {
        for json in [
            "{}",
            r#"{"schema_version":1,"path":"/etc/passwd"}"#,
            r#"{"schema_version":-1}"#,
            r#"{"schema_version":"1"}"#,
        ] {
            assert!(serde_json::from_str::<InfoRequest>(json).is_err());
        }
    }
}
