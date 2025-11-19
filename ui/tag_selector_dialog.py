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
    Simple dialog: list of tags grouped by category with checkboxes.
    Returns a list of selected tag IDs when accepted.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose tags for your prompt")
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        # Scroll area (for many tags)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        scroll.setWidget(inner)
        inner_layout = QVBoxLayout(inner)

        # group tags by category
        tags_by_cat: dict[str, List[Tag]] = {}
        for t in TAG_REGISTRY.values():
            tags_by_cat.setdefault(t.category, []).append(t)

        self.checkboxes: dict[str, QCheckBox] = {}

        for cat, tags in sorted(tags_by_cat.items()):
            cat_label = QLabel(cat.upper())
            inner_layout.addWidget(cat_label)

            for t in sorted(tags, key=lambda x: x.label):
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
        return [tid for tid, cb in self.checkboxes.items() if cb.isChecked()]
