//! Browser viewport adaptation; Leptos owns the listener and focused-field scroll.
use gloo_events::EventListener;
use std::cell::Cell;

pub fn keep_focused_field_visible() -> EventListener {
    let window = web_sys::window().expect("browser window");
    let observed = window.clone();
    let previous_height = Cell::new(height(&window));
    EventListener::new(&window, "resize", move |_| {
        let current_height = height(&observed);
        let previous = previous_height.replace(current_height);
        if current_height <= 0.0 || current_height >= previous {
            return;
        }
        let Some(field) = observed
            .document()
            .and_then(|document| document.active_element())
        else {
            return;
        };
        if !matches!(field.tag_name().as_str(), "INPUT" | "TEXTAREA" | "SELECT") {
            return;
        }
        let bounds = field.get_bounding_client_rect();
        if bounds.top() < 0.0 || bounds.bottom() > current_height {
            // WebViews may reveal only the caret after IME resize, clipping the
            // control's border/label. Keep the complete focused field reachable.
            let options = web_sys::ScrollIntoViewOptions::new();
            options.set_block(web_sys::ScrollLogicalPosition::Center);
            options.set_inline(web_sys::ScrollLogicalPosition::Nearest);
            field.scroll_into_view_with_scroll_into_view_options(&options);
        }
    })
}

fn height(window: &web_sys::Window) -> f64 {
    window
        .inner_height()
        .ok()
        .and_then(|value| value.as_f64())
        .unwrap_or(0.0)
}
