import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)
from utils.detection_config import get_coin_radii_for_currency, normalize_currency_code


class CoinDetectionGUILayoutMixin:
    """Builds and configures GUI widgets/layout"""

    def _setup_ui(self, icon_path=None):
        # Set window properties
        self.setWindowTitle("Coin Detection")
        if icon_path:
            self.setWindowIcon(icon_path)
        self.setAcceptDrops(True)

        # Load stylesheet
        style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as file_obj:
                self.setStyleSheet(file_obj.read())

        title = QLabel("Coin Detection")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setMaximumHeight(48)

        self.image_label = QLabel("Drag and drop an image here or use 'Upload File'")
        self.image_label.setObjectName("ImageLabel")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(True)

        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.setMinimumSize(112, 38)
        self.upload_btn.clicked.connect(self.open_file_dialog)

        self.analyse_btn = QPushButton("Analyse")
        self.analyse_btn.setMinimumSize(92, 38)
        self.analyse_btn.setEnabled(False)
        self.analyse_btn.clicked.connect(self.analyse_image)

        self.calibrate_btn = QPushButton("Calibrate")
        self.calibrate_btn.setMinimumSize(96, 38)
        self.calibrate_btn.setEnabled(False)
        self.calibrate_btn.clicked.connect(self.calibrate_image)

        self.reference_btn = QPushButton("Reference")
        self.reference_btn.setMinimumSize(96, 38)
        self.reference_btn.setEnabled(False)
        self.reference_btn.clicked.connect(self.save_reference)

        self.debug_checkbox = QCheckBox("Debug")
        self.debug_checkbox.setChecked(False)

        self.value_dropdown = QComboBox()
        self.value_dropdown.setToolTip("Select calibration mode/value")
        self.value_dropdown.setMinimumSize(86, 38)
        self.value_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.currency_dropdown = QComboBox()
        self.currency_dropdown.addItems(["RON", "EUR", "USD", "GBP"])
        self.currency_dropdown.setCurrentText("RON")
        self.currency_dropdown.setToolTip("Select currency system")
        self.currency_dropdown.setMinimumSize(86, 38)
        self.currency_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.currency_dropdown.currentTextChanged.connect(self._update_value_dropdown_for_currency)

        self.reference_side_dropdown = QComboBox()
        self.reference_side_dropdown.addItems(["Front", "Back"])
        self.reference_side_dropdown.setCurrentIndex(0)
        self.reference_side_dropdown.setToolTip("Select front or back for ORB reference")
        self.reference_side_dropdown.setMinimumSize(96, 38)
        self.reference_side_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addWidget(self.image_label)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.addWidget(self.upload_btn)
        controls_layout.addWidget(self.analyse_btn)
        controls_layout.addWidget(self.calibrate_btn)
        controls_layout.addWidget(self.reference_btn)
        controls_layout.addWidget(self.currency_dropdown)
        controls_layout.addWidget(self.value_dropdown)
        controls_layout.addWidget(self.reference_side_dropdown)
        controls_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        controls_layout.addWidget(self.debug_checkbox)
        main_layout.addLayout(controls_layout)

        self.setLayout(main_layout)
        self.resize(840, 785)
        self.setMinimumSize(840, 785)
        self.setMaximumSize(840, 785)

        self._update_value_dropdown_for_currency(self.currency_dropdown.currentText())

    def _update_value_dropdown_for_currency(self, currency_code: str):
        """Update value dropdown options based on selected currency"""
        
        # Get sorted coin values for selected currency
        normalized_currency = normalize_currency_code(currency_code)
        values = sorted(get_coin_radii_for_currency(normalized_currency).keys())

        # Preserve previous selection if still valid, otherwise reset to "Auto"
        previous_value = self.value_dropdown.currentData()
        
        # Rebuild dropdown options
        self.value_dropdown.blockSignals(True)
        self.value_dropdown.clear()
        self.value_dropdown.addItem("Auto", userData=None)
        
        # Add specific coin values for selected currency
        for value in values:
            self.value_dropdown.addItem(str(value), userData=value)

        # Try to restore previous selection if it exists in new options
        if previous_value in values:
            idx = self.value_dropdown.findData(previous_value)
            self.value_dropdown.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            self.value_dropdown.setCurrentIndex(0)
        self.value_dropdown.blockSignals(False)
