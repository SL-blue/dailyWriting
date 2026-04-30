"""
Centralized theming for DailyWriting.

Defines the Dark and Light palettes and renders a single global QSS string
applied at the QApplication level. Every themed widget must have a stable
`setObjectName(...)` so the selectors here can reach it. Per-widget inline
`setStyleSheet()` should only carry layout-affecting properties (font-family,
font-size); colors and chrome belong in this module.

Public API:
    apply_theme(name: str)          — apply Dark or Light to the live app
    current_palette() -> dict       — palette currently in effect (per settings)
    DARK_PALETTE / LIGHT_PALETTE    — semantic-token dicts
"""

from __future__ import annotations

from typing import Dict

from PyQt6.QtWidgets import QApplication


# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------

DARK_PALETTE: Dict[str, str] = {
    # Surfaces
    "bg_app":            "#000000",
    "bg_surface":        "#111111",
    "bg_surface_alt":    "#1a1a1a",
    "bg_elevated":       "#222222",
    "bg_pressed":        "#2a2a2a",
    "bg_card_alt":       "#252525",
    # Text
    "text_primary":      "#ffffff",
    "text_secondary":    "#cccccc",
    "text_muted":        "#888888",
    "text_dim":          "#666666",
    "text_placeholder":  "#777777",
    "text_inverse":      "#000000",
    # Borders & hover
    "border":            "#333333",
    "border_strong":     "#444444",
    "hover":             "#333333",
    "hover_strong":      "#444444",
    # Accents
    "accent_red":        "#ff3b30",
    "accent_green":      "#00b894",
    "accent_green_hi":   "#00d9a5",
    "accent_green_lo":   "#009274",
    "accent_green_alt":  "#00a383",
    "accent_cyan":       "#00d0a0",
    "accent_mint":       "#6ee7c8",
    "accent_mint_hover": "#5fd7b8",
    "accent_neutral":         "#b3b3b3",
    "accent_neutral_hover":   "#c6c6c6",
    "accent_neutral_text":    "#000000",
    # Calendar (also read at runtime via current_palette())
    "calendar_today_bg":      "#333333",
    "calendar_today_fg":      "#ffffff",
    "calendar_completed_bg":  "#005f46",
    "calendar_completed_fg":  "#ffffff",
}


LIGHT_PALETTE: Dict[str, str] = {
    # Surfaces
    "bg_app":            "#ffffff",
    "bg_surface":        "#f5f5f5",
    "bg_surface_alt":    "#fafafa",
    "bg_elevated":       "#eeeeee",
    "bg_pressed":        "#e8e8e8",
    "bg_card_alt":       "#f0f0f0",
    # Text
    "text_primary":      "#111111",
    "text_secondary":    "#444444",
    "text_muted":        "#888888",
    "text_dim":          "#666666",
    "text_placeholder":  "#999999",
    "text_inverse":      "#ffffff",
    # Borders & hover
    "border":            "#dddddd",
    "border_strong":     "#cccccc",
    "hover":             "#e8e8e8",
    "hover_strong":      "#dddddd",
    # Accents — red kept identical; greens darkened for contrast on white
    "accent_red":        "#ff3b30",
    "accent_green":      "#00a37e",
    "accent_green_hi":   "#00b894",
    "accent_green_lo":   "#007a5c",
    "accent_green_alt":  "#008c6a",
    "accent_cyan":       "#00b894",
    "accent_mint":       "#00b894",
    "accent_mint_hover": "#00a37e",
    "accent_neutral":         "#b3b3b3",
    "accent_neutral_hover":   "#c6c6c6",
    "accent_neutral_text":    "#000000",
    # Calendar
    "calendar_today_bg":      "#dddddd",
    "calendar_today_fg":      "#111111",
    "calendar_completed_bg":  "#a8e6cf",
    "calendar_completed_fg":  "#0a3a2a",
}


def _palette_for(name: str) -> Dict[str, str]:
    """Resolve a palette name; default to dark on anything unknown."""
    return LIGHT_PALETTE if name == "light" else DARK_PALETTE


def current_palette() -> Dict[str, str]:
    """Palette currently selected in user settings."""
    from core.config import get_settings
    return _palette_for(get_settings().appearance.theme)


