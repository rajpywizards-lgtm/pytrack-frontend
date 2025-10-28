# app/ui/task_table.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt
from app.api.task_client import get_my_tasks


def _format_minutes(m: int | None) -> str:
    if m is None:
        return ""
    try:
        m = int(m)
    except Exception:
        return str(m)
    if m >= 60:
        h = m // 60
        mm = m % 60
        return f"{h}h {mm}m" if mm else f"{h}h"
    return f"{m} min"


class TaskTable(QWidget):
    """Displays a table of tasks fetched from the backend."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

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

        # initial load
        self.load_tasks()

    # -------------------------
    # Public API
    # -------------------------
    def refresh(self) -> None:
        """Reload tasks from backend."""
        self.load_tasks()

    # -------------------------
    # Internal helpers
    # -------------------------
    def load_tasks(self) -> None:
        result = get_my_tasks()
        # normalized result: {"success": bool, "data": [...], "count": n}
        if not result or not result.get("success"):
            # single-row friendly error message
            self.table.clearContents()
            self.table.setRowCount(1)
            item = QTableWidgetItem("⚠️ Could not fetch tasks")
            item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(0, 0, item)
            # clear remaining cells
            for c in range(1, self.table.columnCount()):
                self.table.setItem(0, c, QTableWidgetItem(""))
            return

        tasks = result.get("data", []) or []
        self.table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            # support different backend shapes
            task_id = task.get("id") or task.get("task_id") or ""
            title = task.get("task") or task.get("title") or task.get("name") or ""
            assigned_to = task.get("assigned_to") or task.get("assignee") or "-"
            estimated_minutes = task.get("estimated_minutes") or task.get("time_required") or None
            description = task.get("description") or ""
            highlight = task.get("task_highlight") or task.get("highlight") or ""
            time_recorded = task.get("time_recorded") or ""
            completed_at = task.get("completed_at") or ""

            # Column 0: visible index (1-based). Put real id as tooltip on the row's first cell.
            idx_item = QTableWidgetItem(str(row + 1))
            idx_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if task_id:
                idx_item.setToolTip(str(task_id))
            self.table.setItem(row, 0, idx_item)

            self.table.setItem(row, 1, QTableWidgetItem(str(title)))
            self.table.setItem(row, 2, QTableWidgetItem(str(assigned_to)))
            self.table.setItem(row, 3, QTableWidgetItem(_format_minutes(estimated_minutes)))
            self.table.setItem(row, 4, QTableWidgetItem(str(description)))
            self.table.setItem(row, 5, QTableWidgetItem(str(highlight)))
            self.table.setItem(row, 6, QTableWidgetItem(str(time_recorded)))
            self.table.setItem(row, 7, QTableWidgetItem(str(completed_at)))

        # Resize columns to contents but keep last section stretched
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
