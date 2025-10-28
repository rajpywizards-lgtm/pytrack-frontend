from typing import List, Tuple
from PySide6.QtCharts import (
    QChart, QChartView, QBarSet, QHorizontalStackedBarSeries,
    QValueAxis
)
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtCore import Qt, QMargins


TimelineItem = Tuple[str, float, str]  # (label, hours, hex-color)


class TimesheetChartQt(QWidget):
    """Horizontal stacked bar (timeline) showing task durations.

    Use set_timeline([...]) to provide live data:
      chart.set_timeline([("Emails", 0.5, "#9c27b0"), ...])
    Then call chart.refresh() or chart.refresh() will be called automatically.
    """

    def __init__(self, timeline: List[TimelineItem] | None = None, parent=None):
        super().__init__(parent)

        # default static timeline (keeps backwards compatibility)
        self.timeline: List[TimelineItem] = timeline or [
            ("Emails", 0.5, "#9c27b0"),
            ("Meetings", 1.5, "#f48fb1"),
            ("Coding", 3.0, "#81c784"),
            ("Break", 0.5, "#64b5f6"),
            ("Reports", 1.0, "#f9d976"),
            ("Marketing", 1.0, "#f8f276"),
        ]

        # create container widgets
        self._chart = QChart()
        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._chart_view)

        # initial render
        self.refresh()

    # -----------------------
    # Public API
    # -----------------------
    def set_timeline(self, items: List[TimelineItem]) -> None:
        """Replace timeline data and refresh chart."""
        self.timeline = items or []
        self.refresh()

    def refresh(self) -> None:
        """Rebuild chart from self.timeline (idempotent)."""
        self._chart.removeAllSeries()
        # Clear axes (simpler approach: create new chart object)
        self._chart = QChart()
        self._chart_view.setChart(self._chart)

        total_hours = sum(max(0.0, float(d)) for _, d, _ in self.timeline)

        series = QHorizontalStackedBarSeries()

        # If there are no items, show empty chart with axis range 0..1
        if not self.timeline:
            total_hours = 1.0
            axisX_range = 1.0
        else:
            axisX_range = total_hours if total_hours > 0 else 1.0

        for task, duration, color in self.timeline:
            bar = QBarSet(task)
            # QBarSet expects numeric values (one per category). We append a single value.
            try:
                bar.append(float(duration))
            except Exception:
                bar.append(0.0)
            try:
                bar.setColor(QColor(color))
            except Exception:
                # fallback to a neutral color
                bar.setColor(QColor("#888888"))
            # label color (if supported by the platform) — safe to call
            try:
                bar.setLabelColor(Qt.white)
            except Exception:
                pass
            series.append(bar)

        self._chart.addSeries(series)
        self._chart.setTitle("Today's Work Timeline")
        self._chart.setAnimationOptions(QChart.SeriesAnimations)
        self._chart.setBackgroundVisible(False)
        self._chart.setMargins(QMargins(0, 0, 0, 0))

        # Title & legend styling
        self._chart.setTitleBrush(QColor("#ffffff"))
        self._chart.setTitleFont(QFont("Segoe UI", 11, QFont.Bold))
        legend = self._chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setLabelColor(QColor("#ffffff"))
        legend.setFont(QFont("Segoe UI", 9))

        # ---- Axes ----
        axisX = QValueAxis()
        axisX.setRange(0, axisX_range)
        # Label format: show integer hours when possible, else floats with 1 decimal
        if axisX_range.is_integer():
            axisX.setLabelFormat("%d")
        else:
            axisX.setLabelFormat("%.1f")
        axisX.setTitleText("Time (hours)")
        self._chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        # Y-axis hidden (single category)
        axisY = QValueAxis()
        axisY.setVisible(False)
        self._chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        # set chart object on view
        self._chart_view.setChart(self._chart)
