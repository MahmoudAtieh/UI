from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QComboBox, QSizePolicy, QHBoxLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

class ImageView(QWidget):
    """
    Displays camera feed received from ROS using QImage.
    Emits:
      - detection_layer_changed(str): when view selection is changed
      - log_message_requested(str): for UI status updates
    """
    detection_layer_changed = pyqtSignal(str)
    log_message_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # Group: View selector + camera display
        group = QGroupBox("Camera View")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(4, 4, 4, 4)

        # View selection dropdown
        view_header = QHBoxLayout()
        view_label = QLabel("View:", self)
        self.view_combo = QComboBox(self)
        self.view_combo.addItems(["Raw image", "Tracking"])
        self.view_combo.currentTextChanged.connect(self.detection_layer_changed)
        view_header.addWidget(view_label)
        view_header.addWidget(self.view_combo)
        group_layout.addLayout(view_header)

        # QLabel to display the image
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_layout.addWidget(self.label)

        main_layout.addWidget(group, stretch=1)
        self.setLayout(main_layout)

    def set_image(self, image: QImage):
        """
        Receives QImage from ROSConnector and displays it.
        """
        if image is not None and not image.isNull():
            self.label.setPixmap(QPixmap.fromImage(image))
