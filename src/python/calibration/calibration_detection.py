from detection.coin_detector import CoinDetector


def run_calibration_detection(
    config,
    coin_analyser,
    image_path: str,
    debug_manager,
    stage_message: str,
    is_calibration: bool = True,
):
    """Run circle detection and candidate validation for calibration purposes"""
    
    # Initialize detector with current config and analyser
    detector = CoinDetector(config=config, coin_analyser=coin_analyser, debug_manager=debug_manager)
    detector.config.min_radius = config.min_radius
    detector.config.max_radius = config.max_radius

    # Load and prepare image
    image, gray, blurred = detector.load_and_prepare_image(image_path)
    debug_manager.log(stage_message)

    # Detect circles
    circles = detector.find_circles(blurred)
    if not circles:
        return detector, image, gray, [], [], []

    # Validate candidates
    valid_coins, all_candidates = detector.processor.validate_candidates(
        gray, circles, debug_manager, detector, is_calibration=is_calibration
    )
    
    # Log candidate details for debugging
    debug_manager._log_candidate_details(valid_coins)
    return detector, image, gray, circles, valid_coins, all_candidates
