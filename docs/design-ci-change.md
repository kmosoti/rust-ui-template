# Design workflow and CI changes for human review

Overall architecture: [architecture.md](architecture.md). Research:
[R-0002](../knowledge/research/R-0002-ui-diversity-and-verification.md).

## Design workflow change

```mermaid
flowchart LR
  Old["Broad prompt"] --> One["Layout, copy and code invented together"] --> Guess["Code-only assessment"]
  Brief["Task brief + 3 structural alternatives"] --> Geometry["ASCII/grid specification"]
  Geometry --> Code["Leptos implementation + selected tokens"]
  Code --> Render["Production desktop/mobile render"]
  Render --> Evidence["Screenshots + DOM metrics + axe + keyboard checks"]
  Evidence --> Critique["Concrete critique; bounded corrections"]
  Critique -->|fix an observed defect| Code
  Critique --> Review["Independent standard/medium review and human-readable evidence"]
```

The local skill guides new work; it does not claim the existing sample dashboard
is a unique design or force all products to adopt an industrial theme. Namespace
restrictions are an optional profile with an actual CSS-output check.

## CI setup change

```mermaid
flowchart TD
  Before["Each fresh job"] --> Compile["Compile pinned Trunk from source again"]
  Compile --> Cold["Compile workspace/native dependencies again"]
  After["Fresh job"] --> Restore["Restore isolated trusted base cache if available"]
  Restore --> Verify["Hash-check official Trunk/Tailwind/Tauri assets"]
  Verify --> Cargo["Locked Cargo build; reuse compatible dependencies"]
  Cargo --> Assets["Fresh production assets and native package-owned rebuild"]
  Assets --> Tests["Same security/functional checks + layout checks"]
  Tests --> Push{Successful develop push?}
  Push -->|yes| Save["Save immutable cache by job/image/Rust/locks/SDK"]
  Push -->|PR or failure| NoSave["No trusted cache write"]
```

CI disables incremental/debuginfo-heavy test artifacts to keep caches smaller;
local developer profiles are unchanged. Cache misses remain supported. OS
packages are freshly installed; the baseline measured cost was 27s, compared with
342s spent compiling Trunk. Cold and warm measurements must be reported separately.
This change neither removes native permission/CSP tests nor merges into main.
