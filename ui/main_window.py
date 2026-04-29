# ui/main_window.py

from datetime import date
from pathlib import Path

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
    QMenuBar,
    QMenu,
    QFileDialog,
    QProgressDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent

from core.session_manager import SessionManager
from core.models import WritingSession
from core.storage import load_sessions_for_date, load_all_sessions
from core.streak_days import load_completed_days, compute_streaks_from_days
from core.stats import compute_streaks
from core.topic_generator import TopicGenerator
from core.logging_config import get_logger
from core.config import get_settings
from core.export import export_sessions_bulk, get_export_extension
from core.backup import create_backup, restore_backup, list_backups, get_backup_info
from ui.session_view import SessionView
from ui.calendar_view import CalendarView
from ui.session_list_dialog import SessionListDialog
from ui.history_view import HistoryView
from ui.tag_selector_dialog import TagSelectorDialog
from ui.settings_dialog import SettingsDialog
from ui.stats_view import StatsView
from ui.about_dialog import AboutDialog
from ui.shortcuts_dialog import ShortcutsDialog

logger = get_logger("main_window")



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Daily Writing Trainer")
        self.resize(1100, 700)

        self.CALENDAR_HEADER = "WRITING CALENDAR"
        self.HISTORY_HEADER = "SESSION LIST"


        self.session_manager = SessionManager()
        self.topic_generator = TopicGenerator()
        self.settings = get_settings()

        # ----- Menu bar -----
        self._create_menu_bar()

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

        # Calendar / session list / statistics buttons
        calendar_btn = QPushButton("CALENDAR VIEW")
        calendar_btn.setObjectName("NavButton")
        sessions_list_btn = QPushButton("SESSION LIST")
        sessions_list_btn.setObjectName("NavButton")
        stats_btn = QPushButton("STATISTICS")
        stats_btn.setObjectName("NavButton")

        sb_layout.addWidget(calendar_btn)
        sb_layout.addWidget(sessions_list_btn)
        sb_layout.addWidget(stats_btn)

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

        # --- Stacked pages (calendar, session, history, stats) ---
        self.stacked = QStackedWidget()  # QStackedWidget allows showing one page at a time, allowing switching
        self.calendar_view = CalendarView()
        self.session_view = SessionView(self.session_manager)
        self.session_view.titleChanged.connect(self.on_session_title_changed)
        self.history_view = HistoryView()
        self.history_view.sessionsChanged.connect(self._on_sessions_changed)
        self.stats_view = StatsView()

        # define page indices
        self.PAGE_CALENDAR = 0
        self.PAGE_SESSION = 1
        self.PAGE_HISTORY = 2
        self.PAGE_STATS = 3

        # add widgets in matching order
        self.stacked.addWidget(self.calendar_view)   # index 0
        self.stacked.addWidget(self.session_view)    # index 1
        self.stacked.addWidget(self.history_view)    # index 2
        self.stacked.addWidget(self.stats_view)      # index 3

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
        stats_btn.clicked.connect(self.show_statistics)

        self.session_view.sessionFinished.connect(self.on_session_finished)
        self.session_view.sessionCancelled.connect(self.on_session_cancelled)

        # when a date is clicked in the calendar, open the session list dialog
        self.calendar_view.dateClicked.connect(self.on_calendar_date_clicked)

        # when sessions are changed (deleted) from history view
        self.history_view.sessionsChanged.connect(self._on_sessions_changed)

        self.show_calendar()
        self._apply_basic_style()

        # Check for abandoned drafts after UI is ready
        QTimer.singleShot(500, self._check_abandoned_drafts)

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

    def show_statistics(self):
        self.stats_view.refresh()
        self.header_title.setText("STATISTICS")
        self.streak_label.hide()
        self.stacked.setCurrentIndex(self.PAGE_STATS)

    # ----- Session handlers -----
    def start_free_writing(self):
        self.session_view.start_new_session(mode="free", topic=None)
        self.show_session()

    def start_random_topic(self):

        dlg = TagSelectorDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        tag_ids = dlg.selected_tags()

        # Show loading indicator while generating topic
        progress = QProgressDialog("Generating writing prompt...", None, 0, 0, self)
        progress.setWindowTitle("AI Topic Generation")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)
        progress.show()

        # Process events to show the dialog
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            topic = self.topic_generator.generate_topic(tag_ids)
        finally:
            progress.close()

        # Notify if using fallback prompt
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
        logger.info("Session finished: %s (%d words)", session.id, session.word_count)
        self.show_calendar()

    def on_session_cancelled(self):
        logger.info("Session cancelled")
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

    def _check_abandoned_drafts(self):
        """Check for abandoned drafts from previous sessions and offer recovery."""
        drafts = SessionManager.get_abandoned_drafts()
        if not drafts:
            return

        # For now, handle the most recent draft
        draft = drafts[0]
        logger.info("Found abandoned draft from %s with %d words",
                    draft.session_date, draft.word_count)

        reply = QMessageBox.question(
            self,
            "Recover Draft?",
            f"An unsaved writing session was found from {draft.session_date}.\n\n"
            f"Title: {draft.title}\n"
            f"Words: {draft.word_count}\n"
            f"Content preview: {draft.content[:100]}{'...' if len(draft.content) > 100 else ''}\n\n"
            "Would you like to recover this draft?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Recover the draft - session_view.recover_session handles setup
            self.session_view.recover_session(draft)
            self.show_session()
            logger.info("Draft recovered: %s", draft.id)
        else:
            # Discard the draft
            SessionManager.delete_draft(draft.id)
            logger.info("Draft discarded: %s", draft.id)

            # Check if there are more drafts
            if len(drafts) > 1:
                for d in drafts[1:]:
                    SessionManager.delete_draft(d.id)



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
        QMenuBar {
            background-color: #111111;
            color: #ffffff;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #333333;
        }
        QMenu {
            background-color: #222222;
            color: #ffffff;
            border: 1px solid #333333;
        }
        QMenu::item {
            padding: 6px 24px;
        }
        QMenu::item:selected {
            background-color: #444444;
        }
        QMenu::separator {
            height: 1px;
            background-color: #333333;
            margin: 4px 0;
        }
        """)

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # DailyWriting menu (application menu on macOS)
        app_menu = menubar.addMenu("DailyWriting")

        about_action = QAction("About DailyWriting", self)
        about_action.triggered.connect(self._show_about)
        app_menu.addAction(about_action)

        app_menu.addSeparator()

        settings_action = QAction("Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.setMenuRole(QAction.MenuRole.PreferencesRole)
        settings_action.triggered.connect(self._show_settings)
        app_menu.addAction(settings_action)

        app_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.setMenuRole(QAction.MenuRole.QuitRole)
        quit_action.triggered.connect(self.close)
        app_menu.addAction(quit_action)

        # File menu
        file_menu = menubar.addMenu("File")

        new_free_action = QAction("New Free Session", self)
        new_free_action.setShortcut(QKeySequence("Ctrl+N"))
        new_free_action.triggered.connect(self.start_free_writing)
        file_menu.addAction(new_free_action)

        new_ai_action = QAction("New AI Session", self)
        new_ai_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_ai_action.triggered.connect(self.start_random_topic)
        file_menu.addAction(new_ai_action)

        file_menu.addSeparator()

        export_all_action = QAction("Export All Sessions...", self)
        export_all_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_all_action.triggered.connect(self._export_all_sessions)
        file_menu.addAction(export_all_action)

        file_menu.addSeparator()

        backup_action = QAction("Create Backup...", self)
        backup_action.triggered.connect(self._create_backup)
        file_menu.addAction(backup_action)

        restore_action = QAction("Restore from Backup...", self)
        restore_action.triggered.connect(self._restore_backup)
        file_menu.addAction(restore_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._do_undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._do_redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._do_cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._do_copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._do_paste)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self._do_select_all)
        edit_menu.addAction(select_all_action)

        # View menu
        view_menu = menubar.addMenu("View")

        calendar_action = QAction("Calendar", self)
        calendar_action.setShortcut(QKeySequence("Ctrl+1"))
        calendar_action.triggered.connect(self.show_calendar)
        view_menu.addAction(calendar_action)

        history_action = QAction("Session List", self)
        history_action.setShortcut(QKeySequence("Ctrl+2"))
        history_action.triggered.connect(self.show_history)
        view_menu.addAction(history_action)

        stats_action = QAction("Statistics", self)
        stats_action.setShortcut(QKeySequence("Ctrl+3"))
        stats_action.triggered.connect(self.show_statistics)
        view_menu.addAction(stats_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def _show_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.settingsChanged.connect(self._on_settings_changed)
        dialog.exec()

    def _on_settings_changed(self):
        """Handle settings changes."""
        # Reload settings
        self.settings = get_settings()

        # Update topic generator model
        self.topic_generator.model = self.settings.ai.model

        # Update session view with new appearance settings
        self.session_view.apply_settings(self.settings)

        logger.info("Settings applied")

    def _show_about(self):
        """Show the About dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _show_shortcuts(self):
        """Show the keyboard shortcuts dialog."""
        dialog = ShortcutsDialog(self)
        dialog.exec()

    # ----- Edit menu handlers -----
    def _get_focused_text_widget(self):
        """Get the currently focused text widget, if any."""
        from PyQt6.QtWidgets import QApplication, QTextEdit, QLineEdit
        widget = QApplication.focusWidget()
        if isinstance(widget, (QTextEdit, QLineEdit)):
            return widget
        return None

    def _do_undo(self):
        """Undo action in focused text widget."""
        widget = self._get_focused_text_widget()
        if widget and hasattr(widget, 'undo'):
            widget.undo()

    def _do_redo(self):
        """Redo action in focused text widget."""
        widget = self._get_focused_text_widget()
        if widget and hasattr(widget, 'redo'):
            widget.redo()

    def _do_cut(self):
        """Cut action in focused text widget."""
        widget = self._get_focused_text_widget()
        if widget and hasattr(widget, 'cut'):
            widget.cut()

    def _do_copy(self):
        """Copy action in focused text widget."""
        widget = self._get_focused_text_widget()
        if widget and hasattr(widget, 'copy'):
            widget.copy()

    def _do_paste(self):
        """Paste action in focused text widget."""
        widget = self._get_focused_text_widget()
        if widget and hasattr(widget, 'paste'):
            widget.paste()

    def _do_select_all(self):
        """Select all action in focused text widget."""
        widget = self._get_focused_text_widget()
        if widget and hasattr(widget, 'selectAll'):
            widget.selectAll()

    def _export_all_sessions(self):
        """Export all sessions to a directory."""
        sessions = load_all_sessions()

        if not sessions:
            QMessageBox.information(
                self,
                "No Sessions",
                "There are no sessions to export."
            )
            return

        # Get export directory
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
        )

        if not export_dir:
            return

        # Get export settings
        settings = get_settings()
        export_format = settings.export.default_format
        include_metadata = settings.export.include_metadata

        try:
            exported = export_sessions_bulk(
                sessions,
                Path(export_dir),
                format=export_format,
                include_metadata=include_metadata
            )

            QMessageBox.information(
                self,
                "Export Complete",
                f"Exported {len(exported)} sessions to:\n{export_dir}"
            )
            logger.info("Exported %d sessions to %s", len(exported), export_dir)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export sessions:\n{e}"
            )
            logger.error("Bulk export failed: %s", e)

    def _create_backup(self):
        """Create a backup of all sessions."""
        # Ask for backup location
        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Backup",
            str(Path.home() / "dailywriting_backup.zip"),
            "ZIP Files (*.zip)"
        )

        if not backup_path:
            return

        try:
            path = create_backup(Path(backup_path))

            sessions = load_all_sessions()
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup created successfully!\n\n"
                f"Location: {path}\n"
                f"Sessions: {len(sessions)}"
            )
            logger.info("Manual backup created: %s", path)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Failed",
                f"Failed to create backup:\n{e}"
            )
            logger.error("Backup failed: %s", e)

    def _restore_backup(self):
        """Restore sessions from a backup."""
        # Ask for backup file
        backup_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            str(Path.home()),
            "ZIP Files (*.zip)"
        )

        if not backup_path:
            return

        # Get backup info
        try:
            info = get_backup_info(Path(backup_path))
            if "error" in info:
                QMessageBox.critical(
                    self,
                    "Invalid Backup",
                    f"The selected file is not a valid backup:\n{info['error']}"
                )
                return
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Reading Backup",
                f"Could not read backup file:\n{e}"
            )
            return

        # Confirm restore
        session_count = info.get("session_count", "unknown")
        reply = QMessageBox.question(
            self,
            "Restore Backup",
            f"This backup contains {session_count} sessions.\n\n"
            "Do you want to restore? Existing sessions with the same ID will be skipped.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            restored, skipped = restore_backup(Path(backup_path), merge=True)

            QMessageBox.information(
                self,
                "Restore Complete",
                f"Restore completed!\n\n"
                f"Sessions restored: {restored}\n"
                f"Sessions skipped (already exist): {skipped}"
            )
            logger.info("Restored %d sessions from backup", restored)

            # Refresh views
            self.calendar_view.refresh_month()
            self._update_streak_label()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Restore Failed",
                f"Failed to restore backup:\n{e}"
            )
            logger.error("Restore failed: %s", e)

    def closeEvent(self, event: QCloseEvent):
        """Handle window close - prompt if session is active."""
        # Check if there's an active writing session
        if self.stacked.currentIndex() == self.PAGE_SESSION and self.session_view._current_session:
            content = self.session_view.editor.toPlainText().strip()

            if content:
                reply = QMessageBox.question(
                    self,
                    "Unsaved Session",
                    "You have an active writing session.\n\n"
                    "Do you want to save it before quitting?",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save
                )

                if reply == QMessageBox.StandardButton.Save:
                    # Finish and save the session
                    self.session_view._on_finish_clicked()
                    event.accept()
                elif reply == QMessageBox.StandardButton.Discard:
                    # Clear draft and close
                    if self.session_view._current_session:
                        SessionManager.delete_draft(self.session_view._current_session.id)
                    event.accept()
                else:
                    # Cancel - don't close
                    event.ignore()
                    return
            else:
                # No content, just close (delete empty draft)
                if self.session_view._current_session:
                    SessionManager.delete_draft(self.session_view._current_session.id)

        event.accept()
