# core/prompt_builder.py

import random
from collections import defaultdict
from typing import List

from .tags import TAG_REGISTRY, Tag


def build_topic_instruction(selected_tag_ids: List[str]) -> str:
    """
    Given a list of tag IDs, build a natural-language instruction to send to the LLM
    so it can generate a single writing prompt.
    """

    if not selected_tag_ids:
        # fallback: extremely generic
        return (
            "Generate a single creative writing prompt about a small, meaningful moment "
            "in someone's life. Return only the prompt sentence or paragraph."
        )

    # group tags by category (genre, mood, place...)
    tags_by_cat: dict[str, List[Tag]] = defaultdict(list)
    for tid in selected_tag_ids:
        tag = TAG_REGISTRY.get(tid)
        if tag:
            tags_by_cat[tag.category].append(tag)

    # helper: pick 1–2 random elements from the tags in one category
    def pick_elements(cat: str, max_count: int = 2) -> List[str]:
        candidates: List[str] = []
        for t in tags_by_cat.get(cat, []):
            candidates.extend(t.elements)
        random.shuffle(candidates)
        return candidates[:max_count]

    genre_phrases   = pick_elements("genre", 2)
    mood_phrases    = pick_elements("mood", 2)
    place_phrases   = pick_elements("place", 2)
    time_phrases    = pick_elements("time", 2)
    event_phrases   = pick_elements("event", 2)
    item_phrases    = pick_elements("item", 2)
    skill_phrases   = pick_elements("skill", 2)

    # form control
    form_tags = tags_by_cat.get("form", [])
    if any(t.id == "form_sentence" for t in form_tags):
        form_instruction = "Return the prompt as a single evocative sentence."
    elif any(t.id == "form_paragraph" for t in form_tags):
        form_instruction = "Return the prompt as a short paragraph (2–4 sentences)."
    else:
        form_instruction = "Return the prompt as one or two sentences."

    lines: List[str] = []
    lines.append("You are a writing coach creating prompts for daily practice.")
    lines.append("Generate exactly one creative writing prompt.")
    lines.append("Use the following tendencies as inspiration:")

    if genre_phrases:
        lines.append(f"- Style / genre: {', '.join(genre_phrases)}.")
    if mood_phrases:
        lines.append(f"- Atmosphere / mood: {', '.join(mood_phrases)}.")
    if place_phrases:
        lines.append(f"- Setting or place: {', '.join(place_phrases)}.")
    if time_phrases:
        lines.append(f"- Time: {', '.join(time_phrases)}.")
    if event_phrases:
        lines.append(f"- Central event or situation: {', '.join(event_phrases)}.")
    if item_phrases:
        lines.append(f"- Important objects: {', '.join(item_phrases)}.")
    if skill_phrases:
        lines.append(f"- Writing focus: {', '.join(skill_phrases)}.")

    lines.append(
        "Do not explain the prompt or mention these notes directly. "
        "Just output the final prompt the writer should respond to."
    )
    lines.append(form_instruction)

    # This full string becomes the user message to the LLM
    return "\n".join(lines)
