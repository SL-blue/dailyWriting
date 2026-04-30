"""
Builds the LLM instruction from a per-layer state dict.

See TAG_SYSTEM_SPEC.md for the layer model. Each of the four layers
(territory, emotional_weather, craft, seed) is independently:

    - "off"        — contributes nothing
    - "random"     — system picks one tag from one randomly-chosen category
                     within the layer at generation time
    - "specified"  — user picks specific tag IDs

If `layer_state` is None or omits the seed layer, seed defaults to "random".
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from .tags import (
    LAYER_CATEGORIES,
    LAYER_LABELS,
    LAYERS,
    TAG_REGISTRY,
    Tag,
)


LayerState = Dict[str, Dict[str, object]]


# Defaults the model overuses; rotated subset injected into each prompt.
_BANNED_DEFAULTS: List[str] = [
    "candles",
    "rain",
    "ticking clocks",
    "cigarette smoke",
    "train stations",
    "music boxes",
    "faded photographs",
]


def build_topic_instruction(layer_state: Optional[LayerState] = None) -> str:
    """
    Build the LLM instruction string for a single topic generation.

    Args:
        layer_state: Per-layer configuration. See module docstring.

    Returns:
        A multi-line instruction string ready to send to the LLM.
    """
    state = _normalize(layer_state)
    selected = _resolve_selections(state)
    return _format_prompt(selected)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _normalize(layer_state: Optional[LayerState]) -> LayerState:
    """Fill in defaults for layers the caller didn't specify."""
    state: LayerState = {}
    incoming = layer_state or {}
    for layer in LAYERS:
        if layer in incoming:
            state[layer] = incoming[layer]
        elif layer == "seed":
            state[layer] = {"state": "random"}
        else:
            state[layer] = {"state": "off"}
    return state


def _resolve_selections(state: LayerState) -> Dict[str, List[Tag]]:
    """Turn each layer's config into a concrete list of selected Tags."""
    selected: Dict[str, List[Tag]] = {}
    for layer, conf in state.items():
        kind = conf.get("state", "off")
        if kind == "off":
            continue
        if kind == "specified":
            tag_ids = conf.get("tag_ids", []) or []
            tags = [TAG_REGISTRY[tid] for tid in tag_ids if tid in TAG_REGISTRY]
            if tags:
                selected[layer] = tags
        elif kind == "random":
            tag = _pick_random_for_layer(layer)
            if tag is not None:
                selected[layer] = [tag]
    return selected


def _pick_random_for_layer(layer: str) -> Optional[Tag]:
    """
    Pick one tag from one randomly-chosen category in the layer.
    Seed is special-cased: choose situation OR one role category, not both.
    """
    if layer == "seed":
        category_pool = ["situation", "object_role", "setting_role", "time_role"]
    else:
        category_pool = list(LAYER_CATEGORIES[layer])
    random.shuffle(category_pool)
    for cat in category_pool:
        candidates = [t for t in TAG_REGISTRY.values() if t.category == cat]
        if candidates:
            return random.choice(candidates)
    return None


def _format_prompt(selected: Dict[str, List[Tag]]) -> str:
    lines: List[str] = [
        "You are generating a short story-like snippet for a daily writing exercise.",
        "Output the snippet itself — do not say \"Write about…\" or address the reader.",
        "",
    ]

    for layer in LAYERS:
        tags = selected.get(layer)
        if not tags:
            continue
        directives = "; ".join(t.directive for t in tags)
        lines.append(f"{LAYER_LABELS[layer]}: {directives}.")

    lines.append("")
    lines.append("Invent all specifics. Avoid the most obvious imagery for this combination.")

    banned_line = _banned_defaults_line()
    if banned_line:
        lines.append(banned_line)

    lines.append(_form_closing_instruction(selected.get("craft", [])))
    lines.append("Output only the snippet.")

    return "\n".join(lines)


def _banned_defaults_line() -> str:
    if not _BANNED_DEFAULTS:
        return ""
    k = min(4, len(_BANNED_DEFAULTS))
    picks = random.sample(_BANNED_DEFAULTS, k=k)
    return f"Do not use: {', '.join(picks)}."


_FORM_CLOSING = {
    "form_sentence": "Write exactly one sentence.",
    "form_paragraph": "Write a short paragraph (2–4 sentences).",
    "form_two_sentence": "Write exactly two sentences.",
}


def _form_closing_instruction(craft_tags: List[Tag]) -> str:
    for t in craft_tags:
        if t.category == "form" and t.id in _FORM_CLOSING:
            return _FORM_CLOSING[t.id]
    return "Write one or two sentences."
