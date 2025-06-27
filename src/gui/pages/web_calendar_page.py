from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os


class WebCalendarPage(QWidget):
    """A page that displays a web-based component, like the FullCalendar."""

    def __init__(self, html_file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        url = QUrl.fromLocalFile(html_file_path)
        self.browser.setUrl(url)

        layout.addWidget(self.browser)
