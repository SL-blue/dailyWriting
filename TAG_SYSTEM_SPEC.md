# Tag System & Prompt Builder Redesign Spec

## Goal

Replace the current flat tag system with a layered system that produces more varied, less repetitive LLM output. Balance user control with generative randomness by making each layer independently togglable between off / random / specified.

## Architecture Overview

The tag system has **four layers**. Each layer answers a different kind of question about the prompt and contributes a different kind of constraint to the LLM. Users interact with layers, not individual tags directly.

For each layer, the user chooses one of three states:
- **Off** — layer contributes nothing to the prompt
- **Random** — system picks 1 tag from the layer at generation time
- **Specified** — user picks 1+ specific tags from the layer

Random selection happens **at generation time**, not selection time. Hitting generate twice with the same settings can produce different prompts because random layers re-roll.

## The Four Layers

### Layer 1: Territory
What world are we in? Genre and tonal register.

**Categories in this layer:**
- `genre` — literary, speculative, noir, romance, horror, comic, historical, surreal, fable, slice-of-life
- `register` — lyrical, terse, clinical, ornate, colloquial, fable-like, journalistic, stream-of-consciousness

### Layer 2: Emotional Weather
What does the scene feel like? Mood and tension.

**Categories in this layer:**
- `mood` — emotional temperatures, NOT lists of mood-evoking nouns. Examples of valid mood tags: "held breath," "dawning recognition," "low-grade dread," "tender exhaustion," "quiet euphoria," "uneasy calm"
- `tension` — what kind of pressure is in the scene: internal conflict, interpersonal friction, dramatic irony, withheld information, looming decision, aftermath, mystery, person-vs-environment

### Layer 3: Craft
How is it written? Structural and stylistic constraints.

**Categories in this layer:**
- `perspective` — first-person, close third, omniscient, second-person, collective "we," unreliable narrator
- `temporal_stance` — in-the-moment present, retrospective, anticipatory, conditional ("if she had known…"), iterative ("every Sunday she would…")
- `structural_move` — opens with dialogue, opens mid-action, single sustained image, ends on a question, withholds the central fact, list-form, one-sentence
- `form` — sentence, short paragraph, two-sentence (replaces the existing form_sentence/form_paragraph)

### Layer 4: Seed
What's the spark? Situation and role-based generative seeds. **This layer defaults to "Random" if user has not configured anything.**

**Categories in this layer:**
- `situation` — a threshold moment, a small betrayal, an interrupted ritual, an unexpected kindness, a misrecognition, a return, a refusal, an arrival of news, a confession, a departure
- `object_role` — replaces the old `item` category. Specifies the *role* an object plays, not the object itself. Examples: "an object that holds memory," "an object out of place," "an object being given," "an object being hidden," "an object that breaks," "an object never named"
- `setting_role` — replaces the old `place` category. Examples: "a place of waiting," "a place of transition," "a private place made public," "a familiar place made strange," "a borrowed space," "a threshold space"
- `time_role` — replaces the old `time` category. Examples: "the moment before," "the moment after," "a held interval," "a time misremembered," "a recurring time," "an interrupted routine"

## Critical Implementation Rules

### Tag content
- **Do NOT include `elements` lists on tags the way the current system does.** The whole point of this redesign is to stop feeding the LLM concrete noun examples that it then anchors to. Each tag is just a label + a short directive phrase that gets injected into the prompt.
- Each tag should have: `id`, `category`, `layer`, `label` (user-facing), `directive` (what gets sent to the LLM as the constraint phrase)
- Example tag:
  ```python
  Tag(
      id="object_role_memory",
      category="object_role",
      layer="seed",
      label="An object that holds memory",
      directive="an object that holds memory or carries the weight of the past"
  )
  ```

### Layer state
- Layer state is stored per-generation, not per-tag. The user's selections look like:
  ```python
  {
      "territory": {"state": "off"},
      "emotional_weather": {"state": "random"},
      "craft": {"state": "specified", "tag_ids": ["perspective_second", "structural_opens_dialogue"]},
      "seed": {"state": "random"},  # default
  }
  ```