def apply_theme(name: str) -> None:
    """Apply the named theme to the running QApplication.

    Re-styles every existing top-level widget; no restart required.
    Safe to call before MainWindow exists.
    """
    app = QApplication.instance()
    if app is None:
        return
    app.setStyleSheet(_build_global_qss(_palette_for(name)))


# ---------------------------------------------------------------------------
# Global QSS
# ---------------------------------------------------------------------------

def _build_global_qss(p: Dict[str, str]) -> str:
    return f"""
    /* =====================================================================
       App-level surfaces
       ===================================================================== */
    QMainWindow {{
        background-color: {p['bg_app']};
    }}
    QDialog {{
        background-color: {p['bg_surface_alt']};
    }}

    /* =====================================================================
       Sidebar (main window)
       ===================================================================== */
    QWidget#Sidebar {{
        background-color: {p['bg_surface']};
    }}
    QLabel#SidebarTitle {{
        color: {p['accent_red']};
        font-weight: 700;
        font-size: 24px;
    }}
    QLabel#SectionLabel {{
        color: {p['accent_cyan']};
        font-weight: 600;
        font-size: 16px;
    }}
    QPushButton#NavButton {{
        background-color: {p['accent_red']};
        color: {p['text_primary']};
        font-weight: 600;
        padding: 10px;
        border: none;
    }}
    QPushButton#FreeButton {{
        background-color: {p['accent_green']};
        color: {p['text_inverse']};
        font-weight: 600;
        padding: 10px;
        border: none;
    }}
    QPushButton#RandomButton {{
        background-color: {p['accent_red']};
        color: {p['text_inverse']};
        font-weight: 600;
        padding: 10px;
        border: none;
    }}
    QPushButton#SettingsButton {{
        background-color: {p['bg_pressed']};
        color: {p['text_muted']};
        font-weight: 500;
        padding: 10px;
        border: 1px solid {p['border']};
        border-radius: 4px;
        text-align: left;
    }}
    QPushButton#SettingsButton:hover {{
        background-color: {p['hover']};
        color: {p['text_primary']};
        border-color: {p['border_strong']};
    }}

    /* =====================================================================
       Header
       ===================================================================== */
    QLabel#HeaderTitle {{
        color: {p['text_primary']};
        font-weight: 700;
        font-size: 28px;
    }}
    QLabel#StreakLabel {{
        color: {p['text_primary']};
        font-weight: 600;
        font-size: 16px;
    }}

    /* =====================================================================
       Session view (writing editor)
       ===================================================================== */
    QLineEdit#SessionTitle {{
        font-size: 24px;
        font-weight: 600;
        color: {p['text_placeholder']};
        background-color: transparent;
        border: none;
    }}
    QTextEdit#WritingEditor {{
        background-color: {p['bg_surface_alt']};
        color: {p['text_primary']};
        border: none;
        padding: 8px;
    }}
    QPushButton#FinishButton {{
        background-color: {p['accent_green']};
        color: {p['text_inverse']};
        font-weight: 600;
        padding: 8px 16px;
        border: none;
    }}
    QLabel#PromptTitle {{
        color: {p['accent_red']};
        font-weight: 700;
        font-size: 20px;
    }}
    QLabel#PromptBody {{
        color: {p['text_primary']};
        font-size: 18px;
    }}
    QLabel#PromptTags {{
        color: {p['text_secondary']};
        font-size: 13px;
    }}
    QLabel#TimeLabel {{
        color: {p['text_primary']};
        font-weight: 600;
    }}
    QLabel#WordsLabel {{
        color: {p['accent_green']};
        font-weight: 600;
    }}

    /* =====================================================================
       Menu bar / menus
       ===================================================================== */
    QMenuBar {{
        background-color: {p['bg_surface']};
        color: {p['text_primary']};
    }}
    QMenuBar::item {{
        background-color: transparent;
        padding: 4px 8px;
    }}
    QMenuBar::item:selected {{
        background-color: {p['hover']};
    }}
    QMenu {{
        background-color: {p['bg_elevated']};
        color: {p['text_primary']};
        border: 1px solid {p['border']};
    }}
    QMenu::item {{
        padding: 6px 24px;
    }}
    QMenu::item:selected {{
        background-color: {p['hover_strong']};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {p['border']};
        margin: 4px 0;
    }}

    /* =====================================================================
       Calendar view
       ===================================================================== */
    QCalendarWidget#WritingCalendar {{
        background-color: {p['bg_surface']};
        color: {p['text_primary']};
        border: none;
    }}
    QCalendarWidget#WritingCalendar QAbstractItemView:enabled {{
        background-color: {p['bg_surface']};
        color: {p['text_primary']};
        selection-background-color: {p['hover']};
        selection-color: {p['text_primary']};
        outline: none;
    }}
    QCalendarWidget#WritingCalendar QWidget#qt_calendar_navigationbar {{
        background-color: {p['bg_surface']};
    }}
    QCalendarWidget#WritingCalendar QToolButton {{
        color: {p['text_primary']};
        font-weight: 600;
        background: transparent;
        border: none;
    }}
    QCalendarWidget#WritingCalendar QToolButton::menu-indicator {{
        image: none;
    }}

    /* =====================================================================
       History view
       ===================================================================== */
    QWidget#HistoryViewRoot {{
        background-color: {p['bg_app']};
    }}
    QWidget#HistoryInner {{
        background-color: {p['bg_app']};
    }}
    QScrollArea#HistoryScrollArea {{
        background: transparent;
        border: none;
    }}
    QLabel#EmptyHistoryLabel {{
        font-size: 14px;
        color: {p['text_muted']};
    }}
    QLabel#ResultsLabel {{
        font-size: 13px;
        color: {p['text_muted']};
    }}
    QLineEdit#SearchInput {{
        background-color: {p['bg_surface_alt']};
        color: {p['text_primary']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        padding: 8px 12px;
        font-size: 14px;
    }}
    QLineEdit#SearchInput:focus {{
        border-color: {p['accent_green']};
    }}
    QComboBox#ModeFilter, QComboBox#SortCombo {{
        background-color: {p['bg_surface_alt']};
        color: {p['text_primary']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        padding: 6px 12px;
        min-width: 120px;
    }}
    QComboBox#ModeFilter::drop-down, QComboBox#SortCombo::drop-down {{
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p['bg_surface_alt']};
        color: {p['text_primary']};
        selection-background-color: {p['hover']};
    }}
    QSpinBox#WordsFilter {{
        background-color: {p['bg_surface_alt']};
        color: {p['text_primary']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        padding: 6px;
        min-width: 80px;
    }}
    QLabel#FilterLabel {{
        color: {p['text_muted']};
        font-size: 13px;
    }}
    QPushButton#ClearButton {{
        background-color: {p['hover']};
        color: {p['text_primary']};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
    }}
    QPushButton#ClearButton:hover {{
        background-color: {p['hover_strong']};
    }}
    QWidget#SessionCard {{
        background-color: {p['bg_app']};
    }}
    QLabel#SessionTitle {{
        font-size: 20px;
        font-weight: 700;
        color: {p['text_primary']};
    }}
    QLabel#SessionDate {{
        font-size: 13px;
        color: {p['text_muted']};
    }}
    QLabel#SessionSnippet {{
        font-size: 13px;
        color: {p['text_secondary']};
        font-style: italic;
    }}
    QLabel#SessionModeBadge {{
        background-color: {p['hover']};
        color: {p['text_primary']};
        font-size: 11px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 3px;
    }}
    QFrame#HistoryDivider {{
        background-color: {p['border']};
        max-height: 1px;
        min-height: 1px;
    }}

    /* =====================================================================
       Stats view
       ===================================================================== */
    QWidget#StatsView {{
        background-color: {p['bg_app']};
    }}
    QWidget#StatsContent {{
        background-color: {p['bg_app']};
    }}
    QScrollArea#StatsScrollArea {{
        background: transparent;
        border: none;
    }}
    QWidget#StatsView QLabel#SectionTitle {{
        color: {p['accent_green']};
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    QFrame#StatCard, QFrame#GoalCard {{
        background-color: {p['bg_surface_alt']};
        border-radius: 8px;
        min-width: 150px;
    }}
    QFrame#GoalCard {{
        max-width: 400px;
    }}
    QLabel#StatCardTitle {{
        color: {p['text_muted']};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
    }}
    QLabel#StatCardValue {{
        color: {p['text_primary']};
        font-size: 28px;
        font-weight: 700;
    }}
    QLabel#StatCardSubtitle {{
        color: {p['text_dim']};
        font-size: 11px;
    }}
    QLabel#GoalWordsLabel {{
        color: {p['text_primary']};
        font-size: 20px;
        font-weight: 600;
    }}
    QProgressBar#GoalProgressBar {{
        background-color: {p['hover']};
        border: none;
        border-radius: 4px;
        height: 8px;
    }}
    QProgressBar#GoalProgressBar::chunk {{
        background-color: {p['accent_green']};
        border-radius: 4px;
    }}
    QLabel#GoalStreakLabel {{
        color: {p['accent_green']};
        font-size: 13px;
    }}
    QLabel#NoGoalLabel {{
        color: {p['text_dim']};
        font-size: 14px;
        font-style: italic;
    }}

    /* =====================================================================
       Settings dialog
       ===================================================================== */
    QDialog#SettingsDialog QTabWidget::pane {{
        border: 1px solid {p['border']};
        background-color: {p['bg_surface_alt']};
    }}
    QDialog#SettingsDialog QTabBar::tab {{
        background-color: {p['bg_pressed']};
        color: {p['text_secondary']};
        padding: 8px 16px;
        border: 1px solid {p['border']};
        border-bottom: none;
    }}
    QDialog#SettingsDialog QTabBar::tab:selected {{
        background-color: {p['bg_surface_alt']};
        color: {p['text_primary']};
    }}
    QDialog#SettingsDialog QGroupBox {{
        color: {p['text_primary']};
        font-weight: bold;
        border: 1px solid {p['border']};
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 8px;
    }}
    QDialog#SettingsDialog QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }}
    QDialog#SettingsDialog QLabel {{
        color: {p['text_secondary']};
    }}
    QDialog#SettingsDialog QLineEdit,
    QDialog#SettingsDialog QSpinBox,
    QDialog#SettingsDialog QDoubleSpinBox,
    QDialog#SettingsDialog QComboBox {{
        background-color: {p['bg_pressed']};
        color: {p['text_primary']};
        border: 1px solid {p['border_strong']};
        border-radius: 4px;
        padding: 4px 8px;
        min-height: 24px;
    }}
    QDialog#SettingsDialog QCheckBox {{
        color: {p['text_secondary']};
    }}
    QDialog#SettingsDialog QPushButton {{
        background-color: {p['hover']};
        color: {p['text_primary']};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        min-width: 80px;
    }}
    QDialog#SettingsDialog QPushButton:hover {{
        background-color: {p['hover_strong']};
    }}
    QDialog#SettingsDialog QPushButton:default {{
        background-color: {p['accent_green']};
        color: {p['text_inverse']};
    }}
    QDialog#SettingsDialog QPushButton:default:hover {{
        background-color: {p['accent_green_hi']};
    }}
    QLabel#SettingsHint {{
        color: {p['text_muted']};
        font-size: 13px;
    }}

    /* =====================================================================
       Tag selector dialog
       ===================================================================== */
    QDialog#TagSelectorDialog {{
        background-color: {p['bg_app']};
    }}
    QWidget#CardsContainer {{
        background-color: {p['bg_app']};
    }}
    QDialog#TagSelectorDialog QScrollArea {{
        background: transparent;
        border: none;
    }}
    QDialog#TagSelectorDialog QLabel#DialogTitle {{
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 1px;
        color: {p['accent_red']};
    }}
    QWidget#DialogUnderline {{
        background-color: {p['text_primary']};
    }}
    QDialog#TagSelectorDialog QLabel#DialogSubtitle {{
        font-size: 14px;
        font-weight: 600;
        margin-top: 8px;
        margin-bottom: 4px;
        color: {p['text_primary']};
    }}
    QWidget#LayerCard {{
        background-color: {p['bg_surface_alt']};
        border: 1px solid {p['border']};
        border-radius: 6px;
    }}
    QLabel#LayerHeader {{
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 1px;
        color: {p['text_primary']};
    }}
    QLabel#LayerDesc {{
        font-size: 12px;
        color: {p['text_muted']};
    }}
    QLabel#CategoryLabel {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: {p['text_secondary']};
        margin-top: 4px;
    }}
    QPushButton#StateButton {{
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 8px 12px;
        border: 1px solid {p['border']};
        background-color: {p['bg_app']};
        color: {p['text_primary']};
    }}
    QPushButton#StateButton:hover {{
        background-color: {p['hover']};
    }}
    QPushButton#StateButton:checked {{
        background-color: {p['bg_elevated']};
        color: {p['text_primary']};
        border-color: {p['border_strong']};
    }}
    QPushButton#TagButton {{
        font-size: 12px;
        font-weight: 600;
        padding: 5px 10px;
        border-radius: 4px;
        border: 1px solid {p['border']};
        background-color: {p['bg_app']};
        color: {p['text_primary']};
    }}
    QPushButton#TagButton:hover {{
        background-color: {p['hover']};
    }}
    QPushButton#TagButton:checked {{
        background-color: {p['bg_elevated']};
        color: {p['text_primary']};
        border-color: {p['border_strong']};
    }}
    QPushButton#SecondaryButton {{
        background-color: {p['accent_neutral']};
        color: {p['accent_neutral_text']};
        font-weight: 600;
        padding: 10px 24px;
        border: none;
    }}
    QPushButton#SecondaryButton:hover {{
        background-color: {p['accent_neutral_hover']};
    }}
    QPushButton#PrimaryButton {{
        background-color: {p['accent_mint']};
        color: {p['accent_neutral_text']};
        font-weight: 700;
        padding: 10px 28px;
        border: none;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {p['accent_mint_hover']};
    }}

    /* =====================================================================
       About dialog
       ===================================================================== */
    QDialog#AboutDialog {{
        background-color: {p['bg_surface_alt']};
    }}
    QDialog#AboutDialog QLabel#AppName {{
        color: {p['accent_green']};
        font-size: 28px;
        font-weight: 700;
    }}
    QDialog#AboutDialog QLabel#Version {{
        color: {p['text_muted']};
        font-size: 14px;
    }}
    QDialog#AboutDialog QFrame#Separator {{
        background-color: {p['border']};
        max-height: 1px;
    }}
    QDialog#AboutDialog QLabel#Description {{
        color: {p['text_secondary']};
        font-size: 14px;
    }}
    QDialog#AboutDialog QLabel#Credits {{
        color: {p['text_dim']};
        font-size: 12px;
    }}
    QDialog#AboutDialog QPushButton#CloseButton {{
        background-color: {p['accent_green']};
        color: {p['text_inverse']};
        border: none;
        border-radius: 6px;
        padding: 8px 24px;
        font-size: 14px;
        font-weight: 600;
    }}
    QDialog#AboutDialog QPushButton#CloseButton:hover {{
        background-color: {p['accent_green_alt']};
    }}
    QDialog#AboutDialog QPushButton#CloseButton:pressed {{
        background-color: {p['accent_green_lo']};
    }}

    /* =====================================================================
       Shortcuts dialog
       ===================================================================== */
    QDialog#ShortcutsDialog {{
        background-color: {p['bg_surface_alt']};
    }}
    QDialog#ShortcutsDialog QLabel#DialogTitle {{
        color: {p['text_primary']};
        font-size: 20px;
        font-weight: 700;
    }}
    QDialog#ShortcutsDialog QLabel#SectionTitle {{
        color: {p['accent_green']};
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        margin-top: 8px;
    }}
    QDialog#ShortcutsDialog QScrollArea#ShortcutsScroll {{
        background: transparent;
        border: none;
    }}
    QDialog#ShortcutsDialog QWidget#ShortcutsContent {{
        background-color: {p['bg_surface_alt']};
    }}
    QFrame#ShortcutRow {{
        background-color: {p['bg_card_alt']};
        border-radius: 4px;
    }}
    QLabel#ShortcutKey {{
        color: {p['accent_green']};
        font-size: 14px;
        font-weight: 600;
        font-family: monospace;
    }}
    QLabel#ShortcutDesc {{
        color: {p['text_secondary']};
        font-size: 14px;
    }}
    QDialog#ShortcutsDialog QPushButton#CloseButton {{
        background-color: {p['hover']};
        color: {p['text_primary']};
        border: none;
        border-radius: 6px;
        padding: 8px 24px;
        font-size: 14px;
        font-weight: 600;
    }}
    QDialog#ShortcutsDialog QPushButton#CloseButton:hover {{
        background-color: {p['hover_strong']};
    }}
    """
