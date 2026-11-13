//! Compile and execute Wry's actual Android injection source on a host without GTK.
#![allow(dead_code)]
pub struct InitializationScript {
    pub script: String,
    pub for_main_frame_only: bool,
}
#[rustfmt::skip]
#[path = "../../../../vendor/wry-0.57.2/src/inject_initialization_scripts.rs"]
mod inject_initialization_scripts;
