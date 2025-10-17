from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from api.task_client import get_my_tasks
from utils.state import AppState

class DashboardWindow(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.setWindowTitle("PyTrack Dashboard")
        self.setGeometry(500, 250, 700, 500)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)

        # Header
        title = QLabel("🕒 PyTrack Dashboard", alignment=Qt.AlignCenter)
        title.setStyleSheet("font-size:20px;font-weight:bold;")

        self.user_label = QLabel(f"Logged in as: {AppState.user_email}", alignment=Qt.AlignCenter)
        self.role_label = QLabel(f"Role: {AppState.user_role}", alignment=Qt.AlignCenter)

        # Buttons
        buttons = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh Tasks")
        self.logout_btn = QPushButton("🚪 Logout")
        buttons.addWidget(self.refresh_btn)
        buttons.addWidget(self.logout_btn)
        buttons.setAlignment(Qt.AlignCenter)

        # Task list
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background:#0000;
                border:1px solid #ccc;
                padding:8px;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(self.user_label)
        layout.addWidget(self.role_label)
        layout.addLayout(buttons)
        layout.addWidget(QLabel("📋 Your Tasks", alignment=Qt.AlignCenter))
        layout.addWidget(self.task_list)
        self.setLayout(layout)

        # Connect signals
        self.refresh_btn.clicked.connect(self.load_tasks)
        self.logout_btn.clicked.connect(self.logout_user)

        self.load_tasks()

    def load_tasks(self):
        """Fetch and display tasks."""
        self.task_list.clear()
        self.task_list.addItem("Fetching tasks…")
        result = get_my_tasks()
        self.task_list.clear()

        if not result["success"]:
            QMessageBox.warning(self, "Error", result["error"])
            self.task_list.addItem("⚠️ Could not fetch tasks.")
            return

        tasks = result["data"]
        if not tasks:
            self.task_list.addItem("✅ No tasks assigned yet.")
            return

        for task in tasks:
            title = task.get("title", "Untitled Task")
            status = task.get("status", "unknown")
            icon = {"assigned":"🟡", "in_progress":"🟢", "completed":"🔵"}.get(status, "⚪")
            self.task_list.addItem(QListWidgetItem(f"{icon}  {title}  ({status})"))

    def logout_user(self):
        AppState.clear()
        self.close()
        self.on_logout()
