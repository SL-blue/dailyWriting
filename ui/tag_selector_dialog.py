"""
Layer-based tag selector dialog.

Four cards (Territory, Emotional Weather, Craft, Seed). Each card has a
tri-state control — Off / Random / Specified — and reveals a tag picker
when Specified is active. Produces a `layer_state` dict consumable by
`core.prompt_builder.build_topic_instruction`.
"""

from __future__ import annotations

from typing import Dict, List

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.tags import (
    LAYER_CATEGORIES,
    LAYER_LABELS,
    LAYERS,
    Tag,
    tags_in_category,
)


_LAYER_DESCRIPTIONS: Dict[str, str] = {
    "territory": "What world are we in? Genre and tonal register.",
    "emotional_weather": "What does the scene feel like? Mood and tension.",
    "craft": "How is it written? Structural and stylistic constraints.",
    "seed": "What's the spark? Situation and role-based seeds.",
}


_CATEGORY_LABELS: Dict[str, str] = {
    "genre": "Genre",
    "register": "Register",
    "mood": "Mood",
    "tension": "Tension",
    "perspective": "Perspective",
    "temporal_stance": "Temporal stance",
    "structural_move": "Structural move",
    "form": "Form",
    "situation": "Situation",
    "object_role": "Object role",
    "setting_role": "Setting role",
    "time_role": "Time role",
}


# Default state per spec: Seed → Random, others → Off.
_DEFAULT_LAYER_STATE: Dict[str, str] = {
    "territory": "off",
    "emotional_weather": "off",
    "craft": "off",
    "seed": "random",
}


# ---------------------------------------------------------------------------
# FlowLayout — wraps chip buttons across multiple rows.
# Standard Qt FlowLayout pattern, ported to PyQt6.
# ---------------------------------------------------------------------------

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin: int = 0, spacing: int = 8):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + spacing
            if next_x - spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                next_x = x + hint.width() + spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_height = max(line_height, hint.height())
        return y + line_height - rect.y()


# ---------------------------------------------------------------------------
# LayerCard — controls + picker for a single layer.
# ---------------------------------------------------------------------------

class LayerCard(QWidget):
    def __init__(self, layer: str, default_state: str = "off", parent=None):
        super().__init__(parent)
        self.layer = layer
        self.setObjectName("LayerCard")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        header = QLabel(LAYER_LABELS[layer].upper())
        header.setObjectName("LayerHeader")
        outer.addWidget(header)

        desc = QLabel(_LAYER_DESCRIPTIONS[layer])
        desc.setObjectName("LayerDesc")
        desc.setWordWrap(True)
        outer.addWidget(desc)

        # Tri-state segmented control
        seg_row = QHBoxLayout()
        seg_row.setContentsMargins(0, 0, 0, 0)
        seg_row.setSpacing(0)

        self._state_buttons: Dict[str, QPushButton] = {}
        self._state_group = QButtonGroup(self)
        self._state_group.setExclusive(True)

        for caption, key in (("OFF", "off"), ("RANDOM", "random"), ("PICK", "specified")):
            b = QPushButton(caption)
            b.setCheckable(True)
            b.setObjectName("StateButton")
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self._state_buttons[key] = b
            self._state_group.addButton(b)
            seg_row.addWidget(b)

        outer.addLayout(seg_row)

        # Picker (visible only in "specified" state)
        self._picker = QWidget()
        self._picker.setObjectName("PickerArea")
        picker_layout = QVBoxLayout(self._picker)
        picker_layout.setContentsMargins(0, 6, 0, 0)
        picker_layout.setSpacing(10)

        self._tag_buttons: Dict[str, QPushButton] = {}
        for cat in LAYER_CATEGORIES[layer]:
            cat_label = QLabel(_CATEGORY_LABELS.get(cat, cat).upper())
            cat_label.setObjectName("CategoryLabel")
            picker_layout.addWidget(cat_label)

            chips_wrap = QWidget()
            flow = FlowLayout(chips_wrap, margin=0, spacing=8)
            for tag in sorted(tags_in_category(cat), key=lambda t: t.label):
                btn = self._make_chip(tag)
                self._tag_buttons[tag.id] = btn
                flow.addWidget(btn)
            picker_layout.addWidget(chips_wrap)

        outer.addWidget(self._picker)

        for btn in self._state_buttons.values():
            btn.toggled.connect(self._update_picker_visibility)

        self._state_buttons[default_state].setChecked(True)
        self._update_picker_visibility()

    def _make_chip(self, tag: Tag) -> QPushButton:
        btn = QPushButton(tag.label)
        btn.setCheckable(True)
        btn.setObjectName("TagButton")
        return btn

    def _update_picker_visibility(self):
        self._picker.setVisible(self._state_buttons["specified"].isChecked())

    def current_state(self) -> str:
        for key, btn in self._state_buttons.items():
            if btn.isChecked():
                return key
        return "off"

    def layer_state(self) -> Dict[str, object]:
        state = self.current_state()
        if state == "specified":
            tag_ids = [tid for tid, btn in self._tag_buttons.items() if btn.isChecked()]
            return {"state": "specified", "tag_ids": tag_ids}
        return {"state": state}


# ---------------------------------------------------------------------------
# TagSelectorDialog
# ---------------------------------------------------------------------------

class TagSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TagSelectorDialog")
        self.setWindowTitle("Generate a random topic")
        self.resize(640, 720)

        self._cards: Dict[str, LayerCard] = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(16)

        title = QLabel("GENERATE A RANDOM TOPIC")
        title.setObjectName("DialogTitle")
        main_layout.addWidget(title)

        underline = QWidget()
        underline.setFixedHeight(2)
        underline.setObjectName("DialogUnderline")
        main_layout.addWidget(underline)

        subtitle = QLabel("CONFIGURE EACH LAYER:")
        subtitle.setObjectName("DialogSubtitle")
        main_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setObjectName("CardsContainer")
        cards_layout = QVBoxLayout(container)
        cards_layout.setContentsMargins(0, 8, 0, 8)
        cards_layout.setSpacing(14)

        for layer in LAYERS:
            card = LayerCard(layer, default_state=_DEFAULT_LAYER_STATE[layer])
            self._cards[layer] = card
            cards_layout.addWidget(card)

        cards_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)

        # Bottom buttons
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("GENERATE PROMPT")
        ok_btn.setObjectName("PrimaryButton")
        ok_btn.clicked.connect(self.accept)

        bottom_row.addWidget(cancel_btn, 0, Qt.AlignmentFlag.AlignLeft)
        bottom_row.addStretch()
        bottom_row.addWidget(ok_btn, 0, Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(bottom_row)

    def selected_layer_state(self) -> Dict[str, Dict[str, object]]:
        return {layer: card.layer_state() for layer, card in self._cards.items()}
