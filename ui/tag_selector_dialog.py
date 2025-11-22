# ui/tag_selector_dialog.py

import random
from typing import List, Dict

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSizePolicy

from core.tags import TAG_REGISTRY, Tag


class TagSelectorDialog(QDialog):
    """
    Tag selector dialog.

    - GENRE: individual toggle buttons (one per genre tag)
    - SKILL: single toggle button; when enabled, a random skill tag is chosen
    - FORM: individual toggle buttons (sentence / paragraph tags)
    - OTHER: three toggle buttons, for
        * random mood tag
        * random event tag
        * random item tag

    Internal concrete tags (elements) remain hidden and are chosen at random
    when the corresponding button is active.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate a random topic")
        self.resize(520, 540)

        # ----- group tags by category -----
        genres: List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "genre"]
        forms: List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "form"]

        self._mood_tags: List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "mood"]
        self._event_tags: List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "event"]
        self._item_tags: List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "item"]
        self._skill_tags: List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "skill"]

        # buttons for individual tag ids (genres + forms)
        self.tag_buttons: Dict[str, QPushButton] = {}

        # big toggle buttons for random categories
        self.skill_button: QPushButton | None = None
        self.mood_button: QPushButton | None = None
        self.event_button: QPushButton | None = None
        self.item_button: QPushButton | None = None

        # ----- layout -----
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(16)

        # Header title
        title_label = QLabel("GENERATE A RANDOM TOPIC")
        title_label.setObjectName("DialogTitle")
        main_layout.addWidget(title_label)

        # underline
        line = QWidget()
        line.setFixedHeight(2)
        line.setObjectName("DialogUnderline")
        main_layout.addWidget(line)

        # subtitle
        subtitle = QLabel("SELECT TAGS TO DEFINE YOUR PROMPT'S FOCUS:")
        subtitle.setObjectName("DialogSubtitle")
        main_layout.addWidget(subtitle)

        # Scroll area for sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        center = QWidget()
        center.setObjectName("TagPanel")   # <-- add this line
        scroll.setWidget(center)
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 8, 0, 8)
        center_layout.setSpacing(18)


        # helpers
        def add_category_label(text: str):
            lbl = QLabel(text.upper())
            lbl.setObjectName("CategoryLabel")
            center_layout.addWidget(lbl)

        def add_chip_row(tags: List[Tag]):
            """Row of small toggle buttons for individual tags."""
            if not tags:
                return
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(14)

            for t in sorted(tags, key=lambda x: x.label):
                btn = QPushButton(t.label)
                btn.setCheckable(True)
                btn.setObjectName("TagButton")
                btn.setToolTip(t.description)
                row_layout.addWidget(btn)
                self.tag_buttons[t.id] = btn

            row_layout.addStretch()
            center_layout.addWidget(row)

        def add_big_toggle(text: str) -> QPushButton:
            """A wide toggle button for aggregated random categories."""
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("BigToggleButton")
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )
            center_layout.addWidget(btn)
            return btn

        # GENRE section (individual tag buttons)
        add_category_label("Genre")
        add_chip_row(genres)

        # SKILL section (single aggregate toggle)
        if self._skill_tags:
            add_category_label("Skill")
            self.skill_button = add_big_toggle("Include a random writing focus")

        # FORM section (sentence / paragraph)
        add_category_label("Form")
        add_chip_row(forms)

        # OTHER section (Mood / Event / Item)
        if self._mood_tags or self._event_tags or self._item_tags:
            add_category_label("Other")

        if self._mood_tags:
            self.mood_button = add_big_toggle("Include a random mood emphasis")

        if self._event_tags:
            self.event_button = add_big_toggle("Include a random central event")

        if self._item_tags:
            self.item_button = add_big_toggle("Include a random important object")

        center_layout.addStretch()
        main_layout.addWidget(scroll, 1)

        # bottom buttons: Cancel / Generate
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

        self._apply_style()

    # ----- public API -----

    def selected_tags(self) -> List[str]:
        """
        Return selected tag IDs.

        - Genre/Form: IDs for each button that is checked.
        - Skill: if button checked, choose one random skill tag ID.
        - Other (mood/event/item): if button checked, choose one random tag
          from that category.
        """
        selected: List[str] = [
            tid for tid, btn in self.tag_buttons.items() if btn.isChecked()
        ]

        # skill
        if self.skill_button and self.skill_button.isChecked() and self._skill_tags:
            selected.append(random.choice(self._skill_tags).id)

        # mood
        if self.mood_button and self.mood_button.isChecked() and self._mood_tags:
            selected.append(random.choice(self._mood_tags).id)

        # event
        if self.event_button and self.event_button.isChecked() and self._event_tags:
            selected.append(random.choice(self._event_tags).id)

        # item
        if self.item_button and self.item_button.isChecked() and self._item_tags:
            selected.append(random.choice(self._item_tags).id)

        return selected

    # ----- styling -----

    def _apply_style(self):
        """Dialog-local stylesheet: buttons instead of checkboxes."""
        self.setStyleSheet("""
        QDialog {
            background-color: #ffffff;
        }

        QWidget#TagPanel {
            background-color: #ffffff;
            border: none;
        }

        QScrollArea {
            background: transparent;
            border: none;
        }

        QLabel#DialogTitle {
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1px;
            color: #ff3b30;
        }
        QWidget#DialogUnderline {
            background-color: #000000;
        }
        QLabel#DialogSubtitle {
            font-size: 14px;
            font-weight: 600;
            margin-top: 8px;
            margin-bottom: 8px;
            color: #111111;
        }
        QLabel#CategoryLabel {
            font-size: 14px;
            font-weight: 700;
            margin-top: 16px;
            margin-bottom: 4px;
            color: #111111;   /* if you keep the dark outer rect; change to #111111 if you drop it */
        }

        /* small “chip” buttons (Genre / Form) */
        QPushButton#TagButton {
            font-size: 14px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 4px;
            border: 1px solid transparent;
            background-color: transparent;
            color: #000000;              /* normal text black */
        }
        QPushButton#TagButton:hover {
            border-color: #cccccc;
        }
        QPushButton#TagButton:checked {
            background-color: #111111;
            color: #ffffff;              /* active = dark bg + white text */
        }

        /* big toggle buttons (Skill / Other) */
        QPushButton#BigToggleButton {
            font-size: 13px;
            font-weight: 500;
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid #dddddd;
            background-color: #f5f5f5;
            text-align: left;
            color: #000000;              /* normal text black */
        }
        QPushButton#BigToggleButton:hover {
            background-color: #eaeaea;
        }
        QPushButton#BigToggleButton:checked {
            background-color: #111111;
            color: #ffffff;
            border-color: #111111;
        }

        QPushButton#SecondaryButton {
            background-color: #b3b3b3;
            color: #000000;
            font-weight: 600;
            padding: 10px 24px;
            border: none;
        }
        QPushButton#SecondaryButton:hover {
            background-color: #c6c6c6;
        }

        QPushButton#PrimaryButton {
            background-color: #6ee7c8;
            color: #000000;
            font-weight: 700;
            padding: 10px 28px;
            border: none;
        }
        QPushButton#PrimaryButton:hover {
            background-color: #5fd7b8;
        }
        """)
