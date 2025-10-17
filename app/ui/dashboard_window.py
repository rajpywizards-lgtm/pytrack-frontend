from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QApplication, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
import os
from utils.state import AppState

from app.ui.chart_widget import TimesheetChartQt
from app.ui.task_table import TaskTable


class DashboardWindow(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.setWindowTitle("PyTrack Dashboard")

        # -------- SCREEN CENTERING + LOCKED SIZE --------
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.5)
        height = int(screen.height() * 0.5)
        x = int((screen.width() - width) / 2)
        y = int((screen.height() - height) / 2)
        self.setGeometry(x, y, width, height)
        self.setFixedSize(width, height)  # 🚫 Prevent resizing

        # -------- LOAD STYLESHEET --------
        qss_path = os.path.join(os.path.dirname(__file__), "..", "styles", "dashboard.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())

        # -------- ROOT LAYOUT --------
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ===== TOP BAR =====
        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 5, 20, 5)

        # --- Company Logo ---
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "company_logo_purple.png")
        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(120, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("PyTrack")  # fallback text
            logo_label.setObjectName("AppTitle")

        user_label = QLabel(f"{AppState.user_email or 'userXYZ'}")
        user_label.setObjectName("UserLabel")

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.on_logout)
        logout_btn.setObjectName("LogoutButton")

        topbar_layout.addWidget(logo_label)
        topbar_layout.addStretch(1)
        topbar_layout.addWidget(user_label)
        topbar_layout.addWidget(logout_btn)

        # ===== SCROLLABLE CONTENT =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Inner container that actually holds all dashboard content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 15, 20, 15)
        scroll_layout.setSpacing(20)

        # --- Sections ---
        self.add_section(scroll_layout, "Timesheet — 25 December 2025", "TimesheetFrame", chart=True)
        self.add_section(scroll_layout, "Tasks", "TasksFrame", text="🗂️ Task data will appear here")
        self.add_section(scroll_layout, "Screenshots Sent", "ScreenshotsFrame", text="📸 Screenshots will appear here")
        self.add_section(scroll_layout, "Videos Sent", "VideosFrame", text="🎥 Videos will appear here")

        scroll_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        scroll_area.setWidget(scroll_content)

        # Add topbar + scroll area to root layout
        root_layout.addWidget(topbar)
        root_layout.addWidget(scroll_area)

    # -------- Helper to create styled sections --------
    def add_section(self, parent_layout, title, obj_name, text=None, chart=False):
        section = QFrame()
        section.setObjectName(obj_name)
        layout = QVBoxLayout(section)
        layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        label = QLabel(title)
        label.setObjectName("SectionLabel")
        layout.addWidget(label)

        if chart:
            chart_widget = TimesheetChartQt()
            chart_widget.setFixedHeight(250)
            layout.addWidget(chart_widget)
        elif text:
            if obj_name == "TasksFrame":
                task_table = TaskTable()
                layout.addWidget(task_table)
            else:
                content_label = QLabel(text)
                content_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(content_label)

        parent_layout.addWidget(section)

    def logout_user(self):
        AppState.clear()
        self.close()
        self.on_logout()
