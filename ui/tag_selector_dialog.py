# ui/tag_selector_dialog.py

import random
from typing import List, Dict

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
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

    User-visible categories:
      - GENRE: individual tags (e.g., Detective, Fantasy, Slice of Life)
      - MOOD: one large checkbox → picks one random mood tag internally
      - EVENT: one large checkbox → picks one random event tag internally
      - ITEM: one large checkbox → picks one random item tag internally
      - SKILL: one large checkbox → picks one random skill tag internally
      - FORM: individual tags (Sentence / Paragraph)

    The concrete elements (phrases) inside each Tag remain invisible to the user.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose style and form for your prompt")
        self.resize(420, 520)

        layout = QVBoxLayout(self)

        # ----- Scroll area for content -----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        scroll.setWidget(inner)
        inner_layout = QVBoxLayout(inner)

        # individual checkboxes for genre + form tags
        self.checkboxes: Dict[str, QCheckBox] = {}

        # big-category checkboxes with internal tag lists
        self._mood_tags:   List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "mood"]
        self._event_tags:  List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "event"]
        self._item_tags:   List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "item"]
        self._skill_tags:  List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "skill"]

        self._mood_checkbox:  QCheckBox | None = None
        self._event_checkbox: QCheckBox | None = None
        self._item_checkbox:  QCheckBox | None = None
        self._skill_checkbox: QCheckBox | None = None

        # group tags for GENRE and FORM (shown individually)
        genres: List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "genre"]
        forms:  List[Tag] = [t for t in TAG_REGISTRY.values() if t.category == "form"]

        # helper: add a block of individual checkboxes
        def add_category_block(title: str, tags: List[Tag]):
            if not tags:
                return
            title_label = QLabel(title.upper())
            inner_layout.addWidget(title_label)
            for t in sorted(tags, key=lambda x: x.label):
                cb = QCheckBox(t.label)
                cb.setToolTip(t.description)
                inner_layout.addWidget(cb)
                self.checkboxes[t.id] = cb
            inner_layout.addSpacing(8)

        # ----- GENRE block (individual) -----
        add_category_block("Genre", genres)

        # ----- MOOD block (single checkbox, random mood) -----
        if self._mood_tags:
            mood_label = QLabel("MOOD")
            inner_layout.addWidget(mood_label)

            self._mood_checkbox = QCheckBox("Use a random mood emphasis")
            self._mood_checkbox.setToolTip(
                "If checked, a mood (e.g., calm, eerie, bittersweet) is chosen randomly "
                "to influence the prompt. The exact mood label is not shown."
            )
            inner_layout.addWidget(self._mood_checkbox)
            inner_layout.addSpacing(8)

        # ----- EVENT block (single checkbox, random event) -----
        if self._event_tags:
            event_label = QLabel("EVENT")
            inner_layout.addWidget(event_label)

            self._event_checkbox = QCheckBox("Use a random central event")
            self._event_checkbox.setToolTip(
                "If checked, a type of event (e.g., confrontation, discovery, reunion) "
                "is chosen randomly to shape the situation in the prompt."
            )
            inner_layout.addWidget(self._event_checkbox)
            inner_layout.addSpacing(8)

        # ----- ITEM block (single checkbox, random item) -----
        if self._item_tags:
            item_label = QLabel("ITEM")
            inner_layout.addWidget(item_label)

            self._item_checkbox = QCheckBox("Use a random important object")
            self._item_checkbox.setToolTip(
                "If checked, some object (e.g., photograph, letter, broken watch) is "
                "chosen randomly to act as a subtle focus in the prompt."
            )
            inner_layout.addWidget(self._item_checkbox)
            inner_layout.addSpacing(8)

        # ----- SKILL block (single checkbox, random skill focus) -----
        if self._skill_tags:
            skill_label = QLabel("SKILL")
            inner_layout.addWidget(skill_label)

            self._skill_checkbox = QCheckBox("Use a random writing focus")
            self._skill_checkbox.setToolTip(
                "If checked, a writing focus (e.g., dialogue-heavy, internal monologue, "
                "detailed setting) is chosen randomly to influence the style."
            )
            inner_layout.addWidget(self._skill_checkbox)
            inner_layout.addSpacing(8)

        # ----- FORM block (individual: sentence / paragraph) -----
        add_category_block("Form", forms)

        inner_layout.addStretch()
        layout.addWidget(scroll)

        # ----- Dialog buttons -----
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_tags(self) -> List[str]:
        """
        Return selected tag IDs.

        - GENRE + FORM: return IDs for each checked individual tag.
        - MOOD/EVENT/ITEM/SKILL: if their single checkbox is checked, pick one
          concrete tag at random from the corresponding list and add its ID.
        """
        selected: List[str] = [
            tid for tid, cb in self.checkboxes.items() if cb.isChecked()
        ]

        # handle MOOD
        if self._mood_checkbox and self._mood_checkbox.isChecked() and self._mood_tags:
            mood_tag = random.choice(self._mood_tags)
            selected.append(mood_tag.id)

        # handle EVENT
        if self._event_checkbox and self._event_checkbox.isChecked() and self._event_tags:
            event_tag = random.choice(self._event_tags)
            selected.append(event_tag.id)

        # handle ITEM
        if self._item_checkbox and self._item_checkbox.isChecked() and self._item_tags:
            item_tag = random.choice(self._item_tags)
            selected.append(item_tag.id)

        # handle SKILL
        if self._skill_checkbox and self._skill_checkbox.isChecked() and self._skill_tags:
            skill_tag = random.choice(self._skill_tags)
            selected.append(skill_tag.id)

        return selected
