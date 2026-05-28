from detection.coin_analyser import CoinAnalyser
from detection.coin_detector import CoinDetector
from detection.coin_processor import CoinProcessor
from calibration.calibration_detection import run_calibration_detection
from calibration.calibration_manager import CalibrationManager
from utils.detection_config import DetectionConfig
from utils.utils import ResultsManager


class _NoOpDebugManager:
    """No-op debug manager for non-debug mode in Flutter API context"""
    
    debug_mode = False
    debug_folder = ""

    def log(self, _message: str):
        return

    def log_error(self, _error, args_debug: bool = False):
        return

    def save_detailed_summary(self, results: dict, detector_params: dict, all_candidates: list | None = None):
        return

    def _log_candidate_details(self, all_candidates: list):
        return


def calibrate_and_analyze_from_image(
    manager: CalibrationManager,
    image_path: str,
    auto_mode: bool = True,
    coin_value: int | None = None,
) -> tuple[dict, DetectionConfig, CoinAnalyser]:
    """Calibrate and analyze in a single pass to avoid repeated circle detection."""
    debug_ctx = _NoOpDebugManager()

    if not auto_mode:
        coin_value = manager._validate_manual_coin_value(coin_value)

    # Run calibration detection
    stage_message = "Detecting circles for auto-calibration..." if auto_mode else "Searching for reference coin..."
    detector, image, gray, _, calibration_valid_coins, _ = run_calibration_detection(
        config=manager.config,
        coin_analyser=manager.coin_analyser,
        image_path=image_path,
        debug_manager=debug_ctx,
        stage_message=stage_message,
    )
    
    # Compute pixels/mm based on calibration mode
    if auto_mode:
        new_pixels_per_mm = manager.scale_estimator.compute_auto(calibration_valid_coins, debug_ctx)
    else:
        new_pixels_per_mm, _, _ = manager.scale_estimator.compute_manual(calibration_valid_coins, coin_value, debug_ctx)

    # Build updated config and analyser with new ratio
    updated_config, updated_coin_analyser = manager._build_updated_objects(new_pixels_per_mm)

    # Re-validate with calibrated ratio on the validated coins
    detector.config = updated_config
    detector.coin_analyser = updated_coin_analyser
    detector.processor = CoinProcessor(updated_config, updated_coin_analyser)

    circles_to_validate = [(c["center"][0], c["center"][1], c["radius"]) for c in calibration_valid_coins]
    valid_coins, all_candidates = detector.processor.validate_candidates(
        gray, circles_to_validate, debug_ctx, detector, is_calibration=False
    )
    classified_coins = detector.processor.classify_coins(valid_coins)
    results = ResultsManager.build_results(
        image,
        classified_coins,
        all_candidates,
        draw_total_value=False,
    )
    results["currency_code"] = manager.currency_code
    results["coin_names"] = manager.coin_names

    return results, updated_config, updated_coin_analyser
