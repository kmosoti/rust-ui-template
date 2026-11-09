use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
};

use app_core::LatestRequest;
use futures::future::{AbortHandle, Abortable};
use gloo_timers::future::TimeoutFuture;
use leptos::{prelude::*, task::spawn_local};

fn current_route() -> bool {
    web_sys::window()
        .and_then(|window| window.location().hash().ok())
        .is_some_and(|hash| hash == "#/about")
}

#[component]
pub fn App() -> impl IntoView {
    let about = RwSignal::new(current_route());
    let listener = gloo_events::EventListener::new(
        &web_sys::window().expect("browser window"),
        "hashchange",
        move |_| about.set(current_route()),
    );
    let _listener = StoredValue::new_local(listener);
    view! {
        <main class="mx-auto max-w-2xl p-6 text-slate-900">
            <nav aria-label="Main navigation" class="mb-8 flex gap-4">
                <a class="text-brand underline" href="#/">"Latest response"</a>
                <a class="text-brand underline" href="#/about">"About"</a>
            </nav>
            {move || if about.get() { view! { <About /> }.into_any() } else { view! { <LatestResponse /> }.into_any() }}
        </main>
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
        <section>
            <h1 class="text-3xl font-bold">"Latest response"</h1>
            <p class="mt-3">"Start a slow request, then a fast one to see the latest result win."</p>
            <form class="mt-6 space-y-4" on:submit=move |ev| ev.prevent_default()>
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
            <p class="mt-5" role="status" aria-live="polite">{move || {
                let state = tracker.get();
                let result = state.value().map_or_else(|| "No result yet.".to_string(), |value| format!("Latest result: {value}"));
                let pending = if state.active().is_some() { " Request pending." } else { "" };
                format!("{result}{pending} {}", message.get())
            }}</p>
        </section>
    }
}
