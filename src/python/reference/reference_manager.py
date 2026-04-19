import os
import cv2

from detection.coin_detector import CoinDetector
from detection.coin_analyser import CoinAnalyser
from detection.coin_processor import CoinProcessor
from utils.detection_config import DetectionConfig, get_coin_names_for_currency, normalize_currency_code


class ReferenceManager:
    """Manages reference images for ORB validation and calibration"""
    
    @staticmethod
    def ensure_ref_folder(currency_code="RON"):
        """Create and return currency-specific reference folder path"""

        currency_folder = normalize_currency_code(currency_code).lower()
        ref_dir = os.path.join(os.path.dirname(__file__), "assets", currency_folder)
        os.makedirs(ref_dir, exist_ok=True)
        return ref_dir

    @staticmethod
    def crop_coin(image, center, radius):
        """Crop coin region from image"""
        
        x, y = center
        r = int(radius * 1.05)
        x1, y1 = max(x - r, 0), max(y - r, 0)
        x2, y2 = min(x + r, image.shape[1]), min(y + r, image.shape[0])
        return image[y1:y2, x1:x2]

    @staticmethod
    def save_orb_reference(image_path, coin_value, coin_side="front", currency_code="RON", debug_manager=None):
        """Detect, validate and save coin crop as ORB reference for selected side"""
        try:
            coin_side = (coin_side or "front").strip().lower()
            if coin_side not in {"front", "back"}:
                coin_side = "front"
            currency_code = normalize_currency_code(currency_code)
            coin_names = get_coin_names_for_currency(currency_code)

            debug_manager.log("REFERENCE IMAGE SAVE\n")
            debug_manager.log(f"Debug mode enabled: Saving steps to /{debug_manager.debug_folder}")
            debug_manager.log(f"Reference image: {image_path}")
            debug_manager.log(f"Currency: {currency_code}")
            debug_manager.log(f"Reference coin: {coin_names.get(coin_value, coin_value)}")
            debug_manager.log(f"Reference side: {coin_side}")

            # Initialize components
            config = DetectionConfig(currency_code=currency_code)
            coin_analyser = CoinAnalyser(currency_code=currency_code)
            processor = CoinProcessor(config, coin_analyser)
            detector = CoinDetector(config=config, coin_analyser=coin_analyser, debug_manager=debug_manager)

            # Load and prepare image
            _, gray, blurred = detector.load_and_prepare_image(image_path)
            debug_manager.log("Searching for coin candidates...")

            # Find circles
            circles = detector.find_circles(blurred)
            if not circles:
                debug_manager.log("No coin found in image for reference")
                return None
            debug_manager.log(f"{len(circles)} circle(s) detected")

            # Validate candidates
            valid_coins, _ = processor.validate_candidates(
                gray, circles, debug_manager, is_calibration=True
            )
            debug_manager._log_candidate_details(valid_coins)

            if not valid_coins:
                debug_manager.log("No valid coin found for reference (validation failed)")
                return None

            # Use largest valid coin for reference
            coin = max(valid_coins, key=lambda c: c['radius'])
            center = coin['center']
            radius = coin['radius']
            candidate_number = coin.get('candidate_number', '?')

            # Save reference image
            ref_dir = ReferenceManager.ensure_ref_folder(currency_code)
            filename = f"{coin_value}_{coin_side}.jpg"
            ref_path = os.path.join(ref_dir, filename)

            # Crop and save coin region
            coin_crop = ReferenceManager.crop_coin(gray, center, radius)

            debug_manager.log(f"Reference coin selected: candidate #{candidate_number}, radius={radius}")
            # Save cropped coin as reference image
            cv2.imwrite(ref_path, coin_crop)
            debug_manager.log(f"ORB reference image saved at: {ref_path}")
            return ref_path

        except Exception as e:
            if debug_manager:
                debug_manager.log_error(f"Exception in save_orb_reference: {e}")
            return None