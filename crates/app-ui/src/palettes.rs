//! App-session palette choice; the CSS owns semantic color values.
use leptos::prelude::*;

#[derive(Clone, Copy)]
pub(crate) struct Appearance(pub RwSignal<&'static str>);

pub(crate) struct Palette {
    pub id: &'static str,
    pub name: &'static str,
    pub description: &'static str,
}

pub(crate) const PALETTES: [Palette; 7] = [
    Palette {
        id: "nocturne",
        name: "Nocturne (default)",
        description: "Lavender and charcoal · the original workspace.",
    },
    Palette {
        id: "signal-blue",
        name: "Signal Blue & Porcelain",
        description: "#0057FF + #F8F7F4 · blue on a warm light canvas.",
    },
    Palette {
        id: "butter-iris",
        name: "Butter Yellow & Royal Iris",
        description: "#FFF275 + #3A0CA3 · yellow on deep iris.",
    },
    Palette {
        id: "lime-graphite",
        name: "Lime Spark & Graphite",
        description: "#B6FF2E + #23262F · electric lime on graphite.",
    },
    Palette {
        id: "sulu-fir",
        name: "Sulu & Deep Fir",
        description: "#9FE870 + #163300 · fresh green on deep fir.",
    },
    Palette {
        id: "blooming-romance",
        name: "Blooming Romance",
        description: "Burgundy, soft pink and muted purple · project-selected shades.",
    },
    Palette {
        id: "desert-dusk",
        name: "Desert Dusk",
        description: "Cognac, muted orange and purple · project-selected shades.",
    },
];

#[component]
pub(crate) fn AppearanceSettings() -> impl IntoView {
    let appearance = expect_context::<Appearance>().0;
    view! {
        <section class="mt-8 border-t border-hairline py-8" aria-labelledby="appearance-title">
            <h2 id="appearance-title" class="text-xl font-semibold">"Appearance"</h2>
            <div class="mt-6 max-w-lg"><label class="block text-sm font-medium" for="color-scheme">"Color scheme"</label>
            <select id="color-scheme" class="field" aria-describedby="palette-scope palette-description" prop:value=move || appearance.get() on:change=move |ev| {
                let value = event_target_value(&ev);
                if let Some(palette) = PALETTES.iter().find(|palette| palette.id == value) { appearance.set(palette.id); }
            }>{PALETTES.iter().map(|palette| view! { <option value=palette.id>{palette.name}</option> }).collect_view()}</select></div>
            <p id="palette-scope" class="mt-3 text-sm text-muted">"Applies across this session. Reloading restores Nocturne."</p>
            <p id="palette-description" class="mt-2 text-sm text-muted">{move || PALETTES.iter().find(|palette| palette.id == appearance.get()).map(|palette| palette.description)}</p>
            <ul class="mt-5 flex flex-wrap gap-x-6 gap-y-3 text-sm" aria-label="Feedback color examples">
                <li class="feedback" data-tone="info">"Info: preview"</li><li class="feedback" data-tone="success">"Success: ready"</li><li class="feedback" data-tone="warning">"Warning: check"</li><li class="feedback" data-tone="danger">"Error: attention"</li>
            </ul>
        </section>
    }
}
