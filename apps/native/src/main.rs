#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use app_contract::{AppInfo, HostError, InfoRequest, SCHEMA_VERSION};

#[tauri::command]
fn app_info(request: InfoRequest) -> Result<AppInfo, HostError> {
    request.validate()?;
    Ok(AppInfo {
        schema_version: SCHEMA_VERSION,
        name: "rust-ui-template".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        platform: std::env::consts::OS.to_string(),
    })
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![app_info])
        .run(tauri::generate_context!())
        .expect("run native client");
}
