---
id: R-0002
type: research
status: reviewed-primary-sources
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# R-0002: UI sameness, visual reasoning and enforceable design workflows

## Finding

The proposed diagnosis identifies useful engineering controls, but blends
observations, plausible explanations and unsupported universal/quantitative
claims. Adopt the controls as a task-driven workflow, not a theory that every
model is incapable of visual reasoning or that one industrial theme guarantees
originality. This review does not measure the prevalence of “AI UI slop.”

Research used primary papers, authors' benchmark material, standards and official
tooling docs. The connected deep-research service required authentication; no
account was connected. Public search and primary-source inspection were used.
No Superdesign service or account is used. Sources checked 2026-11-10; benchmark
results apply to the studied models/tasks, not automatically to 2026 systems.

## Claim-by-claim assessment

| Claim | Assessment | Practical implication |
| --- | --- | --- |
| All generated UIs look the same | Too broad; a recognizable recurring template is an observation, not a measured universal result | Compare concrete outputs, content and task outcomes |
| Models cannot reason about geometry | False as an absolute; precise spatial reasoning remains unreliable | Combine visual inspection with browser measurements |
| Training is dominated by 2022–2026 Tailwind/shadcn/Vercel repos | Unverified corpus composition and date range | Do not present a guessed training mixture as fact |
| RLHF causes convergence | Some empirical support for reduced diversity; not an explanation of every UI aesthetic | Use explicit alternatives and evaluate outcomes |
| Utility n-grams make the next classes nearly certain | Plausible familiarity/conditioning effect; probability assertion unmeasured | Inspect actual classes; do not infer hidden attention dynamics |
| Resetting theme namespaces cuts the look by 70% | No evidence for that percentage | Test emitted CSS; evaluate design separately |
| Role separation helps | Sensible workflow inference, not a proven universal performance gain | Write a brief and geometry spec before component implementation |
| Screenshot revision fixes design | Useful feedback channel; improvement is model/task dependent | Bound correction passes and verify the actual change |

### Distribution and decoding

