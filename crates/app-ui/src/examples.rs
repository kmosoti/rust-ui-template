//! Small local-only examples sharing the same Leptos and Tailwind pipeline.
use leptos::prelude::*;

#[component]
pub fn Overview() -> impl IntoView {
    view! {
        <section>
            <div class="mb-10 flex flex-wrap items-end justify-between gap-5">
                <div><p class="mb-3 text-xs font-bold uppercase tracking-widest text-emerald-800">"02 / Workspace overview"</p><h1 class="text-4xl font-bold tracking-tight">"A little more clarity."</h1><p class="mt-3 text-slate-600">"A sample workspace for the things you’re building next."</p></div>
                <a href="#/" class="rounded-lg bg-brand px-5 py-3 text-sm font-semibold text-white">"Open interaction lab →"</a>
            </div>
            <div class="mb-8 grid gap-5 sm:grid-cols-3">
                <Metric label="Active projects" value="03" detail="Two ready for review" />
                <Metric label="This week" value="12" detail="Tasks completed · sample data" />
                <Metric label="Next milestone" value="Friday" detail="Browser prototype review" />
            </div>
            <div class="grid gap-6 md:grid-cols-3">
                <section class="rounded-2xl border border-slate-200 bg-white p-7 md:col-span-2">
                    <div class="mb-6 flex items-center justify-between"><h2 class="text-xl font-bold">"On your desk"</h2><span class="text-sm text-slate-500">"Sample projects"</span></div>
                    <Project name="Field notes" description="A calmer home for everyday observations." tag="In progress" />
                    <Project name="Studio website" description="A small space for your best work." tag="In review" />
                    <Project name="Component library" description="Good foundations, one component at a time." tag="Planning" />
                </section>
                <div class="rounded-2xl bg-slate-900 p-7 text-white"><p class="text-xs font-bold uppercase tracking-widest text-emerald-300">"Make room for focus"</p><h2 class="mt-6 text-3xl font-bold leading-tight">"Less noise."<br/>"More making."</h2><p class="mt-5 leading-relaxed text-slate-300">"Start with one useful interaction. Build the rest on a foundation you can test."</p><a class="mt-8 inline-block font-semibold text-emerald-300 underline" href="#/settings">"Make it yours →"</a></div>
            </div>
        </section>
    }
}

#[component]
fn Metric(label: &'static str, value: &'static str, detail: &'static str) -> impl IntoView {
    view! { <div data-layout-region=label class="rounded-2xl border border-slate-200 bg-white p-6"><p class="text-sm font-medium text-slate-600">{label}</p><p class="mt-3 text-4xl font-bold tracking-tight">{value}</p><p class="mt-3 text-sm text-slate-500">{detail}</p></div> }
}

#[component]
fn Project(name: &'static str, description: &'static str, tag: &'static str) -> impl IntoView {
    view! { <div class="flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 py-5"><div><h3 class="font-semibold">{name}</h3><p class="mt-1 text-sm text-slate-600">{description}</p></div><span class="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-slate-700">{tag}</span></div> }
}

#[component]
pub fn Preferences() -> impl IntoView {
    let digest = RwSignal::new(true);
    let compact = RwSignal::new(false);
    let saved = RwSignal::new(false);
    view! {
        <section class="max-w-3xl">
            <p class="mb-3 text-xs font-bold uppercase tracking-widest text-emerald-800">"03 / Preferences"</p><h1 class="text-4xl font-bold tracking-tight">"Your space, your pace."</h1><p class="mt-3 text-slate-600">"A small settings example. Changes live in this page only."</p>
            <form class="mt-8 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm" on:submit=move |ev| { ev.prevent_default(); saved.set(true); }>
                <h2 class="text-xl font-bold">"Make yourself at home"</h2>
                <div class="mt-7"><label for="display-name" class="block text-sm font-semibold">"Display name"</label><input id="display-name" value="Alex Morgan" on:input=move |_| saved.set(false) class="mt-2 w-full rounded-lg border border-slate-400 px-4 py-3" /></div>
                <fieldset class="mt-8 border-t border-slate-100 pt-6"><legend class="px-1 font-semibold">"Workspace options"</legend>
                    <label class="mt-3 flex items-start gap-3"><input type="checkbox" class="mt-1 size-5 accent-brand" prop:checked=move || digest.get() on:change=move |ev| { digest.set(event_target_checked(&ev)); saved.set(false); } /><span><span class="block font-medium">"Weekly digest"</span><span class="text-sm text-slate-600">"Keep a little perspective on your week."</span></span></label>
                    <label class="mt-6 flex items-start gap-3"><input type="checkbox" class="mt-1 size-5 accent-brand" prop:checked=move || compact.get() on:change=move |ev| { compact.set(event_target_checked(&ev)); saved.set(false); } /><span><span class="block font-medium">"Compact view"</span><span class="text-sm text-slate-600">"A little more information in a little less space."</span></span></label>
                </fieldset>
                <div class="mt-8 flex flex-wrap items-center gap-4 border-t border-slate-100 pt-6"><button type="submit" class="rounded-lg bg-brand px-5 py-3 font-semibold text-white">"Apply preferences"</button><p role="status" class="text-sm text-emerald-900">{move || if saved.get() { "Applied for this demo session." } else { "No account or server required." }}</p></div>
            </form>
        </section>
    }
}
