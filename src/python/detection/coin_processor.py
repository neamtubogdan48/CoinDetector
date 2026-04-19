import numpy as np

from typing import List, Tuple, Dict
from utils.detection_config import DetectionConfig
from detection.coin_analyser import CoinAnalyser
from utils.image_utils import DebugVisualizer


class CoinProcessor:
    """Validates and classifies coin candidates"""

    def __init__(self, config: DetectionConfig, coin_analyser: CoinAnalyser):
        self.config = config
        self.coin_analyser = coin_analyser

    def validate_candidates(self, image: np.ndarray, circles: List[Tuple[int, int, int]], 
                           debug_manager, detector=None, is_calibration: bool = False) -> tuple[List[Dict], List[Dict]]:
        """Validate circle candidates using ORB, overlap, and distance checks"""
        debug_manager.log("Validating candidates...")
        
        valid_coins = []
        all_candidates = []
        
        # Iterate through detected circles and validate each candidate
        for i, (x, y, radius) in enumerate(circles):
            radius_mm = None
            
            # Calculate radius in mm if pixels_per_mm
            if self.config.pixels_per_mm:
                radius_mm = radius / self.config.pixels_per_mm

            # Initialize candidate result
            candidate_result = {
            'center': (x, y),
            'radius': radius,
            'radius_mm': radius_mm,
            'number': i + 1,
            'validated': False
            }
            
            # Perform detailed validation using CoinAnalyser
            detailed_result = self.coin_analyser.validate_candidate(
            image, (x, y), radius, valid_coins, is_calibration=is_calibration
            )
            
            # Update candidate result with detailed validation results
            candidate_result.update(detailed_result)
            candidate_result['number'] = i + 1

            # Determine if candidate is valid based on combined validation results
            candidate_result['validated'] = bool(
            candidate_result.get('orb_passed') and 
            candidate_result.get('overlap_passed') and 
            candidate_result.get('distance_passed')
            )

            # If candidate is valid, add to valid_coins list
            if candidate_result['validated']:
                candidate_result['candidate_number'] = i + 1
                valid_coins.append(candidate_result)
            
            # Add all candidates (for debug text output)
            all_candidates.append(candidate_result)
        
        debug_manager.log(f"    Validation complete: {len(valid_coins)}/{len(circles)} coins validated")
        
        # Save debug image showing validation results
        DebugVisualizer.save_validation_debug_image(
            image,
            valid_coins,
            all_candidates,
            len(circles),
            detector
        )

        return valid_coins, all_candidates
    
    def classify_coins(self, valid_coins: List[Dict]) -> List[Dict]:
        """Classify validated coins based on their dimensions"""
        classified_coins = []
        # Classify each validated coin by radius
        for coin in valid_coins:
            radius_px = coin['radius']
            coin_type, value, radius_mm = self.coin_analyser.classify_by_radius(radius_px)

            # Create a dictionary with classified coin details
            classified_coin = {
                'center': coin['center'],
                'radius': radius_px,
                'radius_mm': radius_mm,
                'coin_type': coin_type,
                'value': value,
                'candidate_number': coin.get('candidate_number', None)
            }
            classified_coins.append(classified_coin)
        
        return classified_coins
