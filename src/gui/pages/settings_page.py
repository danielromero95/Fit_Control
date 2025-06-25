from typing import Dict, Any, Callable
from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QSpinBox, QComboBox, QCheckBox


class SettingsPage(QWidget):
    """Página de configuración de la aplicación."""

    def __init__(
        self,
        exercises: Dict[str, Any],
        on_theme_toggled: Callable[[bool], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        layout = QFormLayout(self)
        self.output_dir_edit = QLineEdit()
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setMinimum(1)

        self.exercise_combo = QComboBox()
        for name in exercises.keys():
            self.exercise_combo.addItem(name)

        self.dark_mode_check = QCheckBox("Modo Oscuro")
        self.dark_mode_check.toggled.connect(on_theme_toggled)

        layout.addRow("Carpeta de Salida:", self.output_dir_edit)
        layout.addRow("Sample Rate (procesar 1 de cada N frames):", self.sample_rate_spin)
        layout.addRow("Ejercicio:", self.exercise_combo)
        layout.addRow(self.dark_mode_check)

