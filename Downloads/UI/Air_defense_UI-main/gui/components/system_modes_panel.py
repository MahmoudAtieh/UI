from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt, pyqtSignal

class SystemModesPanel(QWidget):
    """
    Provides vertical radio buttons for selecting system modes.
    Emits `mode_changed_signal` with the name of the selected mode.
    """
    mode_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initUI()

    def _initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        title = QLabel("System Modes", self)
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)

        # Button group for radio buttons
        self.btn_group = QButtonGroup(self)

        # Display names and corresponding internal values
        self.mode_map = {
            "Manual": "manual",
            "Phase One": "phase_1",
            "Phase Two": "phase_2",
            "Phase Three": "phase_3"
        }

        for idx, display_name in enumerate(self.mode_map.keys()):
            rb = QRadioButton(display_name, self)
            if idx == 0:
                rb.setChecked(True)
            self.btn_group.addButton(rb, id=idx)
            layout.addWidget(rb)

        self.btn_group.buttonToggled.connect(self._on_button_toggled)
        self.setLayout(layout)

    def _on_button_toggled(self, button, checked):
        if checked:
            display_text = button.text()
            internal_value = self.mode_map.get(display_text)
            if internal_value:
                self.mode_changed_signal.emit(internal_value)
