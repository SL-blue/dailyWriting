# ui/tag_selector_dialog.py

from typing import List

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QDialogButtonBox,
    QWidget,
    QScrollArea,
)

from core.tags import TAG_REGISTRY, Tag


class TagSelectorDialog(QDialog):
    """
    Tag selector dialog.

    Now: only show high-level, user-facing choices:
      - genre_* tags
      - form_* tags

    Other categories (mood/place/time/event/item/skill) are internal and
    not exposed in the UI.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose style and form for your prompt")
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        scroll.setWidget(inner)
        inner_layout = QVBoxLayout(inner)

        self.checkboxes: dict[str, QCheckBox] = {}

        # We only expose these categories to the user
        visible_categories = {"genre", "form"}

        # group tags by category
        tags_by_cat: dict[str, List[Tag]] = {}
        for t in TAG_REGISTRY.values():
            if t.category in visible_categories:
                tags_by_cat.setdefault(t.category, []).append(t)

        # Render genre + form checkboxes
        # You can order them explicitly: genre first, then form
        for cat in ["genre", "form"]:
            if cat not in tags_by_cat:
                continue

            cat_label = QLabel(cat.upper())
            inner_layout.addWidget(cat_label)

            for t in sorted(tags_by_cat[cat], key=lambda x: x.label):
                cb = QCheckBox(t.label)
                cb.setToolTip(t.description)
                inner_layout.addWidget(cb)
                self.checkboxes[t.id] = cb

        inner_layout.addStretch()
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_tags(self) -> List[str]:
        """Return selected tag IDs (only genres + form)."""
        return [tid for tid, cb in self.checkboxes.items() if cb.isChecked()]
