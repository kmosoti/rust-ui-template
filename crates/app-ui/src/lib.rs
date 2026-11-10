use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
};

use app_core::LatestRequest;
use futures::future::{AbortHandle, Abortable};
use gloo_timers::future::TimeoutFuture;
use leptos::{prelude::*, task::spawn_local};

mod examples;

fn current_route() -> String {
    web_sys::window()
        .and_then(|window| window.location().hash().ok())
        .unwrap_or_default()
}

#[component]
pub fn App() -> impl IntoView {
    let route = RwSignal::new(current_route());
    let listener = gloo_events::EventListener::new(
        &web_sys::window().expect("browser window"),
        "hashchange",
        move |_| route.set(current_route()),
    );
    let _listener = StoredValue::new_local(listener);
    view! {
        <div class="min-h-screen bg-stone-50 text-slate-900">
            <header class="border-b border-slate-200 bg-white">
                <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
                    <a href="#/overview" class="text-xl font-bold tracking-tight">"Form & Function"<span class="ml-3 rounded bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-900">"UI EXAMPLES"</span></a>
                    <nav aria-label="Main navigation" class="flex flex-wrap gap-5 text-sm font-semibold">
                        <a class="text-brand underline underline-offset-4" href="#/overview">"Overview"</a>
                        <a class="text-brand underline underline-offset-4" href="#/">"Latest response"</a>
                        <a class="text-brand underline underline-offset-4" href="#/settings">"Preferences"</a>
                        <a class="text-brand underline underline-offset-4" href="#/about">"About"</a>
                    </nav>
                </div>
            </header>
            <main class="mx-auto max-w-6xl px-6 py-12">
                {move || match route.get().as_str() {
                    "#/about" => view! { <About /> }.into_any(),
                    "#/overview" => view! { <examples::Overview /> }.into_any(),
                    "#/settings" => view! { <examples::Preferences /> }.into_any(),
                    _ => view! { <LatestResponse /> }.into_any(),
                }}
            </main>
            <footer class="mx-auto max-w-6xl border-t border-slate-200 px-6 py-6 text-sm text-slate-600">"Built with Leptos · Styled with Tailwind · Tested from Rust"</footer>
        </div>
    }
}

#[component]
fn About() -> impl IntoView {
    view! { <section><h1 class="text-3xl font-bold">"About"</h1><p class="mt-4">"Requests are simulated in your browser."</p></section> }
}

#[component]
fn LatestResponse() -> impl IntoView {
    let tracker = RwSignal::new(LatestRequest::<i64>::new());
    let input = RwSignal::new(String::from("1"));
    let message = RwSignal::new(String::new());
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
                return;
            };
            let id = match tracker.try_update(|state| state.begin()) {
                Some(Ok(id)) => id,
                Some(Err(_)) => {
                    message.set("Request IDs exhausted.".into());
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
            <p class="mb-3 text-xs font-bold uppercase tracking-widest text-emerald-800">"01 / Interaction lab"</p>
            <h1 class="text-4xl font-bold tracking-tight">"Latest response"</h1>
            <p class="mt-3">"Start a slow request, then a fast one to see the latest result win."</p>
            <form class="mt-8 space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm" on:submit=move |ev| ev.prevent_default()>
                <div><label class="block font-semibold" for="number">"Number"</label>
                <input class="mt-1 rounded border border-slate-500 px-3 py-2" id="number" type="number" step="1" prop:value=move || input.get() on:input=move |ev| input.set(event_target_value(&ev)) /></div>
                <div class="flex flex-wrap gap-3">
                    <button class="rounded bg-brand px-4 py-2 font-semibold text-white" type="button" on:click=move |_| slow(1500)>"Slow request"</button>
                    <button class="rounded bg-brand px-4 py-2 font-semibold text-white" type="button" on:click=move |_| start(150)>"Fast request"</button>
                    <button class="rounded border border-slate-600 px-4 py-2 font-semibold" type="button" on:click=move |_| {
                        tracker.update(|state| state.cancel());
                        for (_, task) in cancel_tasks.lock().expect("task lock").drain() { task.abort(); }
                        message.set("Request cancelled.".into());
                    }>"Cancel"</button>
                </div>
            </form>
            <p class="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-6 font-medium text-emerald-950" role="status" aria-live="polite">{move || {
                let state = tracker.get();
                let result = state.value().map_or_else(|| "No result yet.".to_string(), |value| format!("Latest result: {value}"));
                let pending = if state.active().is_some() { " Request pending." } else { "" };
                format!("{result}{pending} {}", message.get())
            }}</p>
        </section>
    }
}
