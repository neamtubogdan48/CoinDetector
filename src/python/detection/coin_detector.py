import cv2
import numpy as np
import os

from typing import List, Tuple, Dict
from utils.detection_config import DetectionConfig
from detection.coin_analyser import CoinAnalyser
from utils.image_utils import DebugVisualizer
from detection.coin_processor import CoinProcessor
from utils.utils import ResultsManager


class CoinDetector:
    """Detects coins in images using HoughCircles and validation pipeline"""

    def __init__(self, config: DetectionConfig = None, coin_analyser: CoinAnalyser = None, debug_manager=None):
        self.config = config or DetectionConfig()
        self.coin_analyser = coin_analyser or CoinAnalyser()

        self.debug_manager = debug_manager
        self.debug_step = 0
        
        self.processor = CoinProcessor(self.config, self.coin_analyser)

    def _save_debug_step(self, image, step_name: str, description: str = "") -> int:
        """Save debug image with incremented step counter"""
        self.debug_step = DebugVisualizer.save_debug_image(
            self.debug_manager.debug_mode, self.debug_manager.debug_folder,
            self.debug_step, image, step_name, description
        )
        return self.debug_step
    
    
    def load_and_prepare_image(self, image_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Load image and apply preprocessing (grayscale, CLAHE, gamma correction, blur)"""
        image = cv2.imread(image_path)
        if image is None:
             self.debug_manager.log(f"Cannot load image: {image_path}")

        self.debug_manager.log(f"Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
    
        # Auto-adjust parameters based on image size
        self.config = self.config.auto_adjust_for_image(image.shape[:2])
        self.debug_manager.log(f"Parameters auto-adjusted for {image.shape[1]}x{image.shape[0]}")
    
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE to enhance contrast
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Apply gamma correction for brightness adjustment
        gamma = 1.1
        look_up_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in np.arange(0, 256)]).astype("uint8")
        gray = cv2.LUT(gray, look_up_table)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (self.config.blur_kernel, self.config.blur_kernel), 2)
    
        return image, gray, blurred
    
    
    def find_circles(self, image: np.ndarray) -> List[Tuple[int, int, int]]:
        """Detect circles using HoughCircles algorithm"""
        circles = cv2.HoughCircles(
            image,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=max(self.config.min_radius * 2, 100),
            param1=self.config.hough_param1,
            param2=self.config.hough_param2,
            minRadius=self.config.min_radius,
            maxRadius=self.config.max_radius
        )
        
        detected_circles = []
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            self.debug_manager.log(f"   HoughCircles found {len(circles)} initial candidates")

            # Filter by radius range
            for x, y, r in circles:
                if r >= self.config.min_radius and r <= self.config.max_radius:
                    detected_circles.append((x, y, r))
            
            # Save debug image with detected circles
            if len(detected_circles) > 0:
                debug_image = DebugVisualizer.create_debug_visualization(image, detected_circles, (0, 0, 255), 3)
                self._save_debug_step(debug_image, "all_circles_detected", f"All circles: {len(detected_circles)} candidates")
                
        return detected_circles
    
    
    def detect_coins(self, image_path: str) -> Dict:
        """Main detection pipeline: load image, find circles, validate, classify"""
        try:
            self.debug_manager.log("COIN DETECTION\n")
            self.debug_manager.log(f"Debug mode enabled: Saving steps to {self.debug_manager.debug_folder}")
            self.debug_manager.log(f"Processing: {image_path}")

            self.debug_step = 0
            
            # Load and prepare image
            image, gray, blurred = self.load_and_prepare_image(image_path)

            self._save_debug_step(image, "original", "Original image")
            self._save_debug_step(gray, "grayscale", "Grayscale conversion")
            self._save_debug_step(blurred, "blurred", "Gaussian blurred image")

            # Find circles
            self.debug_manager.log("Running HoughCircles detection...")
            detected_circles = self.find_circles(blurred)
            
            # Validate candidates
            valid_coins, all_candidates = self.processor.validate_candidates(
                gray, detected_circles, self.debug_manager, self, is_calibration=False
            )

            # Classify validated coins
            self.debug_manager.log("Classifying validated coins...")
            classified_coins = self.processor.classify_coins(valid_coins)
            
            # Filter candidates for output image
            candidates_for_result = [c for c in all_candidates if 
                                    c.get('validated') or 
                                    (not c.get('orb_passed') and 
                                     c.get('overlap_passed') and 
                                     c.get('distance_passed'))]
            
            # Build results with annotations
            results = ResultsManager.build_results(
                image,
                classified_coins,
                candidates_for_result,
                draw_total_value=self.debug_manager.debug_mode,
            )
            results['currency_code'] = getattr(self.config, 'currency_code', 'RON')
            results['coin_names'] = getattr(self.coin_analyser, 'coin_names', {})
            
            self._save_debug_step(results['image_with_annotations'], "final_result", "")
            
            # Save detailed summary for debugging and analysis
            detector_params = self.config.to_dict()
            detector_params['analyser'] = self.coin_analyser
            self.debug_manager.save_detailed_summary(
                results, detector_params, all_candidates
            )
            
            return results
            
        except Exception as e:
            self.debug_manager.log_error(e, args_debug=True)
            # Return empty results instead of None
            try:
                empty_image = cv2.imread(image_path) if os.path.exists(image_path) else np.zeros((480, 640, 3), dtype=np.uint8)
            except Exception:
                empty_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
            return ResultsManager.empty_results(empty_image)