# ui/session_view.py

from datetime import datetime

from PyQt6.QtGui import QTextBlockFormat, QTextCursor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QSizePolicy,
)

from core.session_manager import SessionManager
from core.models import WritingSession
from core.utils import mixed_word_count


class SessionView(QWidget):
    sessionFinished = pyqtSignal(WritingSession)
    sessionCancelled = pyqtSignal()
    titleChanged = pyqtSignal(str)

    def __init__(self, session_manager: SessionManager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self._current_session: WritingSession | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 1 second
        self._timer.timeout.connect(self._on_tick)

        self._build_ui()

    # ---------- UI layout ----------

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        self.setLayout(layout)

        # Top row: title (editable) + Finish button
        top_row = QHBoxLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("SESSION TITLE")
        self.title_edit.setObjectName("SessionTitle")
        self.title_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.finish_button = QPushButton("FINISH")
        self.finish_button.setObjectName("FinishButton")
        self.finish_button.setFixedWidth(120)

        top_row.addWidget(self.title_edit)
        top_row.addStretch()
        top_row.addWidget(self.finish_button)

        layout.addLayout(top_row)

        # Prompt area (only visible for random-topic sessions)
        self.prompt_title_label = QLabel("PROMPT:")
        self.prompt_title_label.setObjectName("PromptTitle")

        self.prompt_body_label = QLabel()
        self.prompt_body_label.setObjectName("PromptBody")
        self.prompt_body_label.setWordWrap(True)

        self.prompt_tags_label = QLabel()  # (optional, tags later)
        self.prompt_tags_label.setObjectName("PromptTags")

        self.prompt_container = QWidget()
        prompt_layout = QVBoxLayout()
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_layout.setSpacing(4)
        self.prompt_container.setLayout(prompt_layout)
        prompt_layout.addWidget(self.prompt_title_label)
        prompt_layout.addWidget(self.prompt_body_label)
        prompt_layout.addWidget(self.prompt_tags_label)

        layout.addWidget(self.prompt_container)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("START WRITING HERE...")
        self.editor.setObjectName("WritingEditor")
        layout.addWidget(self.editor, 1)

        # apply 1.5 line spacing
        self._apply_line_spacing()


        # Bottom row: timer + word count (right aligned)
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.time_label = QLabel("TIME: 00:00")
        self.time_label.setObjectName("TimeLabel")

        self.words_label = QLabel("WORDS: 0")
        self.words_label.setObjectName("WordsLabel")

        bottom_row.addWidget(self.time_label)
        bottom_row.addSpacing(16)
        bottom_row.addWidget(self.words_label)

        layout.addLayout(bottom_row)

        # Connections
        self.finish_button.clicked.connect(self._on_finish_clicked)
        self.editor.textChanged.connect(self._on_text_changed)
        self.title_edit.textChanged.connect(self._on_title_changed)

    # ---------- Session lifecycle ----------

    def start_new_session(self, mode: str, topic: str | None):
        """
        Called by MainWindow when the user chooses Free Writing or Random Topic.
        """
        # ask the manager to create a brand new session
        sess = self.session_manager.start_session(mode, topic)
        self._current_session = sess

        # set default title (date) into the editable field
        self.title_edit.setText(sess.title)

        # prompt visibility
        if mode == "random_topic" and topic:
            self.prompt_container.show()
            self.prompt_body_label.setText(topic)
            self.prompt_title_label.show()
        else:
            # free mode: hide prompt block
            self.prompt_container.hide()
            self.prompt_body_label.clear()

        # reset editor and counters
        self.editor.clear()
        self._apply_line_spacing()   # keep 1.5 spacing after clear
        self._update_word_count(0)
        self._update_time_label(0)

        # start timer
        self._timer.start()

    def _on_finish_clicked(self):
        if not self._current_session:
            self.sessionCancelled.emit()
            return

        # Ensure latest content + title are saved into session_manager
        self._push_content_to_manager()
        self._push_title_to_manager()

        sess = self.session_manager.finish_session()
        self._timer.stop()
        self._current_session = None

        if sess is not None:
            self.sessionFinished.emit(sess)
        else:
            self.sessionCancelled.emit()

    # ---------- Helpers ----------

    def _on_tick(self):
        if not self._current_session:
            self._update_time_label(0)
            return
        # compute elapsed from session start
        elapsed = int((datetime.now() - self._current_session.start_time).total_seconds())
        self._update_time_label(elapsed)

    def _on_text_changed(self):
        text = self.editor.toPlainText()
        self._update_word_count(mixed_word_count(text))
        self._push_content_to_manager()

    def _on_title_changed(self, text: str):
        if self._current_session:
            self._current_session.title = text
        self.titleChanged.emit(text)


    def get_current_title(self) -> str:
        text = self.title_edit.text().strip()
        if text:
            return text
        # fallback: use the date if empty
        if self._current_session:
            return self._current_session.session_date.isoformat()
        return "SESSION"


    def _push_content_to_manager(self):
        if self._current_session is None:
            return
        self._current_session.content = self.editor.toPlainText()
        # if your SessionManager has a method like update_content, you can call it here too:
        # self.session_manager.update_content(self._current_session.content)

    def _push_title_to_manager(self):
        if self._current_session is None:
            return
        self._current_session.title = self.title_edit.text().strip() or self._current_session.session_date.isoformat()

    def _update_time_label(self, seconds: int):
        m = seconds // 60
        s = seconds % 60
        self.time_label.setText(f"TIME: {m:02d}:{s:02d}")

    def _update_word_count(self, count: int):
        self.words_label.setText(f"WORDS: {count}")

    def _apply_line_spacing(self):
        """Set writing editor line spacing to 1.5x."""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)

        block_fmt = QTextBlockFormat()
        # 150% line height, cast enum to int to satisfy the type checker
        block_fmt.setLineHeight(150, 0)

        cursor.setBlockFormat(block_fmt)
        cursor.clearSelection()
        self.editor.setTextCursor(cursor)