Kirk et al., *Understanding the Effects of RLHF on LLM Generalisation and
Diversity* ([paper](https://arxiv.org/abs/2310.06452), ICLR 2024), measured diversity
reductions under RLHF on summarization and instruction-following experiments
with two base models. This supports a risk of output concentration in those
settings; it does not establish a Tailwind-specific aesthetic mechanism or a
universal result for all model families.

Ouyang et al., *Training language models to follow instructions with human
feedback* ([paper](https://arxiv.org/abs/2203.02155), 2022), describes supervised
examples, preference rankings and reinforcement learning. Preference training
is not simply a rule to reject every low-frequency token. Autoregressive output
can also be sampled rather than always taking an argmax; a most-likely mode is
not mathematically the same thing as an arithmetic mean. “Regression to the
mean” is therefore a metaphor here, not an established causal derivation.

The [GPT-4 Technical Report](https://cdn.openai.com/papers/gpt-4.pdf) withholds
fine-grained training construction details. It cannot substantiate a specific
2022–2026 repository mixture, and it is not evidence about every current model's
training. Auditing that hypothesis would require disclosed datasets or a
controlled behavioral study, rather than counting popular templates online.

Doshi and Hauser's randomized short-story study, *Generative AI enhances
individual creativity but reduces the collective diversity of novel content*
([original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11244532/), 2024),
found both improved individual evaluations and greater similarity among
AI-assisted stories. It concerns nonprofessional writing participants, not
frontend engineering. It is relevant analogical evidence for anchoring, not
proof that a CSS framework causes visual convergence.

*The Price of Format: Diversity Collapse in LLMs*
([ACL paper](https://aclanthology.org/2025.findings-emnlp.836/), 2025) studies
format/template effects on open-ended generation. Its results caution that
higher sampling temperature alone need not recover diversity. Structural prompt
tokens are not Tailwind utilities, however, and the work does not measure the
specific conditional class probabilities asserted in the proposal.

### Visual reasoning and feedback

*Design2Code* ([paper](https://arxiv.org/html/2403.03163v3), NAACL 2025;
[authors' benchmark](https://github.com/NoviScl/Design2Code)) evaluates reproduction
of 484 real webpages using screenshots, code, metrics and human judgments.
The studied systems can reproduce visual structure but struggle with missing
elements and layout. Self-revision helps some model/settings and offers little
or inconsistent benefit in others; it is not a guaranteed improvement loop.
These are reference-reproduction results, not scores for originality or proof
that today's best model has the same limitations. Geometry metrics and human
judgment also disagree in some cases, supporting complementary evaluation.

*Vision language models are blind*
([paper](https://arxiv.org/abs/2407.06581), revised 2025) demonstrates failures on
small geometric distinctions, intersections and overlapping primitives. The
results depend on spacing and resolution; the paper's title should not be read
as literal inability to use images. OpenAI's current
[vision documentation](https://developers.openai.com/api/docs/guides/images-vision)
also flags precise spatial localization as a limitation. Rendered pixels are a
necessary feedback input for this workflow, but a vision critique is not an
exact geometry oracle. Browser boxes and computed styles reduce ambiguity.

### Engineering interpretation

The one-pass criticism is a useful account of underspecified work, not a literal
computation model: autoregressive decoding involves repeated predictions, and
an agent can already use planning, code inspection and rendering tools. Output
text format does not establish that internal representations lack spatial
information. The stronger actionable claim is that unmeasured output leaves
important geometric and task-hierarchy decisions unverified.

Utility names may be split by a tokenizer. A familiar class combination is not
evidence that attention acts as a fixed n-gram lookup or that its next class has
probability near one. Such a probability needs an identified model, context and
decoding settings. Neither the training-date claim nor the claimed percentage
improvement is substantiated by the sources reviewed here.

Our existing overview visibly uses repeated metric cards. That is a concrete
example to critique, not evidence of a particular model's training data. A useful
metric group may be symmetric; distinctive design should follow the task rather
than prohibit every normal layout. The skill makes current demos optional
examples and requires alternatives before using their structure for new work.

## Tailwind and accessibility corrections

The official [theme documentation](https://tailwindcss.com/docs/theme) supports
resetting namespaces with `--color-*: initial` and custom variables; the
[color documentation](https://tailwindcss.com/docs/colors) describes disabling
palette families. Resetting a namespace removes the corresponding generated
utilities. Unknown classes can remain in HTML without any compilation error.
Arbitrary values and other CSS can also bypass a token convention. Use an emitted
CSS check and review, not an assumed compiler guarantee. This repository's
optional profile has an executable positive/negative output check.

A color's OKLCH lightness is not itself its WCAG contrast ratio. Check actual
foreground/background combinations, opacity and states. Very faint hairlines
can be decorative, but a necessary control boundary or state indicator may need
stronger contrast. The profile distinguishes a decorative hairline from a
control-line token; it still requires rendered testing.

[WCAG 2.2](https://www.w3.org/TR/WCAG22/) defines contrast and reflow requirements;
[the reflow explanation](https://w3c.github.io/wcag/understanding/reflow.html)
clarifies the 320 CSS-pixel scenario and exceptions for genuinely two-dimensional
content. Fixed full-height layouts and blanket overflow-hidden can make content
unreachable under zoom/mobile keyboards. Explicit region scrolling can work,
but requires a tested reading/focus order. Semantic headings, target spacing,
keyboard focus and accessible state changes matter alongside visual identity.
An axe smoke scan is valuable but not a complete conformance audit.

## Repository implementation decisions

1. A local `.agents/skills/distinct-ui/SKILL.md` separates brief, three structural
   alternatives, spatial spec, implementation and bounded rendered critique.
   Different directions must vary hierarchy/density/geometry, not just accents.
2. Default anti-patterns are review constraints with functional exceptions:
   repeated decorative cards, tinted circles and marketing heroes are not a
   substitute for app hierarchy. A border on a real input/table is legitimate.
3. A semantic restricted theme is an opt-in starting profile. Existing demos
   remain examples, not required visual patterns; forcing all work into the
   same dark industrial system would create a new uniform default.
4. Chromiumoxide captures desktop/390px/320px production output and DOM metrics;
   page overflow, clipped text and annotated region collisions can fail checks.
   DOM depth, nested borders, typography and optical balance remain diagnostic.
   No novelty percentage or visual-quality guarantee is claimed.
5. Geometry is recorded before view! implementation. This can happen as separate
   artifacts/passes within the same authorized work session; no automatic user
   approval gate or paid design service is introduced.
6. `tailwind_fuse` is not installed; it is not a prerequisite for this workflow.
   Complete static classes and existing components suffice for this slice.

### Proposed future evaluation (not executed)

For a defensible diversity claim, run paired tasks holding content/functionality
constant. Record model/version, prompt, available references and sampling settings.
Compare unconstrained baseline, token-only restrictions, and brief+geometry+render
feedback; include multiple outputs per task. Blind the condition labels for
human assessment. Score task completion, hierarchy, readability, accessibility
and useful visual variation separately. Record defects and reviewer agreement;
do not equate edit distance or random asymmetry with better design. The current
implementation is an engineering intervention, not that controlled experiment.

## CI evidence and acceleration rationale

Official [GitHub caching documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
and [actions/cache](https://github.com/actions/cache) describe cache lookup,
branch scope, immutable keys and restore/save actions. This project separates
job/platform/toolchain/lock/SDK cache identities; only successful develop pushes
save. PRs restore permitted base caches but do not publish trusted executable
caches. No pull_request_target execution or signing secrets are added. Cached
tool archives are checked against committed hashes and extracted afresh.

Actual prior native job 130154305222 (run 42908982231) took 14m20s. Its steps
included Trunk source installation 342s, native production build 191s, native
Clippy 81s, frontend build 85s, OS dependencies 27s and Rust installation 11s.
These timings identify the useful target: eliminate repeated Trunk compilation
and reuse compiled dependencies. They do not promise a particular warm speedup.
OS packages still install on fresh hosted runners; caching /usr or the package
database would be unsafe and is not done. Cold/warm observations for the new
workflow belong in O-0006, with cache hit/miss and image/SDK context explicit.

## Revisit when

New benchmark results, a disclosed corpus, or a controlled project experiment
changes the evidence; the design task demands different constraints; cache size,
restore cost or ABI updates erase the performance benefit. Review model effort
is a user cost constraint: standard/medium only, never max/ultra.

## Relations

- **informs**: [D-0006](../decisions/D-0006-design-workflow-and-ci.md)
- **observed-in**: [O-0006](../observations/O-0006-design-ci.md)
- **extends**: [R-0001](R-0001-cross-platform-evidence.md)
