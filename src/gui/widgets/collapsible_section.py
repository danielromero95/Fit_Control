from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    pyqtProperty,
)
from PyQt5.QtGui import QIcon, QPixmap, QTransform

try:
    import qtawesome as qta  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    qta = None


class _RotatableButton(QPushButton):
    """QPushButton with a rotatable icon used for the chevron."""

    def __init__(
        self,
        text: str,
        normal_pixmap: QPixmap,
        hover_pixmap: QPixmap,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self._angle = 0.0
        self._normal_pixmap = normal_pixmap
        self._hover_pixmap = hover_pixmap
        self._base_pixmap = normal_pixmap
        self.setIcon(QIcon(normal_pixmap))
        self.setIconSize(normal_pixmap.size())
        self.setCursor(Qt.PointingHandCursor)

    def getAngle(self) -> float:
        return self._angle

    def setAngle(self, angle: float) -> None:
        self._angle = angle
        transform = QTransform().rotate(angle)
        rotated = self._base_pixmap.transformed(
            transform, Qt.SmoothTransformation
        )
        self.setIcon(QIcon(rotated))

    angle = pyqtProperty(float, fget=getAngle, fset=setAngle)

    # ------------------------------------------------------
    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._base_pixmap = self._hover_pixmap or self._normal_pixmap
        self.setAngle(self._angle)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._base_pixmap = self._normal_pixmap
        self.setAngle(self._angle)
        super().leaveEvent(event)


class CollapsibleSection(QWidget):
    """A section with a clickable header that expands/collapses its content."""

    def __init__(self, title: str, content_widget: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._content = content_widget
        self._content.setObjectName("GridContentContainer")

        normal_pixmap = QPixmap()
        hover_pixmap = QPixmap()
        if qta is not None:
            try:
                normal_pixmap = qta.icon(
                    "fa5s.chevron-right", color="#F6AD55"
                ).pixmap(14, 14)
                hover_pixmap = qta.icon(
                    "fa5s.chevron-right", color="#FFFFFF"
                ).pixmap(14, 14)
            except Exception:
                normal_pixmap = QPixmap()
                hover_pixmap = QPixmap()

        self.header_btn = _RotatableButton(title, normal_pixmap, hover_pixmap)
        self.header_btn.setObjectName("CollapsibleHeader")
        self.header_btn.setCheckable(True)
        self.header_btn.setChecked(True)
        self.header_btn.clicked.connect(self.toggle)

        self.header_btn.setAngle(90)  # start expanded

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.header_btn)
        layout.addWidget(self._content)

        self._content.setMaximumHeight(self._content.sizeHint().height())

        self._content_anim = QPropertyAnimation(self._content, b"maximumHeight")
        self._content_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._content_anim.setDuration(150)

        self._arrow_anim = QPropertyAnimation(self.header_btn, b"angle")
        self._arrow_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._arrow_anim.setDuration(150)

        self._anim_group = QParallelAnimationGroup()
        self._anim_group.addAnimation(self._content_anim)
        self._anim_group.addAnimation(self._arrow_anim)

        self._expanded = True

    # ----------------------------------------------------------
    def toggle(self) -> None:
        """Toggle between expanded and collapsed state with animation."""
        full_height = self._content.sizeHint().height()
        if self._expanded:
            self._content_anim.setStartValue(full_height)
            self._content_anim.setEndValue(0)
            self._arrow_anim.setStartValue(90)
            self._arrow_anim.setEndValue(0)
        else:
            self._content_anim.setStartValue(0)
            self._content_anim.setEndValue(full_height)
            self._arrow_anim.setStartValue(0)
            self._arrow_anim.setEndValue(90)
        self._anim_group.start()
        self._expanded = not self._expanded

    def expand(self) -> None:
        """Expand the section if it is collapsed."""
        if not self._expanded:
            self.toggle()

    def collapse(self) -> None:
        """Collapse the section if it is expanded."""
        if self._expanded:
            self.toggle()
