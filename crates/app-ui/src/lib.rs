use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
};

use app_core::LatestRequest;
use futures::future::{AbortHandle, Abortable};
use gloo_timers::future::TimeoutFuture;
use leptos::{prelude::*, task::spawn_local};

mod examples;
mod palettes;

fn current_route() -> String {
    web_sys::window()
        .and_then(|window| window.location().hash().ok())
        .unwrap_or_default()
}

pub type HostInfoReader = fn() -> futures::future::LocalBoxFuture<
    'static,
    Result<app_contract::AppInfo, app_contract::HostError>,
>;

#[derive(Clone, Copy)]
struct HostReader(HostInfoReader);

#[component]
pub fn App(read_host_info: HostInfoReader) -> impl IntoView {
    provide_context(HostReader(read_host_info));
    let appearance = RwSignal::new("nocturne");
    provide_context(palettes::Appearance(appearance));
    let route = RwSignal::new(current_route());
    let main_ref = NodeRef::<leptos::html::Main>::new();
    let listener = gloo_events::EventListener::new(
        &web_sys::window().expect("browser window"),
        "hashchange",
        move |_| route.set(current_route()),
    );
    let _listener = StoredValue::new_local(listener);
    view! {
        <div data-palette=move || appearance.get() class="min-h-screen bg-canvas text-ink">
        <a class="skip-link" data-ui-overflow="allow" data-ui-reason="Visually hidden skip link expands on keyboard focus; tested before activation." href="#workspace-content" on:click=move |ev| {
            ev.prevent_default();
            if let Some(main) = main_ref.get() { let _ = main.focus(); }
        }>"Skip to content"</a>
        <div class="app-shell">
            <aside data-layout-region="workspace-rail" class="workspace-rail" aria-label="Workspace">
                <a href="#/overview" class="workspace-brand"><span aria-hidden="true" class="brand-mark">"◈"</span>"NOCTURNE"</a>
                <p class="workspace-caption">"Your personal workspace"</p>
                <nav aria-label="Main navigation" class="workspace-nav">
                    <NavLink route href="#/overview" label="Library" glyph="▦" />
                    <NavLink route href="#/" label="Latest response" glyph="→" />
                    <NavLink route href="#/settings" label="Preferences" glyph="≡" />
                    <NavLink route href="#/about" label="About" glyph="◇" />
                </nav>
                <div class="rail-index"><p class="eyebrow">"In this workspace"</p><a class="index-link" href="#/">"01 / Response lab"</a><a class="index-link" href="#/settings">"02 / Preferences"</a><a class="index-link" href="#/about">"03 / Application info"</a></div>
                <p class="rail-note"><span class="block text-ink">"A place to make things."</span>"Local examples. No account needed."</p>
            </aside>
            <div data-layout-region="workspace-body" class="workspace-body">
                <header data-layout-region="header" class="context-bar"><span>"Personal workspace"<span aria-hidden="true" class="mx-3">"/"</span>"Examples"</span><span class="font-mono text-success">"CSR · LOCAL DEMO"</span></header>
                <main node_ref=main_ref id="workspace-content" tabindex="-1" data-layout-region="main" class="workspace-main">
                    {move || match route.get().as_str() {
                        "#/about" => view! { <About /> }.into_any(),
                        "#/settings" => view! { <examples::Preferences /> }.into_any(),
                        "#/" => view! { <LatestResponse /> }.into_any(),
                        _ => view! { <examples::Overview /> }.into_any(),
                    }}
                </main>
                <footer data-layout-region="footer" class="workspace-footer"><span>"NOCTURNE / Rust UI Template"</span><span>"Leptos · Tailwind · Rust"</span></footer>
            </div>
        </div>
        </div>
    }
}

#[component]
fn NavLink(
    route: RwSignal<String>,
    href: &'static str,
    label: &'static str,
    glyph: &'static str,
) -> impl IntoView {
    view! { <a class="nav-link" href=href aria-label=label aria-current=move || {
        let current = route.get();
        let selected = current == href || (href == "#/overview" && !matches!(current.as_str(), "#/" | "#/settings" | "#/about"));
        selected.then_some("page")
    }><span aria-hidden="true" class="w-4 text-center text-base text-brand">{glyph}</span>{label}</a> }
}

