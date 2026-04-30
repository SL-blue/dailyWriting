"""
Tag definitions for the layered prompt system.

Each tag belongs to a `category`, which belongs to a `layer`. Users interact
with layers (Off / Random / Specified) — see TAG_SYSTEM_SPEC.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Tag:
    id: str         # e.g. "object_role_memory"
    category: str   # e.g. "object_role"
    layer: str      # one of: territory, emotional_weather, craft, seed
    label: str      # user-facing
    directive: str  # short phrase injected into the prompt


# Layer → ordered list of categories that belong to it.
LAYER_CATEGORIES: Dict[str, List[str]] = {
    "territory": ["genre", "register"],
    "emotional_weather": ["mood", "tension"],
    "craft": ["perspective", "temporal_stance", "structural_move", "form"],
    "seed": ["situation", "object_role", "setting_role", "time_role"],
}

# Layer → label used in the prompt itself.
LAYER_LABELS: Dict[str, str] = {
    "territory": "Genre/Register",
    "emotional_weather": "Emotional weather",
    "craft": "Craft",
    "seed": "Seed",
}

LAYERS: List[str] = list(LAYER_CATEGORIES.keys())


def _t(tag_id: str, category: str, layer: str, label: str, directive: str) -> Tag:
    return Tag(id=tag_id, category=category, layer=layer, label=label, directive=directive)


_RAW_TAGS: List[Tag] = [
    # ============================================================
    # Layer 1: Territory
    # ============================================================
    # genre
    _t("genre_literary", "genre", "territory", "Literary", "literary"),
    _t("genre_speculative", "genre", "territory", "Speculative", "speculative"),
    _t("genre_noir", "genre", "territory", "Noir", "noir"),
    _t("genre_romance", "genre", "territory", "Romance", "romance"),
    _t("genre_horror", "genre", "territory", "Horror", "horror"),
    _t("genre_comic", "genre", "territory", "Comic", "comic"),
    _t("genre_historical", "genre", "territory", "Historical", "historical"),
    _t("genre_surreal", "genre", "territory", "Surreal", "surreal"),
    _t("genre_fable", "genre", "territory", "Fable", "fable"),
    _t("genre_slice_of_life", "genre", "territory", "Slice of life", "slice-of-life"),
    # register
    _t("register_lyrical", "register", "territory", "Lyrical", "lyrical"),
    _t("register_terse", "register", "territory", "Terse", "terse"),
    _t("register_clinical", "register", "territory", "Clinical", "clinical"),
    _t("register_ornate", "register", "territory", "Ornate", "ornate"),
    _t("register_colloquial", "register", "territory", "Colloquial", "colloquial"),
    _t("register_fable_like", "register", "territory", "Fable-like", "fable-like"),
    _t("register_journalistic", "register", "territory", "Journalistic", "journalistic"),
    _t("register_stream", "register", "territory", "Stream-of-consciousness", "stream-of-consciousness"),

    # ============================================================
    # Layer 2: Emotional Weather
    # ============================================================
    # mood — emotional temperatures, not noun-lists
    _t("mood_held_breath", "mood", "emotional_weather", "Held breath", "held breath"),
    _t("mood_dawning_recognition", "mood", "emotional_weather", "Dawning recognition", "dawning recognition"),
    _t("mood_low_grade_dread", "mood", "emotional_weather", "Low-grade dread", "low-grade dread"),
    _t("mood_tender_exhaustion", "mood", "emotional_weather", "Tender exhaustion", "tender exhaustion"),
    _t("mood_quiet_euphoria", "mood", "emotional_weather", "Quiet euphoria", "quiet euphoria"),
    _t("mood_uneasy_calm", "mood", "emotional_weather", "Uneasy calm", "uneasy calm"),
    _t("mood_brittle_cheer", "mood", "emotional_weather", "Brittle cheer", "brittle cheer"),
    _t("mood_resignation", "mood", "emotional_weather", "Resignation", "resignation"),
    # tension
    _t("tension_internal", "tension", "emotional_weather", "Internal conflict", "internal conflict"),
    _t("tension_interpersonal", "tension", "emotional_weather", "Interpersonal friction", "interpersonal friction"),
    _t("tension_dramatic_irony", "tension", "emotional_weather", "Dramatic irony", "dramatic irony"),
    _t("tension_withheld_info", "tension", "emotional_weather", "Withheld information", "withheld information"),
    _t("tension_looming_decision", "tension", "emotional_weather", "Looming decision", "a looming decision"),
    _t("tension_aftermath", "tension", "emotional_weather", "Aftermath", "aftermath"),
    _t("tension_mystery", "tension", "emotional_weather", "Mystery", "mystery"),
    _t("tension_person_vs_environment", "tension", "emotional_weather", "Person vs environment", "person-vs-environment pressure"),

    # ============================================================
    # Layer 3: Craft
    # ============================================================
    # perspective
    _t("perspective_first", "perspective", "craft", "First person", "first person"),
    _t("perspective_close_third", "perspective", "craft", "Close third", "close third"),
    _t("perspective_omniscient", "perspective", "craft", "Omniscient", "omniscient"),
    _t("perspective_second", "perspective", "craft", "Second person", "second person"),
    _t("perspective_collective_we", "perspective", "craft", "Collective \"we\"", "collective \"we\""),
    _t("perspective_unreliable", "perspective", "craft", "Unreliable narrator", "unreliable narrator"),
    # temporal stance
    _t("temporal_present", "temporal_stance", "craft", "In the moment", "in-the-moment present"),
    _t("temporal_retrospective", "temporal_stance", "craft", "Retrospective", "retrospective"),
    _t("temporal_anticipatory", "temporal_stance", "craft", "Anticipatory", "anticipatory"),
    _t("temporal_conditional", "temporal_stance", "craft", "Conditional", "conditional (\"if she had known…\")"),
    _t("temporal_iterative", "temporal_stance", "craft", "Iterative", "iterative (\"every Sunday she would…\")"),
    # structural move
    _t("structural_opens_dialogue", "structural_move", "craft", "Opens with dialogue", "opens with dialogue"),
    _t("structural_opens_mid_action", "structural_move", "craft", "Opens mid-action", "opens mid-action"),
    _t("structural_single_image", "structural_move", "craft", "Single sustained image", "a single sustained image"),
    _t("structural_ends_question", "structural_move", "craft", "Ends on a question", "ends on a question"),
    _t("structural_withholds_central_fact", "structural_move", "craft", "Withholds central fact", "withholds the central fact"),
    _t("structural_list_form", "structural_move", "craft", "List form", "list-form"),
    _t("structural_one_sentence", "structural_move", "craft", "One sentence", "one-sentence"),
    # form
    _t("form_sentence", "form", "craft", "One sentence", "one sentence"),
    _t("form_paragraph", "form", "craft", "Short paragraph", "one short paragraph"),
    _t("form_two_sentence", "form", "craft", "Two sentences", "two sentences"),

    # ============================================================
    # Layer 4: Seed
    # ============================================================
    # situation
    _t("situation_threshold_moment", "situation", "seed", "A threshold moment", "a threshold moment"),
    _t("situation_small_betrayal", "situation", "seed", "A small betrayal", "a small betrayal"),
    _t("situation_interrupted_ritual", "situation", "seed", "An interrupted ritual", "an interrupted ritual"),
    _t("situation_unexpected_kindness", "situation", "seed", "An unexpected kindness", "an unexpected kindness"),
    _t("situation_misrecognition", "situation", "seed", "A misrecognition", "a misrecognition"),
    _t("situation_return", "situation", "seed", "A return", "a return"),
    _t("situation_refusal", "situation", "seed", "A refusal", "a refusal"),
    _t("situation_arrival_of_news", "situation", "seed", "An arrival of news", "an arrival of news"),
    _t("situation_confession", "situation", "seed", "A confession", "a confession"),
    _t("situation_departure", "situation", "seed", "A departure", "a departure"),
    # object_role
    _t("object_role_memory", "object_role", "seed", "An object that holds memory", "an object that holds memory or carries the weight of the past"),
    _t("object_role_out_of_place", "object_role", "seed", "An object out of place", "an object out of place"),
    _t("object_role_being_given", "object_role", "seed", "An object being given", "an object being given"),
    _t("object_role_being_hidden", "object_role", "seed", "An object being hidden", "an object being hidden"),
    _t("object_role_breaks", "object_role", "seed", "An object that breaks", "an object that breaks"),
    _t("object_role_never_named", "object_role", "seed", "An object never named", "an object that is referred to but never named"),
    # setting_role
    _t("setting_role_waiting", "setting_role", "seed", "A place of waiting", "a place of waiting"),
    _t("setting_role_transition", "setting_role", "seed", "A place of transition", "a place of transition"),
    _t("setting_role_private_made_public", "setting_role", "seed", "A private place made public", "a private place made public"),
    _t("setting_role_familiar_made_strange", "setting_role", "seed", "A familiar place made strange", "a familiar place made strange"),
    _t("setting_role_borrowed", "setting_role", "seed", "A borrowed space", "a borrowed space"),
    _t("setting_role_threshold", "setting_role", "seed", "A threshold space", "a threshold space"),
    # time_role
    _t("time_role_moment_before", "time_role", "seed", "The moment before", "the moment before"),
    _t("time_role_moment_after", "time_role", "seed", "The moment after", "the moment after"),
    _t("time_role_held_interval", "time_role", "seed", "A held interval", "a held interval"),
    _t("time_role_misremembered", "time_role", "seed", "A time misremembered", "a time misremembered"),
    _t("time_role_recurring", "time_role", "seed", "A recurring time", "a recurring time"),
    _t("time_role_interrupted_routine", "time_role", "seed", "An interrupted routine", "an interrupted routine"),
]


TAG_REGISTRY: Dict[str, Tag] = {tag.id: tag for tag in _RAW_TAGS}


def tags_in_layer(layer: str) -> List[Tag]:
    return [t for t in TAG_REGISTRY.values() if t.layer == layer]


def tags_in_category(category: str) -> List[Tag]:
    return [t for t in TAG_REGISTRY.values() if t.category == category]
