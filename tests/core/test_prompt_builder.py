"""
Tests for core/prompt_builder.py — the layered prompt instruction builder.
"""

import random

import pytest

from core import prompt_builder
from core.prompt_builder import build_topic_instruction
from core.tags import LAYER_LABELS, TAG_REGISTRY, tags_in_layer


@pytest.fixture(autouse=True)
def _seed_random():
    """Make random selections deterministic per test."""
    random.seed(0)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_no_args_defaults_seed_random_others_off(self):
        prompt = build_topic_instruction()
        # Seed line should appear; others should not.
        assert f"{LAYER_LABELS['seed']}:" in prompt
        assert f"{LAYER_LABELS['territory']}:" not in prompt
        assert f"{LAYER_LABELS['emotional_weather']}:" not in prompt
        assert f"{LAYER_LABELS['craft']}:" not in prompt

    def test_empty_dict_same_as_no_args(self):
        prompt = build_topic_instruction({})
        assert f"{LAYER_LABELS['seed']}:" in prompt

    def test_explicit_seed_off_overrides_default(self):
        prompt = build_topic_instruction({"seed": {"state": "off"}})
        assert f"{LAYER_LABELS['seed']}:" not in prompt


# ---------------------------------------------------------------------------
# Off / Random / Specified
# ---------------------------------------------------------------------------

class TestLayerStates:
    def test_off_layer_omitted(self):
        prompt = build_topic_instruction({
            "territory": {"state": "off"},
            "emotional_weather": {"state": "off"},
            "craft": {"state": "off"},
            "seed": {"state": "off"},
        })
        for label in LAYER_LABELS.values():
            assert f"{label}:" not in prompt

    def test_random_layer_produces_one_directive(self):
        prompt = build_topic_instruction({
            "territory": {"state": "random"},
            "emotional_weather": {"state": "off"},
            "craft": {"state": "off"},
            "seed": {"state": "off"},
        })
        # The territory line must exist and contain at least one of the layer's directives.
        territory_directives = {t.directive for t in tags_in_layer("territory")}
        territory_lines = [
            line for line in prompt.splitlines()
            if line.startswith(f"{LAYER_LABELS['territory']}:")
        ]
        assert len(territory_lines) == 1
        body = territory_lines[0].split(":", 1)[1].strip().rstrip(".")
        assert body in territory_directives

    def test_specified_layer_honors_user_selection(self):
        prompt = build_topic_instruction({
            "craft": {
                "state": "specified",
                "tag_ids": ["perspective_second", "structural_opens_dialogue"],
            },
            "seed": {"state": "off"},
        })
        craft_line = next(
            line for line in prompt.splitlines()
            if line.startswith(f"{LAYER_LABELS['craft']}:")
        )
        assert TAG_REGISTRY["perspective_second"].directive in craft_line
        assert TAG_REGISTRY["structural_opens_dialogue"].directive in craft_line

    def test_specified_with_unknown_tag_ids_filtered(self):
        prompt = build_topic_instruction({
            "craft": {
                "state": "specified",
                "tag_ids": ["does_not_exist", "perspective_first"],
            },
            "seed": {"state": "off"},
        })
        craft_line = next(
            line for line in prompt.splitlines()
            if line.startswith(f"{LAYER_LABELS['craft']}:")
        )
        assert "does_not_exist" not in craft_line
        assert TAG_REGISTRY["perspective_first"].directive in craft_line

    def test_specified_with_empty_tag_ids_omitted(self):
        prompt = build_topic_instruction({
            "craft": {"state": "specified", "tag_ids": []},
            "seed": {"state": "off"},
        })
        assert f"{LAYER_LABELS['craft']}:" not in prompt


# ---------------------------------------------------------------------------
# Form tag → closing instruction
# ---------------------------------------------------------------------------

class TestFormClosingInstruction:
    def _prompt_with_form(self, form_id):
        return build_topic_instruction({
            "craft": {"state": "specified", "tag_ids": [form_id]},
            "seed": {"state": "off"},
        })

    def test_form_sentence(self):
        assert "Write exactly one sentence." in self._prompt_with_form("form_sentence")

    def test_form_paragraph(self):
        assert "Write a short paragraph (2–4 sentences)." in self._prompt_with_form("form_paragraph")

    def test_form_two_sentence(self):
        assert "Write exactly two sentences." in self._prompt_with_form("form_two_sentence")

    def test_no_form_tag_default_closing(self):
        prompt = build_topic_instruction({
            "craft": {"state": "specified", "tag_ids": ["perspective_first"]},
            "seed": {"state": "off"},
        })
        assert "Write one or two sentences." in prompt

    def test_completely_empty_state_default_closing(self):
        prompt = build_topic_instruction({
            "territory": {"state": "off"},
            "emotional_weather": {"state": "off"},
            "craft": {"state": "off"},
            "seed": {"state": "off"},
        })
        assert "Write one or two sentences." in prompt


# ---------------------------------------------------------------------------
# Anti-repetition / housekeeping lines
# ---------------------------------------------------------------------------

class TestHousekeeping:
    def test_anti_repetition_line_present(self):
        prompt = build_topic_instruction()
        assert "Invent all specifics. Avoid the most obvious imagery for this combination." in prompt

    def test_output_only_snippet_line_present(self):
        prompt = build_topic_instruction()
        assert "Output only the snippet." in prompt

    def test_no_writing_coach_preamble(self):
        prompt = build_topic_instruction()
        # Spec explicitly says remove the "writing coach" framing.
        assert "writing coach" not in prompt.lower()

    def test_banned_defaults_line_present(self):
        prompt = build_topic_instruction()
        assert "Do not use:" in prompt


# ---------------------------------------------------------------------------
# Random layer — seed special case
# ---------------------------------------------------------------------------

class TestRandomSeedLayer:
    def test_seed_random_picks_from_a_single_seed_category(self, monkeypatch):
        # Force the random category to "situation" deterministically.
        chosen_categories = []

        real_choice = random.choice
        real_shuffle = random.shuffle

        def spy_shuffle(seq):
            real_shuffle(seq)
            chosen_categories.append(seq[0])

        monkeypatch.setattr(random, "shuffle", spy_shuffle)

        prompt = build_topic_instruction({
            "territory": {"state": "off"},
            "emotional_weather": {"state": "off"},
            "craft": {"state": "off"},
            "seed": {"state": "random"},
        })

        seed_line = next(
            line for line in prompt.splitlines()
            if line.startswith(f"{LAYER_LABELS['seed']}:")
        )
        # Exactly one tag (one directive, no semicolons).
        body = seed_line.split(":", 1)[1].strip().rstrip(".")
        assert ";" not in body

    def test_random_layer_is_deterministic_with_seed(self):
        random.seed(42)
        a = build_topic_instruction({"territory": {"state": "random"},
                                     "seed": {"state": "off"}})
        random.seed(42)
        b = build_topic_instruction({"territory": {"state": "random"},
                                     "seed": {"state": "off"}})
        assert a == b
