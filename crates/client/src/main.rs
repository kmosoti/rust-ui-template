mod host;
use leptos::prelude::*;
fn main() {
    leptos::mount::mount_to_body(|| view! { <app_ui::App read_host_info=host::app_info /> });
}
