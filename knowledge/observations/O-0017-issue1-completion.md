---
id: O-0017
type: observation
status: validated-develop-source
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Scoped Issue #1 completion evidence

## Reviewed delivery

The user-approved scope is [D-0011](../decisions/D-0011-scoped-csr-milestone.md).
Independent fresh gpt-6.1-terra review used medium reasoning, never max/ultra.
Reviewer-owned rebase landing into develop completed for:

- PR #21: merged native/Android documentation reconciliation.
- PR #26: permissive native dependency paths; four initial parent patches.
- PR #25: presented Android capture validation, including the real early callback
  deadline failure/fix and inspected complete library/landscape/IME captures.
- PR #29: dependency/advisory gates, updated Gradle locks/strict metadata,
  verified repeated setup, conditional clean frontend gate, and the fifth rcdom
  patch after a failing actual-source template-preservation regression.

The final implementation is develop
`323167e3b536ecaeb3f3ba8574f7fa3e21e0db73`. Every exact-head PR #29 check passed,
with independent inspection of final Android, clean-build and security artifacts.
All six post-merge workflows passed on this develop source:

| Check | GitHub run |
| --- | --- |
| Core | 42982373217 |
| CSR browser | 42982373255 |
| Linux native DEB/RPM | 42982373186 |
| Android APK/emulator | 42982373209 |
| Dependency security | 42982373154, attempts1 and2 |
| Independent clean frontend | 42982373211 |

These correspond to actions/runs/RUN in kmosoti/rust-ui-template. Final docs PR #30
changes only README/docs/knowledge and has its own applicable core/browser checks;
its review/landing and issue closure must not be inferred before those complete.
Main remains `e959615423c7deaa0608fc3a51769b71239bc2b1`, confirmed with
`git ls-remote origin refs/heads/main`; no release, tag or publication occurred.

## Executed verification and artifacts

- Actual-source local tests:12 Tauri HTML/CSP tests,8 Wry injection tests,9 directory
  tests. The new template test failed before the serializer correction and passed
  after it. Independent reviewer verified all five original archive checksums,
  original file hashes and patch-applied byte-for-byte source reproduction.
- 26 Python tests passed, including download recovery/idempotency, expired-exception
  rejection and coverage of real frontend inputs against both conditional filters.
- Both complete cargo-deny checks passed; an actual MPL-only fixture is rejected.
  OSV scans all four actual Gradle locks and reports zero vulnerabilities across
  388 versions, four explicitly UNKNOWN licenses. Two Rust macro maintenance
  exceptions expire2027-02-09; no MPL/vulnerability waiver was introduced.
- Gradle generated actual locks and verification checksums. Local strict
  instrumentation compile passed; final CI additionally built both actual ABIs,
  packaged APKs and exercised production/denial runtime scenarios.
- Exact-head PR #29 Android run42981139718 artifact13838360538 was independently
  inspected: complete library/landscape and focused input/IME. Backend fallback
  injection is covered by compiling its actual source in the host harness;
  modern WebView runtime success does not establish every older fallback runtime.
- Exact-head clean run42981140733 artifact13836974842 reports tested synthetic
  merge ec47860150d07c0d01db9a032a1a861afcdff176,6 identical production files,
  all commands passed. Empty-target production builds72.69s/69.94s; fresh workspace
  tests81.39s, subpath1.44s, real browser90.01s. No compiled cache was restored.
  Registry source downloads were reused. This is frontend byte reproducibility,
  not signed/native-package determinism.
- Security run42981139978 artifact13836569560 was independently inspected;
  tool archive cold/repeated setup1.054s/0.207s. Source/commands/results and failures
  are expanded in O-0013–O-0016; source-linked extraction is not a Lean proof.

## Same-source cache experiment

Executed `gh api repos/kmosoti/rust-ui-template/actions/runs/42982373154/attempts/1/jobs`
and fed the JSON to `python3 scripts/ci_timings.py`; inspected restore/save logs.
Then `gh run rerun 42982373154` and inspected attempt2 jobs/logs and artifact
13837807842. Both used source 323167e3 and Ubuntu24.04 image 20261101.360.1.

| Dependency-security observation | Seed attempt1 | Warm attempt2 |
| --- | ---: | ---: |
| Whole job | 31s | 24s |
| Restore | 0s, miss | 4s, exact hit |
| Verified tool setup step | 2s | 1s |
| Cache save | 4s | skipped |

The warm archive was 156MiB (163382659 bytes). Actual warm setup calls took 0.141s
and 0.366s; both began with both pinned archives present and still verified bytes.
All policy/license/advisory checks executed on both runs. Only the successful
trusted develop push seeded the cache; PRs did not save it. One paired sample is
not a general speedup guarantee. The security cache avoids unused compiled targets.

Android exact-head run42981139718 took445s: restore61s, verified CLI/tool setup2s,
SDK/NDK/emulator verification11s, dual-ABI build147s, production/denial VM checks159s.
Transfer is now more costly than repeated installer work; measured cache-splitting
investigation is #31. Do not infer gains by omitting functional checks.

## Remaining limits and ownership

#22 deferred desktop/Apple platforms; #23 broader Linux/Android/minimum runtime
and manual accessibility coverage; #24 signing/distribution/native determinism
and default-branch weekly security schedule activation; #27 actual Aeneas/Lean
proof; #28 dated macro maintenance replacements; #31 Android cache transfer.
SSR/hydration stays #2. Physical ARM64/API29/TalkBack, Wayland/hardware GPU and
Windows/macOS/iOS runtime claims remain unestablished. A documented intermittent
Linux WebDriver transport reset has no asserted GPU cause or blanket retry.

## Revisit when

Any source, dependency, toolchain, platform, cache boundary or release scope changes.
Keep support claims tied to actual artifacts/checks and do not mark this record
human-ratified merely because its PR is merged.
