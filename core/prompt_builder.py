# core/prompt_builder.py

import random
from collections import defaultdict
from typing import List

from .tags import TAG_REGISTRY, Tag


def build_topic_instruction(selected_tag_ids: List[str]) -> str:
    """
    Given a list of tag IDs, build a natural-language instruction for the LLM
    to generate a single story-like sentence or short paragraph that implies a story.
    The 'elements' inside tags are used only as invisible examples for the LLM.
    """

    # group tags by category (genre, mood, place, time, event, item, skill, form, ...)
    tags_by_cat: dict[str, List[Tag]] = defaultdict(list)
    for tid in selected_tag_ids:
        tag = TAG_REGISTRY.get(tid)
        if tag:
            tags_by_cat[tag.category].append(tag)

    # Helper: get visible names for genres / form
    genre_labels = [t.label for t in tags_by_cat.get("genre", [])]
    form_tags = tags_by_cat.get("form", [])

    # Helper: pick some *example* elements per category (hidden from user)
    def pick_example_elements(cat: str, max_count: int = 3) -> List[str]:
        candidates: List[str] = []
        for t in tags_by_cat.get(cat, []):
            candidates.extend(t.elements)
        random.shuffle(candidates)
        return candidates[:max_count]

    mood_examples   = pick_example_elements("mood", 3)
    place_examples  = pick_example_elements("place", 3)
    time_examples   = pick_example_elements("time", 3)
    event_examples  = pick_example_elements("event", 3)
    item_examples   = pick_example_elements("item", 3)
    skill_examples  = pick_example_elements("skill", 2)

    # Decide output form
    if any(t.id == "form_sentence" for t in form_tags):
        form_instruction = (
            "Write exactly one sentence that reads like a moment from a story. "
            "It should feel like the beginning or a fragment of a scene."
        )
    elif any(t.id == "form_paragraph" for t in form_tags):
        form_instruction = (
            "Write a short paragraph (2–4 sentences) that reads like a moment from a story. "
            "It should feel like the beginning or a fragment of a scene."
        )
    else:
        form_instruction = (
            "Write one or two sentences that read like a moment from a story. "
            "It should feel like the beginning or a fragment of a scene."
        )

    lines: List[str] = []

    # High-level role + behavior
    lines.append(
        "You are a writing coach creating short story-like prompts for daily writing practice."
    )
    lines.append(
        "Generate exactly one story-like snippet that implies a larger story, "
        "rather than an instruction. It should sound as if it comes from the beginning "
        "or a small fragment of a longer narrative."
    )

    # Visible genre info
    if genre_labels:
        lines.append(
            "The style/genre should be somewhere in the space suggested by these genre labels: "
            + ", ".join(genre_labels)
            + "."
        )

    # Invisible inspirations for other dimensions
    # Tell the model clearly that these are *examples*, not mandatory phrases.
    def add_example_block(title: str, examples: List[str]):
        if examples:
            joined = "; ".join(examples)
            lines.append(
                f"As inspiration for the {title}, think of examples like: {joined}. "
                f"These are just references to the feeling; do NOT copy these phrases literally. "
                f"Invent your own details that fit this space."
            )

    add_example_block("atmosphere or mood", mood_examples)
    add_example_block("setting or place", place_examples)
    add_example_block("time or period", time_examples)
    add_example_block("central situation or event", event_examples)
    add_example_block("important objects or props", item_examples)
    add_example_block("writing focus (what kind of scene to emphasize)", skill_examples)

    # Output and constraints
    lines.append(
        "Do NOT say things like 'Write about...' or 'Describe...'. "
        "Do NOT address the reader directly, and do NOT explain that this is a prompt. "
        "Simply output the story-like snippet itself, as if it were taken from a story."
    )
    lines.append(form_instruction)

    # final instruction string
    return "\n".join(lines)
