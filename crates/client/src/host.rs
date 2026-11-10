use app_contract::{AppInfo, HostError, InfoRequest, SCHEMA_VERSION};
use futures::{FutureExt, future::LocalBoxFuture};
use wasm_bindgen::prelude::*;

#[wasm_bindgen(
    inline_js = "export function isDesktop() { return !!window.__TAURI_INTERNALS__; } export async function readInfo(request) { return window.__TAURI_INTERNALS__.invoke('app_info', { request }); }"
)]
extern "C" {
    #[wasm_bindgen(js_name = isDesktop)]
    fn is_desktop() -> bool;
    #[wasm_bindgen(catch, js_name = readInfo)]
    async fn read_info(request: JsValue) -> Result<JsValue, JsValue>;
}

pub fn app_info() -> LocalBoxFuture<'static, Result<AppInfo, HostError>> {
    async {
        if !is_desktop() {
            return Err(HostError::Unsupported);
        }
        let request = serde_wasm_bindgen::to_value(&InfoRequest {
            schema_version: SCHEMA_VERSION,
        })
        .map_err(|_| HostError::InvocationFailed)?;
        let info = read_info(request)
            .await
            .map_err(|_| HostError::InvocationFailed)?;
        let info: AppInfo =
            serde_wasm_bindgen::from_value(info).map_err(|_| HostError::InvocationFailed)?;
        if info.schema_version != SCHEMA_VERSION {
            return Err(HostError::UnsupportedVersion);
        }
        Ok(info)
    }
    .boxed_local()
}
