from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QWidget
from typing import Optional

try:
    import qtawesome as qta  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    qta = None

class DashboardCard(QGroupBox):
    """Card container for dashboard KPI and charts."""

    def __init__(self, title: str, icon_name: Optional[str] = None, parent: Optional[QWidget] = None) -> None:
        # Prepend icon text if qtawesome is available
        if icon_name and qta is not None:
            try:
                icon_txt = qta.icon(icon_name).text()
                title = f"{icon_txt}  {title}"
            except Exception:
                pass
        super().__init__(title, parent)
        self.setObjectName("DashboardCard")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 20, 10, 10)

    def setContent(self, widget: QWidget) -> None:
        """Replace current content with the provided widget."""
        while self._layout.count() > 0:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._layout.addWidget(widget)
