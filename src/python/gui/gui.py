import os
import sys

import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QWidget,
)

# Ensure src/python and project root are in sys.path for imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PYTHON_SRC_DIR = os.path.join(ROOT_DIR, "src", "python")
if PYTHON_SRC_DIR not in sys.path:
    sys.path.insert(0, PYTHON_SRC_DIR)

from detection.coin_detector import CoinDetector
from detection.coin_analyser import CoinAnalyser
from calibration.calibration_manager import CalibrationManager
from reference.reference_manager import ReferenceManager
from debug.debug_manager import DebugManager
from gui.gui_layout import CoinDetectionGUILayoutMixin
from utils.detection_config import normalize_currency_code


class CoinDetectionGUI(CoinDetectionGUILayoutMixin, QWidget):
    """ Main GUI class for coin detection, calibration and reference management"""
    
    def __init__(self, icon_path=None):
        super().__init__()
        self.root_dir = ROOT_DIR
        self.image_path = None
        self._calibrated_runtime = None
        self._setup_ui(icon_path=QIcon(icon_path) if icon_path else None)

    def _create_debug_manager(self) -> DebugManager | None:
        """ Initialize and return a DebugManager based on the debug checkbox state"""
        debug_mode = self.debug_checkbox.isChecked()
        debug_manager = DebugManager(debug_mode=debug_mode, debug_folder=os.path.join(self.root_dir, "debug"))
        
        if not debug_manager.setup():
            QMessageBox.critical(self, "Error", "Failed to initialize debug manager.")
            return None
        
        return debug_manager

    def open_file_dialog(self):
        """Open a file dialog to select an image file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.set_image(file_path)

    def set_image(self, file_path):
        """Set the image to be analyzed and update the GUI accordingly"""
        
        self.image_path = file_path
        pixmap = QPixmap(file_path)
        # Handle case where image fails to load
        if pixmap.isNull():
            self.image_label.setText("Failed to load image.")
            self.analyse_btn.setEnabled(False)
            self.calibrate_btn.setEnabled(False)
            self.reference_btn.setEnabled(False)
            return

        # Scale pixmap to fit within 70% of screen width and 50% of screen height while maintaining aspect ratio
        screen_rect = QApplication.primaryScreen().availableGeometry()
        max_width = int(screen_rect.width() * 0.7)
        max_height = int(screen_rect.height() * 0.5)
        self.image_label.setPixmap(
            pixmap.scaled(
                max_width,
                max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.analyse_btn.setEnabled(True)
        self.calibrate_btn.setEnabled(True)
        self.reference_btn.setEnabled(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events if they contain URLs (files)"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop events to set the image"""
        urls = event.mimeData().urls()
        if urls:
            self.set_image(urls[0].toLocalFile())

    def analyse_image(self):
        """Run coin detection analysis on the current image using calibrated parameters"""
        if not self.image_path:
            QMessageBox.warning(self, "No Image", "Please upload an image first.")
            return

        debug_manager = self._create_debug_manager()
        if debug_manager is None:
            return

        start_time = debug_manager.start_timer()

        # Ensure we have calibrated parameters before analysis
        try:
            if self._calibrated_runtime is None:
                QMessageBox.warning(
                    self,
                    "Calibration required",
                    "Run calibration first before analysis.",
                )
                return

            # Initialize detector with calibrated config and analyser
            calibrated_config, calibrated_analyser = self._calibrated_runtime
            detector = CoinDetector(
                config=calibrated_config,
                coin_analyser=calibrated_analyser,
                debug_manager=debug_manager,
            )

            # Run analysis
            results = detector.detect_coins(self.image_path)
            if results is None:
                QMessageBox.critical(self, "Error", "Analysis failed")
                return

            # Save output image and display in GUI
            output_path = os.path.join(self.root_dir, "output.jpg")
            cv2.imwrite(output_path, results["image_with_annotations"])
            self.set_image(output_path)

        finally:
            # Log time for analysis operation
            debug_manager.log_operation_duration("Analyse", start_time)

    def calibrate_image(self):
        """Run calibration process on the current image to compute pixels/mm ratio"""
        if not self.image_path:
            QMessageBox.warning(self, "No Image", "Please upload an image first.")
            return

        debug_manager = self._create_debug_manager()
        if debug_manager is None:
            return

        start_time = debug_manager.start_timer()
        duration_logged = False

        try:
            # Determine if auto or manual calibration mode is selected
            selected_value = self.value_dropdown.currentData()
            auto_mode = selected_value is None
            selected_currency = normalize_currency_code(self.currency_dropdown.currentText())
            manager = CalibrationManager(currency_code=selected_currency)

            # Auto mode: run calibration without specific coin value
            if auto_mode:
                config, analyser = manager.calibrate_auto_from_image(
                    self.image_path,
                    debug_manager=debug_manager,
                )
                self._calibrated_runtime = (config, analyser)
                debug_manager.log_operation_duration("Calibration", start_time)
                duration_logged = True
                
                # Show message box after successful calibration
                QMessageBox.information(
                    self,
                    "Calibration finished",
                    "Calibration finished",
                )
                return

            # Manual mode: validate selected coin value and run calibration
            coin_value = int(selected_value)
            config, analyser = manager.calibrate_from_image(
                self.image_path,
                coin_value,
                debug_manager=debug_manager,
            )
            self._calibrated_runtime = (config, analyser)
            
            # Log time for calibration operation
            debug_manager.log_operation_duration("Calibration", start_time)
            duration_logged = True
            
            # Show message box after successful calibration
            QMessageBox.information(
                self,
                "Calibration finished",
                "Calibration finished",
            )
        finally:
            if not duration_logged:
                # Log time for calibration operation
                debug_manager.log_operation_duration("Calibration", start_time)

    def save_reference(self):
        """ Save a reference image for ORB matching based on the current image and selected coin value/side"""
        if not self.image_path:
            QMessageBox.warning(self, "No Image", "Please upload an image first.")
            return

        debug_manager = self._create_debug_manager()
        if debug_manager is None:
            return

        start_time = debug_manager.start_timer()
        duration_logged = False

        try:
            selected_value = self.value_dropdown.currentData()
            # Validate that a specific coin value is selected for reference save (cannot be "Auto")
            if selected_value is None:
                debug_manager.log_operation_duration("Reference", start_time)
                duration_logged = True
                QMessageBox.warning(self, "Reference", "Select a specific denomination for reference save.")
                return

            # Save reference image with selected coin value, side and currency
            coin_value = int(selected_value)
            selected_side = self.reference_side_dropdown.currentText()
            coin_side = "front" if selected_side == "Front" else "back"
            selected_currency = normalize_currency_code(self.currency_dropdown.currentText())
            ref_path = ReferenceManager.save_orb_reference(
                self.image_path,
                coin_value,
                coin_side=coin_side,
                currency_code=selected_currency,
                debug_manager=debug_manager,
            )

            # Handle case where reference save failed
            if not ref_path:
                debug_manager.log_operation_duration("Reference", start_time)
                duration_logged = True
                QMessageBox.critical(self, "Error", "Reference save failed")
                return

            # Log time for reference operation
            debug_manager.log_operation_duration("Reference", start_time)
            duration_logged = True
            
            # Show message box after successful reference save
            QMessageBox.information(
                self,
                "Reference saved",
                "Reference saved",
            )
        finally:
            if not duration_logged:
                # Log time for reference operation
                debug_manager.log_operation_duration("Reference", start_time)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application icon
    icon_path = os.path.join(ROOT_DIR, "src", "other", "assets", "favicon.ico")
    app.setWindowIcon(QIcon(icon_path))

    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Create and show the main window
    window = CoinDetectionGUI(icon_path=icon_path)
    window.show()
    sys.exit(app.exec())
