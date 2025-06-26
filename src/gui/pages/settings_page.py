from typing import Callable
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QComboBox,
    QGroupBox,
)


class SettingsPage(QWidget):
    """Página de configuración de la aplicación."""

    def __init__(
        self,
        on_theme_changed: Callable[[bool], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        # ---- Sección Análisis ----
        analysis_group = QGroupBox("Análisis")
        analysis_layout = QFormLayout(analysis_group)

        self.output_dir_edit = QLineEdit()
        self.browse_btn = QPushButton("Examinar...")
        browse_layout = QHBoxLayout()
        browse_layout.addWidget(self.output_dir_edit)
        browse_layout.addWidget(self.browse_btn)
        browse_widget = QWidget()
        browse_widget.setLayout(browse_layout)

        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setMinimum(1)

        analysis_layout.addRow("Carpeta de Salida:", browse_widget)
        analysis_layout.addRow(
            "Sample Rate (procesar 1 de cada N frames):", self.sample_rate_spin
        )

        main_layout.addWidget(analysis_group)

        # ---- Sección Apariencia ----
        appearance_group = QGroupBox("Apariencia")
        appearance_layout = QFormLayout(appearance_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Oscuro", "Claro"])
        self.theme_combo.currentTextChanged.connect(
            lambda text: on_theme_changed(text == "Oscuro")
        )

        appearance_layout.addRow("Tema:", self.theme_combo)

        main_layout.addWidget(appearance_group)
        main_layout.addStretch()

        self.browse_btn.clicked.connect(self._select_output_dir)

    def _select_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta", self.output_dir_edit.text() or "."
        )
        if directory:
            self.output_dir_edit.setText(directory)