#[component]
fn About() -> impl IntoView {
    let reader = expect_context::<HostReader>().0;
    let info = LocalResource::new(reader);
    view! {
        <section class="max-w-3xl"><p class="eyebrow mb-3">"Workspace / System"</p><h1 class="page-heading">"About"</h1><p class="page-summary">"Requests are simulated in your browser or native WebView."</p>
        <h2 class="mt-8 border-t border-hairline pt-6 text-xl font-semibold">"Application information"</h2>
        <Suspense fallback=move || view! { <p role="status">"Reading application information…"</p> }>
        <p class="mt-3 text-muted" role="status" data-testid="host-info">{move || info.get().map(|result| match result {
            Ok(info) => format!("{} {} · {}", info.name, info.version, info.platform),
            Err(app_contract::HostError::Unsupported) => "Application information is unavailable in browser mode.".to_string(),
            Err(_) => "Application information could not be read.".to_string(),
        })}</p>
        </Suspense></section>
    }
}

#[component]
fn LatestResponse() -> impl IntoView {
    let tracker = RwSignal::new(LatestRequest::<i64>::new());
    let input = RwSignal::new(String::from("1"));
    let message = RwSignal::new(String::new());
    let message_tone = RwSignal::new("info");
    let tasks: Arc<Mutex<HashMap<u64, AbortHandle>>> = Arc::new(Mutex::new(HashMap::new()));
    let cleanup = Arc::clone(&tasks);
    on_cleanup(move || {
        for (_, task) in cleanup.lock().expect("task lock").drain() {
            task.abort();
        }
    });
    let start = {
        let tasks = Arc::clone(&tasks);
        move |delay: u32| {
            let Ok(value) = input.get_untracked().parse::<i64>() else {
                message.set("Enter a whole number.".into());
                message_tone.set("danger");
                return;
            };
            let id = match tracker.try_update(|state| state.begin()) {
                Some(Ok(id)) => id,
                Some(Err(_)) => {
                    message.set("Request IDs exhausted.".into());
                    message_tone.set("danger");
                    return;
                }
                None => return,
            };
            message.set(String::new());
            let (handle, registration) = AbortHandle::new_pair();
            tasks.lock().expect("task lock").insert(id.get(), handle);
            let tasks = Arc::clone(&tasks);
            spawn_local(async move {
                let outcome = Abortable::new(TimeoutFuture::new(delay), registration).await;
                tasks.lock().expect("task lock").remove(&id.get());
                if outcome.is_ok() {
                    let _ = tracker.try_update(|state| state.complete(id, value));
                }
            });
        }
    };
    let slow = start.clone();
    let cancel_tasks = Arc::clone(&tasks);
    view! {
        <section class="max-w-3xl">
            <p class="eyebrow mb-3">"Workspace / Interaction lab"</p>
            <h1 class="page-heading">"Latest response"</h1>
            <p class="page-summary">"Start a slow request, then a fast one to see the latest result win."</p>
            <form class="mt-8 space-y-6 border-t border-hairline py-8" on:submit=move |ev| ev.prevent_default()>
                <div><label class="block font-semibold" for="number">"Number"</label>
                <input class="field sm:max-w-80" id="number" type="number" step="1" prop:value=move || input.get() on:input=move |ev| input.set(event_target_value(&ev)) /></div>
                <div class="flex flex-wrap gap-3">
                    <button class="primary-action" type="button" on:click=move |_| slow(1500)>"Slow request"</button>
                    <button class="primary-action" type="button" on:click=move |_| start(150)>"Fast request"</button>
                    <button class="secondary-action" type="button" on:click=move |_| {
                        tracker.update(|state| state.cancel());
                        for (_, task) in cancel_tasks.lock().expect("task lock").drain() { task.abort(); }
                        message.set("Request cancelled.".into());
                        message_tone.set("warning");
                    }>"Cancel"</button>
                </div>
            </form>
            <p class="feedback border-t border-hairline py-6 font-medium leading-relaxed" data-tone=move || {
                let state = tracker.get();
                if !message.get().is_empty() { message_tone.get() }
                else if state.active().is_some() { "info" }
                else if state.value().is_some() { "success" }
                else { "neutral" }
            } role="status" aria-live="polite">{move || {
                let state = tracker.get();
                let result = state.value().map_or_else(|| "No result yet.".to_string(), |value| format!("Latest result: {value}"));
                let pending = if state.active().is_some() { " Request pending." } else { "" };
                format!("{result}{pending} {}", message.get())
            }}</p>
        </section>
    }
}
