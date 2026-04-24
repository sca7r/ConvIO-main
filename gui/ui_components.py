"""
CONVIO - Reusable UI Components
================================

Reusable Qt widgets for result presentation.  No business logic here —
components receive pre-formatted strings from ``results_formatter``.

Components
----------
MetricsPanel        QGroupBox with a 2-column key/value grid.
SortableTable       QTableWidget with alternating rows + sort on header click.
TopologyResultWidget  QWidget that stacks a PlotWidget above a MetricsPanel.
"""

from typing import Any, Dict, List, Optional, Tuple

import pyqtgraph as pg

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QGroupBox, QHeaderView,
    QLabel, QScrollArea, QSizePolicy, QSplitter, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)


# ── Shared style constants ─────────────────────────────────────────────────────
_HEADER_BG  = QColor("#37474F")   # dark blue-grey
_HEADER_FG  = QColor("#FFFFFF")
_ALT_ROW    = QColor("#F5F7F8")   # very light grey
_BEST_ROW   = QColor("#E8F5E9")   # light green
_KEY_FONT   = QFont("Arial", 9)
_KEY_FONT.setBold(True)
_VAL_FONT   = QFont("Arial", 9)


class MetricsPanel(QGroupBox):
    """
    A labelled panel that displays key → value pairs in a 2-column grid.

    Usage::

        panel = MetricsPanel("Bus Topology Metrics")
        panel.update_metrics({"Total Length": "1234.56 mm", ...})
    """

    def __init__(self, title: str, parent: QWidget = None):
        super().__init__(title, parent)
        self._grid = QGridLayout(self)
        self._grid.setSpacing(4)
        self._grid.setContentsMargins(8, 8, 8, 8)
        self._labels: List[Tuple[QLabel, QLabel]] = []

    def update_metrics(self, metrics: Dict[str, str]) -> None:
        """Replace all rows with new key/value pairs."""
        # Clear existing widgets
        for key_lbl, val_lbl in self._labels:
            key_lbl.deleteLater()
            val_lbl.deleteLater()
        self._labels.clear()

        for row, (key, val) in enumerate(metrics.items()):
            key_lbl = QLabel(key)
            key_lbl.setFont(_KEY_FONT)
            key_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            val_lbl = QLabel(val)
            val_lbl.setFont(_VAL_FONT)
            val_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            val_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self._grid.addWidget(key_lbl, row, 0)
            self._grid.addWidget(val_lbl, row, 1)
            self._labels.append((key_lbl, val_lbl))

    def clear(self) -> None:
        self.update_metrics({})


class SortableTable(QTableWidget):
    """
    A read-only, sortable QTableWidget with alternating row colours and a
    styled header.

    Usage::

        t = SortableTable(["Linkage", "Wire (mm)", "CAN (mm)", "Total (mm)", "Saving"])
        t.populate([("complete", "1200.0", "300.0", "1500.0", "+12.3%"), ...],
                   best_row=0)   # optional: highlight row index
    """

    def __init__(self, headers: List[str], parent: QWidget = None):
        super().__init__(parent)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setStyleSheet(
            f"QHeaderView::section {{"
            f"background-color: {_HEADER_BG.name()};"
            f"color: {_HEADER_FG.name()};"
            f"padding: 4px; border: none; font-weight: bold; }}"
        )
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("alternate-background-color: #F5F7F8;")

    def populate(
        self,
        rows: List[Tuple],
        best_row: Optional[int] = None,
        center_cols: Optional[List[int]] = None,
    ) -> None:
        """
        Fill the table with rows.

        Args:
            rows:        Each tuple maps 1-to-1 to the column headers.
            best_row:    If given, paint that row with _BEST_ROW background.
            center_cols: Column indices to centre-align (default: all but first).
        """
        self.setSortingEnabled(False)
        self.setRowCount(len(rows))

        if center_cols is None:
            center_cols = list(range(1, self.columnCount()))

        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if c in center_cols:
                    item.setTextAlignment(Qt.AlignCenter)
                if r == best_row:
                    item.setBackground(_BEST_ROW)
                self.setItem(r, c, item)

        self.setSortingEnabled(True)
        self.resizeRowsToContents()

    def clear_data(self) -> None:
        self.setRowCount(0)


class TopologyResultWidget(QWidget):
    """
    Composite widget: plot view on top, scrollable metrics panel below.

    The outer ``main_window`` accesses ``widget.plot_view`` directly for
    visualization and calls ``widget.metrics_panel.update_metrics(...)``
    to refresh the numbers.
    """

    def __init__(self, plot_title: str, metrics_title: str, parent: QWidget = None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Vertical, self)

        # Plot view
        self.plot_view = pg.PlotWidget()

        # Metrics in a scroll area so long key lists never hide the plot
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMaximumHeight(200)

        self.metrics_panel = MetricsPanel(metrics_title)
        scroll.setWidget(self.metrics_panel)

        splitter.addWidget(self.plot_view)
        splitter.addWidget(scroll)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        outer.addWidget(splitter)
