# core/tags.py

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Tag:
    id: str          # e.g. "genre_detective"
    label: str       # e.g. "Detective / Mystery"
    category: str    # e.g. "genre"
    description: str # human description
    # This can hold concrete phrases / elements that represent the tendency.
    elements: List[str]


# A small initial vocabulary.
TAG_REGISTRY: Dict[str, Tag] = {
    # ---- Genre / Style ----
    "genre_daily": Tag(
        id="genre_daily",
        label="Daily life",
        category="genre",
        description="Everyday life, journals, slice-of-life scenes.",
        elements=[
            "an ordinary day routine",
            "a small decision in daily life",
            "a quiet moment on a commute",
            "a conversation over breakfast",
        ],
    ),
    "genre_detective": Tag(
        id="genre_detective",
        label="Detective / Mystery",
        category="genre",
        description="Investigation, secrets, clues.",
        elements=[
            "an unsolved case",
            "a missing person report",
            "a strange clue that does not fit",
            "an investigator who notices tiny details",
        ],
    ),
    "genre_fantasy": Tag(
        id="genre_fantasy",
        label="Fantasy",
        category="genre",
        description="Magic, other worlds, strange rules.",
        elements=[
            "a hidden magical rule of the world",
            "a market where impossible items are sold",
            "a door that appears only at midnight",
        ],
    ),

    # ---- Mood ----
    "mood_cozy": Tag(
        id="mood_cozy",
        label="Cozy / Warm",
        category="mood",
        description="Safe, warm, intimate atmosphere.",
        elements=[
            "warm indoor light on a rainy day",
            "the smell of something baking in the kitchen",
            "a familiar room full of worn furniture",
        ],
    ),
    "mood_eerie": Tag(
        id="mood_eerie",
        label="Eerie",
        category="mood",
        description="Subtle unease, uncanny feeling.",
        elements=[
            "a nearly empty street at night",
            "a buzzing streetlamp in the fog",
            "the sense that someone is watching",
        ],
    ),

    # ---- Place ----
    "place_city": Tag(
        id="place_city",
        label="City",
        category="place",
        description="Urban streets, apartments, offices.",
        elements=[
            "a narrow city alley behind tall buildings",
            "a crowded subway platform",
            "a rooftop overlooking neon lights",
        ],
    ),
    "place_nature": Tag(
        id="place_nature",
        label="Nature",
        category="place",
        description="Forest, lake, mountains.",
        elements=[
            "a quiet path through dense trees",
            "a lake reflecting the sky at dusk",
            "a wind-swept hillside",
        ],
    ),

    # ---- Time ----
    "time_evening": Tag(
        id="time_evening",
        label="Evening",
        category="time",
        description="Early night, lights turning on.",
        elements=[
            "the moment when streetlights just turn on",
            "the sky turning from blue to dark",
        ],
    ),
    "time_midnight": Tag(
        id="time_midnight",
        label="Midnight",
        category="time",
        description="Deep night, fewer people, stranger things.",
        elements=[
            "a clock striking midnight",
            "a city that feels different after midnight",
        ],
    ),

    # ---- Event ----
    "event_chance_meeting": Tag(
        id="event_chance_meeting",
        label="Chance meeting",
        category="event",
        description="Two people run into each other by accident.",
        elements=[
            "two strangers meeting at a bus stop",
            "someone bumping into another in a bookstore",
            "an old friend unexpectedly appearing in a crowd",
        ],
    ),
    "event_mystery_clue": Tag(
        id="event_mystery_clue",
        label="Mystery clue",
        category="event",
        description="Someone finds something that doesn't make sense.",
        elements=[
            "a photograph that should not exist",
            "a note with only a time and a place written",
        ],
    ),

    # ---- Items ----
    "item_photo": Tag(
        id="item_photo",
        label="Photograph",
        category="item",
        description="A photo related to the story.",
        elements=[
            "an old photograph with one face scratched out",
            "a photo taken on a day no one remembers",
        ],
    ),
    "item_key": Tag(
        id="item_key",
        label="Key",
        category="item",
        description="A key to some door, box or secret.",
        elements=[
            "a key with no lock to match",
            "a heavy, old-fashioned key found in a pocket",
        ],
    ),

    # ---- Skill / Focus ----
    "skill_dialogue": Tag(
        id="skill_dialogue",
        label="Dialogue focus",
        category="skill",
        description="Emphasis on conversation.",
        elements=[
            "focus on what the characters say and how they say it",
        ],
    ),
    "skill_description": Tag(
        id="skill_description",
        label="Description focus",
        category="skill",
        description="Emphasis on sensory details.",
        elements=[
            "focus on the sensory details of the scene",
        ],
    ),

    # ---- Form ----
    "form_sentence": Tag(
        id="form_sentence",
        label="One sentence prompt",
        category="form",
        description="Return a single, rich sentence.",
        elements=[],
    ),
    "form_paragraph": Tag(
        id="form_paragraph",
        label="Short paragraph prompt",
        category="form",
        description="Return a short paragraph describing a scene.",
        elements=[],
    ),
}
