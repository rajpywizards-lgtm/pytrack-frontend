from PySide6.QtCharts import (
    QChart, QChartView, QBarSet, QHorizontalStackedBarSeries,
    QValueAxis
)
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtCore import Qt, QMargins


class TimesheetChartQt(QWidget):
    """Horizontal stacked bar (bullet timeline) showing task durations."""
    def __init__(self):
        super().__init__()

        # ---- Fake static daily timeline ----
        # Format: (Task, Duration (hrs), Color)
        self.timeline = [
            ("Emails",   0.5, "#9c27b0"),
            ("Meetings", 1.5, "#f48fb1"),
            ("Coding",   3.0, "#81c784"),
            ("Break",    0.5, "#64b5f6"),
            ("Reports",  1.0, "#f9d976"),
            ("Marketing", 1.0, "#f8f276"),
        ]

        # ---- Create stacked bar ----
        series = QHorizontalStackedBarSeries()

        for task, duration, color in self.timeline:
            bar = QBarSet(task)
            bar.append(duration)
            bar.setColor(QColor(color))
            bar.setLabelColor(Qt.white)
            series.append(bar)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Today's Work Timeline")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # ✅ Make title and legend text white
        chart.setTitleBrush(QColor("#ffffff"))
        chart.setTitleFont(QFont("Segoe UI", 11, QFont.Bold))

        legend = chart.legend()
        legend.setLabelColor(QColor("#ffffff"))
        legend.setFont(QFont("Segoe UI", 9))

        # ---- Axes ----
        # X-axis: total hours in the day (0–8 for simplicity)
        axisX = QValueAxis()
        axisX.setRange(0, sum(d for _, d, _ in self.timeline))
        axisX.setLabelFormat("%d hr")
        axisX.setTitleText("Time (hours)")
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        # Y-axis hidden (only one stacked bar)
        axisY = QValueAxis()
        axisY.setVisible(False)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        # ---- Chart View ----
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(chart_view)