### Randomness
- When a layer is in "random" state, at generation time pick **one tag from one randomly-chosen category within that layer**. Don't pick one tag from every category — that over-constrains.
- Exception: the Seed layer in random mode should usually pick from `situation` OR from one of the role categories, not both. A situation tag is often enough to anchor a scene.

### Multi-tag selection
- In "specified" state, users may pick multiple tags from any category in the layer, and from multiple categories. The LLM handles combinations well.

## Prompt Builder Spec

### Structure
The prompt sent to the LLM should be **short and structurally clean**. Roughly:

```
You are generating a short story-like snippet for a daily writing exercise.
Output the snippet itself — do not say "Write about…" or address the reader.

[Constraints, one line per active layer:]
Genre/Register: literary, terse.
Emotional weather: low-grade dread; internal conflict.
Craft: close third; retrospective; opens mid-action; one paragraph.
Seed: an interrupted ritual involving an object out of place.

Invent all specifics. Avoid the most obvious imagery for this combination.
Output only the snippet.
```

### Per-layer formatting in prompt
- Each active layer becomes one line in the prompt with the format `[Layer label]: [directive 1]; [directive 2]; ...`
- If a layer is "off," omit it entirely from the prompt.
- If a layer is "random" or "specified," join the directive strings of selected tags with `; `.
- Form tag (from Craft layer) determines the closing instruction:
  - `form_sentence` → "Write exactly one sentence."
  - `form_paragraph` → "Write a short paragraph (2–4 sentences)."
  - `form_two_sentence` → "Write exactly two sentences."
  - If no form tag is active → "Write one or two sentences."

### Anti-repetition mechanism
Always include the line: `Invent all specifics. Avoid the most obvious imagery for this combination.`

Optionally (worth experimenting with) maintain a small rotating list of "banned" defaults the model overuses — candles, rain, ticking clocks, cigarette smoke, train stations, music boxes, faded photographs — and inject 3–5 of them per call as: `Do not use: candles, rain, music boxes.` Rotate the list each call.

### What to remove from current prompt
- Remove the long preamble about being a "writing coach."
- Remove the "these are just references, do not copy literally" hedging — it doesn't work and adds noise.
- Remove all per-category example blocks ("As inspiration for the atmosphere, think of examples like…"). These are the source of the repetition problem.
- Keep the "do not say 'Write about…'" instruction; that one matters.

## Migration Notes

### Breaking changes
- `tags.py` schema changes: `Tag` dataclass loses `elements`, gains `layer` and `directive`.
- `prompt_builder.build_topic_instruction()` signature changes from `List[str]` (tag IDs) to a layer state dict (see "Layer state" above).
- Stored sessions are unaffected — these changes are only to topic generation, not session storage.

### UI changes (for separate implementation, not in this spec)
The `tag_selector_dialog.py` will need rework to show four layer cards with [Off / Random / Specified] tri-state controls and disclosure for the "Specified" picker. Out of scope for this spec; flag this as a follow-up.

### Backwards compatibility
None needed for the topic generator — it's stateless. The old `selected_tag_ids` list format can be dropped.

## Implementation Order

1. Rewrite `core/tags.py` with the new schema and populated tag set across all four layers.
2. Rewrite `core/prompt_builder.py` to consume layer state and produce the new prompt format.
3. Update `core/topic_generator.py` to pass layer state through (the actual API call logic is unchanged).
4. Update or write tests for the new prompt builder. Verify: off layers omitted, random layers produce a tag, specified layers honor user selection, form tag produces correct closing instruction.
5. (Separate task) Update `ui/tag_selector_dialog.py` for the new layer-based UI.

## Open Questions to Defer

- Coherence rules (preventing contradictory random rolls like "comic genre + dread mood") — defer until we see real outputs and decide if it's a problem.
- Per-layer "specificity slider" (random / pick one / pick multiple) — defer; tri-state is probably enough.
- Persisting user's last layer state as a default — defer to a settings task.
