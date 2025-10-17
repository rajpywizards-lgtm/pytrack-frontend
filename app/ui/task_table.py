from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from api.task_client import get_my_tasks


class TaskTable(QWidget):
    """Displays a table of tasks fetched from the backend."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        title = QLabel("Assigned Tasks")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-weight:600;font-size:15px;")
        layout.addWidget(title)

        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setMinimumHeight(250)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.table.setHorizontalHeaderLabels([
            "#", "Task", "Assignee", "Time Required", "Description",
            "Task Highlight", "Time Recorded", "Completed At"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #252525;
                color: white;
                border: 1px solid #444;
                gridline-color: #555;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: #ffffff;
                font-weight: 600;
                padding: 5px;
                border: none;
            }
        """)

        layout.addWidget(self.table)

        # Fetch and load tasks
        self.load_tasks()

    def load_tasks(self):
        result = get_my_tasks()
        if not result["success"]:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("⚠️ Could not fetch tasks"))
            return

        tasks = result["data"]
        self.table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            self.table.setItem(row, 0, QTableWidgetItem(str(task.get("id", "-"))))
            self.table.setItem(row, 1, QTableWidgetItem(task.get("task", "")))
            self.table.setItem(row, 2, QTableWidgetItem(task.get("assignee", "—")))
            self.table.setItem(row, 3, QTableWidgetItem(str(task.get("estimated_minutes", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(task.get("description", "")))
            self.table.setItem(row, 5, QTableWidgetItem(task.get("task_highlight", "")))
            self.table.setItem(row, 6, QTableWidgetItem(str(task.get("time_recorded", ""))))
            self.table.setItem(row, 7, QTableWidgetItem(task.get("completed_at", "")))
