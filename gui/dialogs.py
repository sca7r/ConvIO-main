"""
CONVIO - Dialog Windows
=======================

Modal dialogs shown on top of the main window.
"""

from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QDialog, QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout,
)


class ComparisonWindow(QDialog):
    """
    A dialog window to display the comparison of clustering linkage methods.

    Used after a "Run Full Analysis" run: shows the wiring length for each
    linkage method and highlights the best one.
    """

    _LINKAGE_METHODS = ["average", "complete", "single"]
    _COLUMNS = ["Linkage Method", "I/O Wiring (mm)", "CAN Bus (mm)", "Total Length (mm)"]
    _BEST_ROW_BG = QColor("#d4edda")

    def __init__(self, data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Linkage Method Comparison")
        self.setMinimumSize(600, 200)

        layout = QVBoxLayout(self)

        title = QLabel("<b>Comprehensive Analysis Results</b>")
        title.setFont(QFont("Arial", 14))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setRowCount(len(self._LINKAGE_METHODS))
        self.table.setColumnCount(len(self._COLUMNS))
        self.table.setHorizontalHeaderLabels(self._COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self._populate_table(data)

        best_method = data.get("best_method", "N/A")
        recommendation = QLabel(
            f"<b>Recommendation:</b> The '<b>{best_method}</b>' linkage method produced "
            f"the shortest overall wiring harness length and has been selected for "
            f"detailed visualization."
        )
        recommendation.setWordWrap(True)
        layout.addWidget(recommendation)

    # ------------------------------------------------------------------
    def _populate_table(self, data: Dict[str, Any]):
        results = data.get("results", {})
        best_method = data.get("best_method")

        for row, method in enumerate(self._LINKAGE_METHODS):
            res = results.get(method, {})

            wire_len = res.get("total_wire_length", 0.0)
            can_len = res.get("can_bus", {}).get("total_length", 0.0)
            total_len = res.get("overall_wiring_harness_length", 0.0)

            items = [
                QTableWidgetItem(method),
                QTableWidgetItem(f"{wire_len:.2f}"),
                QTableWidgetItem(f"{can_len:.2f}"),
                QTableWidgetItem(f"{total_len:.2f}"),
            ]

            # Bold + green-tinted background for the row corresponding to the
            # best method found in the sweep.
            if method == best_method:
                bold_font = QFont()
                bold_font.setBold(True)
                for item in items:
                    item.setFont(bold_font)
                    item.setBackground(self._BEST_ROW_BG)

            for col, item in enumerate(items):
                self.table.setItem(row, col, item)
