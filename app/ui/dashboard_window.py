# app/ui/dashboard_window.py
import threading
import io
import os
from datetime import datetime, timezone

import requests  # kept for some fallback logging
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QApplication, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer

from app.utils.state import AppState
from app.ui.chart_widget import TimesheetChartQt
from app.ui.task_table import TaskTable
from app.api.screenshot_client import upload_screenshot
from app.api.task_client import get_my_tasks

# If you still want to use the backend direct path for any fallback:
API_URL = "http://127.0.0.1:8000"


class DashboardWindow(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.setWindowTitle("PyTrack Dashboard")

        # Keep references to dynamic widgets so we can refresh later
        self._chart_widget = None
        self._task_table = None
        self._user_label = None

        # -------- SCREENSHOT TIMER SETUP (background worker) --------
        self.screenshot_timer = QTimer(self)
        self.screenshot_timer.timeout.connect(self._on_screenshot_timeout)
        self.screenshot_timer.start(60 * 1000)  # every 1 minute

        # -------- SCREEN CENTERING + SIZE --------
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.5)
        height = int(screen.height() * 0.5)
        x = int((screen.width() - width) / 2)
        y = int((screen.height() - height) / 2)
        self.setGeometry(x, y, width, height)
        self.setFixedSize(width, height)

        # -------- LOAD STYLESHEET (safe) --------
        qss_path = os.path.join(os.path.dirname(__file__), "..", "styles", "dashboard.qss")
        try:
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
        except Exception:
            pass

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
            try:
                pixmap = QPixmap(logo_path)
                logo_label.setPixmap(pixmap.scaled(120, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception:
                logo_label.setText("PyTrack")
                logo_label.setObjectName("AppTitle")
        else:
            logo_label.setText("PyTrack")
            logo_label.setObjectName("AppTitle")

        # --- User label & logout ---
        self._user_label = QLabel(AppState.get_user_email() or "userXYZ")
        self._user_label.setObjectName("UserLabel")

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout_user)
        logout_btn.setObjectName("LogoutButton")

        topbar_layout.addWidget(logo_label)
        topbar_layout.addStretch(1)
        topbar_layout.addWidget(self._user_label)
        topbar_layout.addWidget(logout_btn)

        # ===== SCROLLABLE CONTENT =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 15, 20, 15)
        scroll_layout.setSpacing(20)

        # --- Sections ---
        self.add_section(scroll_layout, "Timesheet", "TimesheetFrame", chart=True)
        self.add_section(scroll_layout, "Tasks", "TasksFrame", text="🗂️ Task data will appear here")
        self.add_section(scroll_layout, "Screenshots Sent", "ScreenshotsFrame", text="📸 Screenshots will appear here")
        self.add_section(scroll_layout, "Videos Sent", "VideosFrame", text="🎥 Videos will appear here")

        scroll_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        scroll_area.setWidget(scroll_content)

        root_layout.addWidget(topbar)
        root_layout.addWidget(scroll_area)

        # initial data load
        self.refresh()

    # -----------------------
    # Section helper
    # -----------------------
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
            self._chart_widget = chart_widget
        elif text:
            if obj_name == "TasksFrame":
                task_table = TaskTable()
                layout.addWidget(task_table)
                self._task_table = task_table
            else:
                content_label = QLabel(text)
                content_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(content_label)

        parent_layout.addWidget(section)

    # -----------------------
    # Public API
    # -----------------------
    def refresh(self):
        """Reload tasks and refresh chart."""
        # update user label
        self._user_label.setText(AppState.get_user_email() or "userXYZ")

        # refresh tasks (table already loads on init)
        try:
            if self._task_table:
                self._task_table.refresh()
                # Optionally update chart using task durations:
                tasks_result = get_my_tasks()
                if tasks_result.get("success"):
                    tasks = tasks_result.get("data", [])
                    # Convert tasks to timeline items: (title, hours, color)
                    timeline = []
                    for t in tasks:
                        mins = t.get("estimated_minutes") or 0
                        hours = (mins / 60.0) if mins else 0.0
                        title = t.get("task") or t.get("title") or "Task"
                        timeline.append((title, round(hours, 2), "#81c784"))
                    if self._chart_widget:
                        self._chart_widget.set_timeline(timeline)
        except Exception:
            # keep UI stable even if refresh fails
            pass

    # -----------------------
    # Logout
    # -----------------------
    def logout_user(self):
        AppState.clear_auth()
        AppState.clear()
        try:
            self.close()
        finally:
            # call callback (e.g., show login window)
            try:
                self.on_logout()
            except Exception:
                pass

    # -----------------------
    # Screenshot capture (threaded)
    # -----------------------
    def _on_screenshot_timeout(self):
        # only capture if logged in
        if not AppState.get_access_token():
            return
        # spawn background thread to capture & upload
        t = threading.Thread(target=self.capture_screenshot, daemon=True)
        t.start()

    def capture_screenshot(self):
        """
        Capture primary monitor, convert to bytes, then call upload_screenshot (which posts to backend).
        Runs in background thread to avoid blocking the UI.
        """
        try:
            # lazy imports (not required unless capture is used)
            from mss import mss
            from PIL import Image

            # capture primary monitor
            with mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

            # convert to JPEG bytes
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=70, optimize=True)
            buf.seek(0)
            image_bytes = buf.read()

            # prepare timestamp
            ts_iso = datetime.now(timezone.utc).isoformat()

            # call frontend client which uses AppState token and backend upload endpoint
            res = upload_screenshot(image_bytes, captured_at_iso=ts_iso)
            if res.get("status") == "success":
                print(f"[✅] Uploaded screenshot: {res.get('image_url')}")
            else:
                print(f"[⚠] Upload failed: {res.get('message')}")
        except Exception as e:
            print(f"[❌] Screenshot pipeline failed: {e}")
