"""
Tests for ui/theme.py — palette resolution and global stylesheet generation.
"""

import pytest

from PyQt6.QtWidgets import QApplication

from ui import theme
from ui.theme import (
    DARK_PALETTE,
    LIGHT_PALETTE,
    apply_theme,
    current_palette,
    _build_global_qss,
    _palette_for,
)


@pytest.fixture(scope="module")
def qapp():
    """A single QApplication for all theme tests."""
    app = QApplication.instance() or QApplication([])
    yield app


class TestPaletteShape:
    """Both palettes must expose the same set of tokens."""

    def test_palettes_have_same_keys(self):
        assert set(DARK_PALETTE.keys()) == set(LIGHT_PALETTE.keys())

    def test_no_empty_values(self):
        for name, p in (("dark", DARK_PALETTE), ("light", LIGHT_PALETTE)):
            for k, v in p.items():
                assert v.startswith("#"), f"{name}/{k} = {v!r} is not a hex code"
                assert len(v) in (4, 7, 9), f"{name}/{k} = {v!r} has unexpected length"

    def test_dark_and_light_diverge_on_backgrounds(self):
        # The whole point — bg/text actually differ.
        assert DARK_PALETTE["bg_app"] != LIGHT_PALETTE["bg_app"]
        assert DARK_PALETTE["text_primary"] != LIGHT_PALETTE["text_primary"]

    def test_red_accent_is_identical(self):
        # Brand red works on both backgrounds; spec says keep it the same.
        assert DARK_PALETTE["accent_red"] == LIGHT_PALETTE["accent_red"]


class TestPaletteResolution:
    def test_dark_resolves_to_dark(self):
        assert _palette_for("dark") is DARK_PALETTE

    def test_light_resolves_to_light(self):
        assert _palette_for("light") is LIGHT_PALETTE

    def test_unknown_falls_back_to_dark(self):
        assert _palette_for("garbage") is DARK_PALETTE
        assert _palette_for("") is DARK_PALETTE


class TestApplyTheme:
    def test_apply_dark_sets_app_stylesheet(self, qapp):
        apply_theme("dark")
        qss = qapp.styleSheet()
        # Dark-specific values + key selectors present
        assert DARK_PALETTE["bg_app"] in qss  # "#000000"
        assert "#Sidebar" in qss
        assert "#LayerCard" in qss
        assert "#WritingEditor" in qss

    def test_apply_light_sets_app_stylesheet(self, qapp):
        apply_theme("light")
        qss = qapp.styleSheet()
        assert LIGHT_PALETTE["bg_app"] in qss  # "#ffffff"
        assert "#Sidebar" in qss
        # Light should NOT use the dark bg as bg_app
        # (note: #000000 may still appear as text_inverse, hence we check it's
        #  not used in the QMainWindow rule which fixes app bg)
        assert f"background-color: {LIGHT_PALETTE['bg_app']}" in qss

    def test_apply_garbage_falls_back_to_dark(self, qapp):
        apply_theme("garbage")
        qss = qapp.styleSheet()
        assert DARK_PALETTE["bg_app"] in qss

    def test_apply_is_idempotent(self, qapp):
        apply_theme("light")
        first = qapp.styleSheet()
        apply_theme("light")
        second = qapp.styleSheet()
        assert first == second


class TestBuildGlobalQss:
    """The QSS builder injects every QSS-targeted token from the palette."""

    # Tokens consumed at runtime via current_palette() (not in the QSS string).
    # Calendar cell colors are applied via QTextCharFormat in calendar_view.
    RUNTIME_ONLY_TOKENS = {
        "calendar_today_bg",
        "calendar_today_fg",
        "calendar_completed_bg",
        "calendar_completed_fg",
    }

    def test_dark_qss_contains_every_qss_token(self):
        qss = _build_global_qss(DARK_PALETTE)
        for token, value in DARK_PALETTE.items():
            if token in self.RUNTIME_ONLY_TOKENS:
                continue
            assert value in qss, f"Token {token}={value!r} not used in QSS"

    def test_light_qss_contains_every_qss_token(self):
        qss = _build_global_qss(LIGHT_PALETTE)
        for token, value in LIGHT_PALETTE.items():
            if token in self.RUNTIME_ONLY_TOKENS:
                continue
            assert value in qss, f"Token {token}={value!r} not used in QSS"

    def test_qss_has_no_unrendered_braces(self):
        # f-string mishap detection: stray `{token}` left in output
        qss = _build_global_qss(DARK_PALETTE)
        # Real QSS uses single braces around rule bodies after f-string
        # processing. There should be no `{xxx}` placeholder-style strings.
        import re
        leftovers = re.findall(r"\{[a-z_]+\}", qss)
        assert not leftovers, f"Unrendered placeholders: {leftovers}"


class TestCurrentPalette:
    def test_reflects_settings(self, qapp, monkeypatch, tmp_path):
        # Point config at a temp file and write a theme value
        import core.config as cfg
        cfg_file = tmp_path / "config.json"
        monkeypatch.setattr(cfg, "CONFIG_FILE", cfg_file)
        monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg, "_settings", None)

        s = cfg.get_settings()
        s.appearance.theme = "light"
        s.save()
        cfg.reload_settings()

        assert current_palette() is LIGHT_PALETTE

        s.appearance.theme = "dark"
        s.save()
        cfg.reload_settings()

        assert current_palette() is DARK_PALETTE
