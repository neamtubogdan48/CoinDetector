from detection.coin_analyser import CoinAnalyser
from calibration.calibration_detection import run_calibration_detection
from calibration.calibration_scale import CalibrationScaleEstimator
from utils.detection_config import (
    DetectionConfig,
    get_coin_names_for_currency,
    get_coin_radii_for_currency,
    normalize_currency_code,
)


class CalibrationManager:
    """Manages calibration of detection parameters based on reference coin images"""
    
    # Manual calibration tuning knobs
    MANUAL_SELECTION_TOP_K = 3

    # Auto calibration tuning knobs
    AUTO_OUTLIER_ERROR_THRESHOLD = 0.06
    AUTO_GLOBAL_ERROR_WEIGHT = 0.20

    def __init__(self, config: DetectionConfig = None, coin_analyser: CoinAnalyser = None, currency_code: str = "RON"):
        self.config = config or DetectionConfig()
        self.currency_code = normalize_currency_code(currency_code or self.config.currency_code)
        self.config.currency_code = self.currency_code

        self.coin_radii_mm = get_coin_radii_for_currency(self.currency_code)
        self.coin_names = get_coin_names_for_currency(self.currency_code)

        self.coin_analyser = coin_analyser or CoinAnalyser(
            currency_code=self.currency_code,
            coin_radii_mm=self.coin_radii_mm,
            coin_names=self.coin_names,
        )

        self.scale_estimator = CalibrationScaleEstimator(
            coin_radii_mm=self.coin_radii_mm,
            coin_names=self.coin_names,
            manual_selection_top_k=self.MANUAL_SELECTION_TOP_K,
            auto_outlier_error_threshold=self.AUTO_OUTLIER_ERROR_THRESHOLD,
            auto_global_error_weight=self.AUTO_GLOBAL_ERROR_WEIGHT,
        )

    def _log_calibration_header(self, image_path: str, debug_manager, auto_mode: bool, coin_value: int = None):
        """Log calibration header details"""

        if auto_mode:
            debug_manager.log("COIN CALIBRATION (AUTO MODE)\n")
        else:
            debug_manager.log("COIN CALIBRATION\n")
        debug_manager.log(f"DEBUG MODE: Saving processing steps to {debug_manager.debug_folder}")
        debug_manager.log(f"Calibration image: {image_path}")
        debug_manager.log(f"Currency: {self.currency_code}")
        if auto_mode:
            debug_manager.log("Auto mode: estimate pixels/mm from all validated coin candidates")
        else:
            debug_manager.log(f"Reference coin: {self.coin_names[coin_value]}")
            debug_manager.log(f"Radius: {self.coin_radii_mm[coin_value]}mm")

    def _log_expected_coin_sizes(self, pixels_per_mm: float, debug_manager):
        """Log expected pixel sizes at the calibrated scale"""

        debug_manager.log("\nExpected coin sizes at this scale:")
        for coin_val, radius_mm in self.coin_radii_mm.items():
            expected_px = int(radius_mm * pixels_per_mm)
            coin_name = self.coin_names[coin_val]
            debug_manager.log(f"   {coin_name}: {radius_mm}mm -> {expected_px}px")
        debug_manager.log("")

    def _build_updated_objects(self, new_pixels_per_mm: float) -> tuple[DetectionConfig, CoinAnalyser]:
        """Create updated config and analyser with a calibrated ratio"""

        updated_config = DetectionConfig(
            min_radius=self.config.min_radius,
            max_radius=self.config.max_radius,
            pixels_per_mm=new_pixels_per_mm,
            blur_kernel=self.config.blur_kernel,
            hough_param1=self.config.hough_param1,
            hough_param2=self.config.hough_param2,
            reference_resolution=self.config.reference_resolution,
            currency_code=self.currency_code,
        )

        updated_coin_analyser = CoinAnalyser(
            pixels_per_mm=new_pixels_per_mm,
            tolerance_mm=self.coin_analyser.tolerance_mm,
            currency_code=self.currency_code,
            coin_radii_mm=self.coin_radii_mm,
            coin_names=self.coin_names,
        )

        return updated_config, updated_coin_analyser

    def _validate_manual_coin_value(self, coin_value: int | None) -> int:
        """Validate manual calibration denomination for current currency"""

        if coin_value is None:
            allowed = ", ".join(str(v) for v in sorted(self.coin_radii_mm.keys()))
            raise ValueError(f"coin_value is required for manual mode. Allowed values: {allowed}")

        if coin_value not in self.coin_radii_mm:
            allowed = ", ".join(str(v) for v in sorted(self.coin_radii_mm.keys()))
            raise ValueError(f"coin_value must be one of: {allowed}")

        return int(coin_value)

    def calibrate_auto_from_image(self, image_path: str, debug_manager=None) -> tuple[DetectionConfig, CoinAnalyser]:
        """Auto-calibrate pixels/mm by fitting detected coins to selected currency denominations"""

        self._log_calibration_header(image_path, debug_manager, auto_mode=True)

        # Run calibration detection
        _, _, valid_coins, _ = run_calibration_detection(
            config=self.config,
            coin_analyser=self.coin_analyser,
            image_path=image_path,
            debug_manager=debug_manager,
            stage_message="Detecting circles for auto-calibration...",
        )
        
        # Compute pixels/mm based on auto calibration logic
        new_pixels_per_mm = self.scale_estimator.compute_auto(valid_coins, debug_manager)

        debug_manager.log("\nAuto calibration complete!")
        debug_manager.log(f"   Calculated ratio: {new_pixels_per_mm:.2f} pixels/mm")

        # Create updated config and analyser with new ratio
        updated_config, updated_coin_analyser = self._build_updated_objects(new_pixels_per_mm)
        self._log_expected_coin_sizes(new_pixels_per_mm, debug_manager)
        return updated_config, updated_coin_analyser

    def calibrate_from_image(self, image_path: str, coin_value: int, debug_manager=None) -> tuple[DetectionConfig, CoinAnalyser]:
        """Calibrates parameters for a coin type based on a reference image"""
        # Validate manual coin value input
        coin_value = self._validate_manual_coin_value(coin_value)

        self._log_calibration_header(image_path, debug_manager, auto_mode=False, coin_value=coin_value)

        # Run calibration detection
        _, _, valid_coins, _ = run_calibration_detection(
            config=self.config,
            coin_analyser=self.coin_analyser,
            image_path=image_path,
            debug_manager=debug_manager,
            stage_message="Searching for reference coin...",
        )
        
        # Compute pixels/mm based on manual calibration logic
        new_pixels_per_mm, calibrated_radius_px, real_radius_mm = self.scale_estimator.compute_manual(
            valid_coins, coin_value, debug_manager
        )

        debug_manager.log("\nCalibration complete!")
        debug_manager.log(f"   Detected radius: {calibrated_radius_px}px")
        debug_manager.log(f"   Expected radius: {real_radius_mm}mm")
        debug_manager.log(f"   Calculated ratio: {new_pixels_per_mm:.2f} pixels/mm")

        # Create updated config and analyser with new ratio
        updated_config, updated_coin_analyser = self._build_updated_objects(new_pixels_per_mm)
        self._log_expected_coin_sizes(new_pixels_per_mm, debug_manager)

        return updated_config, updated_coin_analyser
