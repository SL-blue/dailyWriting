# ui/main_window.py

from datetime import date

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QFrame,
    QDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from core.session_manager import SessionManager
from core.models import WritingSession
from core.storage import load_sessions_for_date, load_all_sessions
from core.streak_days import load_completed_days, compute_streaks_from_days
from core.stats import compute_streaks
from core.topic_generator import TopicGenerator
from ui.session_view import SessionView
from ui.calendar_view import CalendarView
from ui.session_list_dialog import SessionListDialog
from ui.history_view import HistoryView
from ui.tag_selector_dialog import TagSelectorDialog



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Daily Writing Trainer")
        self.resize(1100, 700)

        self.CALENDAR_HEADER = "WRITING CALENDAR"
        self.HISTORY_HEADER = "SESSION LIST"


        self.session_manager = SessionManager()
        self.topic_generator = TopicGenerator()

        # ----- central widget & root layout -----
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        central.setLayout(root_layout)

        # ===== LEFT SIDEBAR =====
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        sb_layout = QVBoxLayout()
        sb_layout.setContentsMargins(24, 24, 24, 24)
        sb_layout.setSpacing(16)
        sidebar.setLayout(sb_layout)

        # App title
        title_label = QLabel("THE\nDAILY\nWRITER")
        title_label.setObjectName("SidebarTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # align: bitwise operation
        sb_layout.addWidget(title_label)

        # Calendar / session list buttons
        calendar_btn = QPushButton("CALENDAR VIEW")
        calendar_btn.setObjectName("NavButton")
        sessions_list_btn = QPushButton("SESSION LIST")
        sessions_list_btn.setObjectName("NavButton")  # Set same style as calendar button(in styling part)

        sb_layout.addWidget(calendar_btn)
        sb_layout.addWidget(sessions_list_btn)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        sb_layout.addWidget(line)

        # "Start new session" label
        start_label = QLabel("START NEW\nSESSION")
        start_label.setObjectName("SectionLabel")
        sb_layout.addWidget(start_label)

        # Session buttons
        self.free_button = QPushButton("FREE WRITING")
        self.free_button.setObjectName("FreeButton")

        self.random_button = QPushButton("RANDOM TOPIC\n(AI)")
        self.random_button.setObjectName("RandomButton")

        sb_layout.addWidget(self.free_button)
        sb_layout.addWidget(self.random_button)

        sb_layout.addStretch()  # anchor content to top without manual spacers or pixel math

        # ===== RIGHT MAIN AREA =====
        main_area = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(16)
        main_area.setLayout(main_layout)


        # --- Header: title + streak ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        self.header_title = QLabel(self.CALENDAR_HEADER)
        self.header_title.setObjectName("HeaderTitle")

        self.streak_label = QLabel("STREAK: 0 DAYS")
        self.streak_label.setObjectName("StreakLabel")
        self.streak_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.streak_label)

        # --- Stacked pages (calendar, session, history) ---
        self.stacked = QStackedWidget()  # QStackedWidget allows showing one page at a time, allowing switching
        self.calendar_view = CalendarView()
        self.session_view = SessionView(self.session_manager)
        self.session_view.titleChanged.connect(self.on_session_title_changed)
        self.history_view = HistoryView()
        self.history_view.sessionsChanged.connect(self._on_sessions_changed)

        # define page indices
        self.PAGE_CALENDAR = 0
        self.PAGE_SESSION = 1
        self.PAGE_HISTORY = 2

        # add widgets in matching order
        self.stacked.addWidget(self.calendar_view)   # index 0
        self.stacked.addWidget(self.session_view)    # index 1
        self.stacked.addWidget(self.history_view)    # index 2

        # Add to main layout (header on top, pages below)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.stacked)


        # Put sidebar + main area into root layout
        root_layout.addWidget(sidebar)
        root_layout.addWidget(main_area, 1)  # stretch = 1, main_area expand and sidebar stay fixed width

        # ----- Connections -----
        self.free_button.clicked.connect(self.start_free_writing)
        self.random_button.clicked.connect(self.start_random_topic)

        calendar_btn.clicked.connect(self.show_calendar)
        sessions_list_btn.clicked.connect(self.show_history)

        self.session_view.sessionFinished.connect(self.on_session_finished)
        self.session_view.sessionCancelled.connect(self.on_session_cancelled)

        # when a date is clicked in the calendar, open the session list dialog
        self.calendar_view.dateClicked.connect(self.on_calendar_date_clicked)

        # when sessions are changed (deleted) from history view
        self.history_view.sessionsChanged.connect(self._on_sessions_changed)

        self.show_calendar()
        self._apply_basic_style()

    # ----- Navigation helpers -----
    def show_calendar(self):
        self.calendar_view.refresh_month()
        self._update_streak_label()
        self.header_title.setText(self.CALENDAR_HEADER)
        self.streak_label.show()
        self.stacked.setCurrentIndex(self.PAGE_CALENDAR)

    def show_session(self):
        # writing page: header = session title, streak hidden
        self.header_title.setText(self.session_view.get_current_title())
        self.streak_label.hide()
        self.stacked.setCurrentIndex(self.PAGE_SESSION)

    def show_history(self):
        self.history_view.refresh()
        self.header_title.setText(self.HISTORY_HEADER)
        self.streak_label.show()
        self._update_streak_label()
        self.stacked.setCurrentIndex(self.PAGE_HISTORY)



    # ----- Session handlers -----
    def start_free_writing(self):
        self.session_view.start_new_session(mode="free", topic=None)
        self.show_session()

    def start_random_topic(self):

        dlg = TagSelectorDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:  # ? What does exec() do here?
            return

        tag_ids = dlg.selected_tags()
        topic = self.topic_generator.generate_topic(tag_ids)

        # Connect to local backup if Gemini fails
        if self.topic_generator.last_used_fallback:
            QMessageBox.information(
                self,
                "AI temporarily unavailable",
                "Gemini was overloaded or unreachable, so a local backup prompt was used instead."
            )

        self.session_view.start_new_session(mode="random_topic", topic=topic)
        self.show_session()


    def on_session_title_changed(self, title: str):
        """Keep header title in sync with the writing session title."""
        if self.stacked.currentIndex() == self.PAGE_SESSION:
            # if title is empty, SessionView.get_current_title() will fall back
            self.header_title.setText(self.session_view.get_current_title())

    def on_session_finished(self, session: WritingSession):
        print(f"MainWindow: Session finished with id={session.id}")
        # later: update streak, etc.
        self.show_calendar()

    def on_session_cancelled(self):
        print("MainWindow: Session cancelled.")
        self.show_calendar()

    def _on_sessions_changed(self):
        """Called when sessions are deleted from the history view."""
        # refresh calendar highlights + streak info
        self.calendar_view.refresh_month()
        self._update_streak_label()

    def on_calendar_date_clicked(self, day: date):
        """Open a dialog listing all sessions on the clicked day."""
        from core.storage import load_sessions_for_date

        sessions = load_sessions_for_date(day)
        if not sessions:
            return

        dlg = SessionListDialog(day, self)
        dlg.exec()

        # After dialog closes, refresh calendar + streak
        self.calendar_view.refresh_month()
        self._update_streak_label()


    def _update_streak_label(self):
        """Recompute streak from completed-days log and update the label."""
        days = load_completed_days()
        current, longest, total = compute_streaks_from_days(days)
        self.streak_label.setText(
            f"STREAK: {current} DAYS\nLONGEST: {longest} DAYS\nTOTAL DAYS: {total}"
        )



    # ----- Basic styling to get close to your mock -----
    def _apply_basic_style(self):
        self.setStyleSheet("""
        QMainWindow {
            background-color: #000000;
        }
        QWidget#Sidebar {
            background-color: #111111;
        }
        QLabel#SidebarTitle {
            color: #ff3b30;
            font-weight: 700;
            font-size: 24px;
        }
        QLabel#SectionLabel {
            color: #00d0a0;
            font-weight: 600;
            font-size: 16px;
        }
        QPushButton#NavButton {
            background-color: #ff3b30;
            color: white;
            font-weight: 600;
            padding: 10px;
            border: none;
        }
        QPushButton#FreeButton {
            background-color: #00b894;
            color: black;
            font-weight: 600;
            padding: 10px;
            border: none;
        }
        QPushButton#RandomButton {
            background-color: #ff3b30;
            color: black;
            font-weight: 600;
            padding: 10px;
            border: none;
        }
        QLabel#HeaderTitle {
            color: #ffffff;
            font-weight: 700;
            font-size: 28px;
        }
        QLabel#StreakLabel {
            color: #ffffff;
            font-weight: 600;
            font-size: 16px;
        }
        QPushButton#FinishButton {
            background-color: #00b894;
            color: black;
            font-weight: 600;
            padding: 8px 16px;
            border: none;
        }
        QLabel#PromptTitle {
            color: #ff3b30;
            font-weight: 700;
            font-size: 20px;
        }
        QLabel#PromptBody {
            color: #ffffff;
            font-size: 18px;
        }
        QLabel#PromptTags {
            color: #bbbbbb;
            font-size: 13px;
        }
        QLineEdit#SessionTitle {
            font-size: 24px;      /* bigger title */
            font-weight: 600;
            color: #777777;
            border: none;
        }
        QTextEdit#WritingEditor {
            font-size: 20px;      /* bigger body text */
        }
        QLabel#TimeLabel {
            font-weight: 600;
        }
        QLabel#WordsLabel {
            font-weight: 600;
            color: #00b894;
        }
        """)
