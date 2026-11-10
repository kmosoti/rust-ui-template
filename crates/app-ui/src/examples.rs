//! Local-only examples using the template's default workspace/launcher design.
use leptos::prelude::*;

#[component]
pub fn Overview() -> impl IntoView {
    view! {
        <section>
            <div class="flex flex-wrap items-end justify-between gap-4"><div><p class="eyebrow mb-3">"Workspace / Library"</p><h1 class="page-heading">"Your library"</h1><p class="page-summary">"A little space for your next big idea."</p></div><span class="font-mono text-xs text-muted">"03 EXAMPLES"</span></div>
            <section aria-labelledby="featured-title" class="feature-grid">
                <img data-testid="featured-art" src="public/observatory.svg" alt="A small observatory above a winding trail in a violet mountain landscape." class="feature-art" width="1200" height="900" />
                <div class="feature-detail"><p class="eyebrow text-brand">"Featured / Interaction lab"</p><h2 id="featured-title" class="feature-title">"Signal & silence"</h2><p class="mt-4 leading-relaxed text-muted">"Keep the latest signal. Leave the noise behind. Explore requests, timing, and cancellation in one small working example."</p><a data-testid="launch-example" class="primary-action mt-7" href="#/">"Open response lab"<span aria-hidden="true">"→"</span></a><div class="mt-8 flex flex-wrap gap-x-5 gap-y-2 border-t border-hairline pt-5 text-xs text-muted"><span class="text-ready">"Ready to explore"</span><span>"Local simulation"</span></div></div>
            </section>
            <div class="mt-10 grid gap-10 xl:grid-cols-[2fr_1fr]">
                <section data-layout-region="library" aria-labelledby="library-title"><div class="mb-5 flex flex-wrap items-center justify-between gap-3"><h2 id="library-title" class="text-lg font-semibold">"Workspace examples"</h2><span class="text-xs text-muted">"Sample library"</span></div>
                    <LibraryRow number="01" title="Response lab" description="Slow, fast, cancel. The latest result wins." href="#/" />
                    <LibraryRow number="02" title="Preferences" description="Make a few adjustments. Keep things local." href="#/settings" />
                    <LibraryRow number="03" title="Application info" description="A clear view of the browser or native host." href="#/about" />
                </section>
                <section data-layout-region="workspace-notes" aria-labelledby="notes-title" class="border-t border-hairline pt-5"><p class="eyebrow">"From the workspace"</p><h2 id="notes-title" class="mt-4 text-xl font-semibold">"Built for the in-between."</h2><p class="mt-3 text-sm leading-relaxed text-muted">"Part notebook, part launchpad. A shared Rust UI with room for your own tools, worlds, and ideas."</p><a class="mt-5 inline-block py-2 text-sm font-medium text-brand underline underline-offset-4" href="#/about">"Explore the foundation →"</a><p class="mt-5 border-t border-hairline pt-5 font-mono text-xs text-muted">"SAMPLE CONTENT / ORIGINAL ARTWORK"</p></section>
            </div>
        </section>
    }
}

#[component]
fn LibraryRow(
    number: &'static str,
    title: &'static str,
    description: &'static str,
    href: &'static str,
) -> impl IntoView {
    view! { <a href=href class="library-row"><span class="demo-number">{number}</span><span class="min-w-0"><span class="block font-medium">{title}</span><span class="mt-1 block text-sm leading-relaxed text-muted">{description}</span></span><span aria-hidden="true" class="text-muted">"→"</span></a> }
}

#[component]
pub fn Preferences() -> impl IntoView {
    let digest = RwSignal::new(true);
    let compact = RwSignal::new(false);
    let saved = RwSignal::new(false);
    view! {
        <section class="max-w-3xl">
            <p class="eyebrow mb-3">"Workspace / Personalize"</p><h1 class="page-heading">"Preferences"</h1><p class="page-summary">"A workspace that feels like yours. Changes live in this page only."</p>
            <form class="mt-8 border-t border-hairline py-8" on:submit=move |ev| { ev.prevent_default(); saved.set(true); }>
                <h2 class="text-xl font-semibold">"Your profile"</h2>
                <div class="mt-7 max-w-lg"><label for="display-name" class="block text-sm font-medium">"Display name"</label><input id="display-name" value="Alex Morgan" on:input=move |_| saved.set(false) class="field" /></div>
                <fieldset class="mt-8 border-t border-hairline pt-6"><legend class="pr-4 font-medium">"Workspace options"</legend>
                    <label class="mt-3 flex items-start gap-3"><input type="checkbox" class="mt-1 size-5 shrink-0 accent-brand" prop:checked=move || digest.get() on:change=move |ev| { digest.set(event_target_checked(&ev)); saved.set(false); } /><span><span class="block font-medium">"Weekly digest"</span><span class="text-sm text-muted">"Keep a little perspective on your week."</span></span></label>
                    <label class="mt-6 flex items-start gap-3"><input type="checkbox" class="mt-1 size-5 shrink-0 accent-brand" prop:checked=move || compact.get() on:change=move |ev| { compact.set(event_target_checked(&ev)); saved.set(false); } /><span><span class="block font-medium">"Compact view"</span><span class="text-sm text-muted">"A little more information in a little less space."</span></span></label>
                </fieldset>
                <div class="mt-8 flex flex-wrap items-center gap-4 border-t border-hairline pt-6"><button type="submit" class="primary-action">"Apply preferences"</button><p role="status" class="text-sm text-ready">{move || if saved.get() { "Applied for this demo session." } else { "No account or server required." }}</p></div>
            </form>
        </section>
    }
}
