import numpy as np
import cv2
import math

from utils import detection_config as detection_config
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from utils.image_utils import ImageProcessor
from utils.detection_config import get_coin_names_for_currency, get_coin_radii_for_currency, normalize_currency_code
import os


@dataclass
class CoinAnalyser:
    """Validates coin candidates using ORB matching, overlap checking, and distance analysis"""

    # Tuning knobs
    overlap_threshold: float = 0.06
    pixels_per_mm: Optional[float] = None
    tolerance_mm: float = 0.8
    currency_code: str = "RON"
    coin_radii_mm: 'Optional[Dict[int, float]]' = None
    coin_names: 'Optional[Dict[int, str]]' = None

    def __post_init__(self):
        self.currency_code = normalize_currency_code(self.currency_code or detection_config.DetectionConfig.currency_code)
        if self.coin_radii_mm is None:
            self.coin_radii_mm = get_coin_radii_for_currency(self.currency_code)
        if self.coin_names is None:
            self.coin_names = get_coin_names_for_currency(self.currency_code)
        
    def classify_by_radius(self, radius_px: int) -> Tuple[str, int, float]:
        """Classify coin type by comparing pixel radius with real coin dimensions"""

        if not self.pixels_per_mm:
            raise ValueError("pixels_per_mm is not set. Calibrate before classification.")
        
        # Convert pixel radius to mm
        radius_mm = radius_px / self.pixels_per_mm
        
        best_match = None
        best_diff = float('inf')
        
        # Find closest matching coin type
        for coin_value, target_radius_mm in self.coin_radii_mm.items():
            diff = abs(radius_mm - target_radius_mm)
            if diff <= self.tolerance_mm and diff < best_diff:
                best_diff = diff
                best_match = coin_value
        
        if best_match:
            return self.coin_names.get(best_match, f"{best_match}"), best_match, radius_mm
        
        return "unknown", 0, radius_mm
    
    def calculate_overlap_ratio(self, center1: Tuple[int, int], radius1: int,
                              center2: Tuple[int, int], radius2: int) -> float:
        """Calculate geometric overlap ratio between two circles (0.0 - 1.0)"""
        x1, y1 = center1
        x2, y2 = center2
        
        # Calculate distance between centers
        dx = float(x2 - x1)
        dy = float(y2 - y1)
        d = math.hypot(dx, dy)
        r1 = float(radius1)
        r2 = float(radius2)
        
        # No overlap
        if d >= (r1 + r2):
            return 0.0
        
        # Complete overlap
        if d <= abs(r1 - r2):
            smaller_area = math.pi * (min(r1, r2) ** 2)
            larger_area = math.pi * (max(r1, r2) ** 2)
            return smaller_area / larger_area
        
        # Partial overlap calculation
        try:
            alpha = math.acos((d*d + r1*r1 - r2*r2) / (2 * d * r1))
            beta = math.acos((d*d + r2*r2 - r1*r1) / (2 * d * r2))
            inter_area = r1*r1*alpha + r2*r2*beta - 0.5*math.sqrt(
                max(0.0, (-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
            )
        except ValueError:
            # Conservative numeric fallback
            inter_area = math.pi * (min(r1, r2) ** 2)
        
        # Normalize by smaller circle area to get overlap ratio
        small_area = math.pi * (min(r1, r2) ** 2)
        return (inter_area / small_area) if small_area > 0 else 0.0
    
    def check_overlap_with_existing(self, center: Tuple[int, int], radius: int, 
                                   existing_coins: List[Dict]) -> Tuple[bool, str]:
        """Check if candidate overlaps with validated coins"""
        if not existing_coins:
            return True, "No existing coins to check overlap"
        
        # Check for overlap with existing coins
        for existing_coin in existing_coins:
            overlap_ratio = self.calculate_overlap_ratio(
                center, radius, 
                existing_coin['center'], existing_coin['radius']
            )
            if overlap_ratio >= self.overlap_threshold:
                return False, f"Overlap {overlap_ratio*100:.1f}% with existing coin (threshold {self.overlap_threshold*100:.0f}%)"
        
        return True, "No significant overlap with existing coins"
    
    def compare_pixel_intensity(self, gray_image: np.ndarray, center: Tuple[int, int], 
                                   radius: int) -> Tuple[bool, str]:
        """Check if coin is closer to camera by comparing pixel intensities"""
        
        # Create ring mask around coin and compare mean intensity with coin area
        background_mask = ImageProcessor.create_ring_mask(gray_image.shape, center, radius + 10, radius + 30)
        coin_mask = ImageProcessor.create_circular_mask(gray_image.shape, center, radius)
        coin_pixels = ImageProcessor.get_masked_pixels(gray_image, coin_mask)
        
        if background_mask is None or len(coin_pixels) == 0:
            return False, "Cannot analyze pixel intensity - insufficient coin data"
        
        background_pixels = ImageProcessor.get_masked_pixels(gray_image, background_mask)
        if len(background_pixels) == 0:
            return False, "Cannot analyze pixel intensity - insufficient background data"
        
        # Compare intensities
        coin_mean_intensity = np.mean(coin_pixels)
        background_mean_intensity = np.mean(background_pixels)
        
        if coin_mean_intensity < background_mean_intensity - 1:
            return True, f"Coin pixel intensity lower than background: (coin:{coin_mean_intensity:.1f} < bg:{background_mean_intensity:.1f})"
        else:
            return False, f"Background pixel intensity lower than coin: (coin:{coin_mean_intensity:.1f} >= bg:{background_mean_intensity:.1f})"
    
    def compare_with_reference_orb(self, gray: np.ndarray, center: tuple, radius: int, coin_value: int) -> bool:
        """Match coin with both front/back reference images using ORB features"""
        
        # Determine reference paths based on currency and coin value
        ref_dir = os.path.join(os.path.dirname(__file__), "..", "reference", "assets", self.currency_code.lower())
        if not coin_value:
            return False

        # Get reference paths for both sides of the coin
        ref_paths = {
            "front": os.path.join(ref_dir, f"{coin_value}_front.jpg"),
            "back": os.path.join(ref_dir, f"{coin_value}_back.jpg"),
        }

        # Require both reference sides to exist
        if not all(os.path.exists(path) for path in ref_paths.values()):
            return False

        # Crop coin from grayscale image
        x, y = center
        r = int(radius * 1.05)
        x1, y1 = max(x - r, 0), max(y - r, 0)
        x2, y2 = min(x + r, gray.shape[1]), min(y + r, gray.shape[0])
        coin_crop = gray[y1:y2, x1:x2]
        if coin_crop.size == 0:
            return False

        # Initialize ORB
        orb = cv2.ORB_create()
        _, des1 = orb.detectAndCompute(coin_crop, None)

        # Check if descriptors are found for coin crop
        if des1 is None:
            return False

        # Match coin against both sides, candidate is valid if either side matches well
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        for ref_path in ref_paths.values():
            ref_img = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
            if ref_img is None:
                continue
            ref_gray = cv2.resize(ref_img, (coin_crop.shape[1], coin_crop.shape[0]))
            _, des2 = orb.detectAndCompute(ref_gray, None)
            if des2 is None:
                continue

            # Match descriptors and filter good matches
            matches = bf.match(des1, des2)
            matches = sorted(matches, key=lambda x: x.distance)
            good_matches = [m for m in matches if m.distance < 60]
            if len(good_matches) >= 15:
                return True

        return False

    def validate_candidate(self, gray: np.ndarray, center: tuple, radius: int, existing_coins=None, is_calibration: bool = False) -> dict:
        """Run full validation pipeline: ORB, overlap, distance checks"""
        result = {
            'center': center,
            'radius': radius,
            'distance_passed': None,
            'distance_reason': None,
            'overlap_passed': None,
            'overlap_reason': None,
            'orb_passed': None,
            'orb_reason': None
        }
        reasons = []

        # Ignore ORB validation during calibration
        if is_calibration:
            result['orb_passed'] = True
            result['orb_reason'] = "ORB skipped for calibration/reference"
        else:
            coin_type, coin_value, _ = self.classify_by_radius(radius)

            # ORB validation
            if coin_type != "unknown":
                orb_verification = self.compare_with_reference_orb(gray, center, radius, coin_value)
                result['orb_passed'] = orb_verification
                result['orb_reason'] = "ORB match with reference" if orb_verification else "ORB match failed"
                if not orb_verification:
                    reasons.append(result['orb_reason'])
            else:
                result['orb_passed'] = False
                result['orb_reason'] = "Unknown coin type"
                reasons.append(result['orb_reason'])

        # Overlap check
        overlap_passed, overlap_reason = self.check_overlap_with_existing(center, radius, existing_coins)
        result['overlap_passed'] = overlap_passed
        result['overlap_reason'] = overlap_reason
        if not overlap_passed:
            reasons.append(overlap_reason)

        # Distance analysis
        distance_passed, distance_reason = self.compare_pixel_intensity(gray, center, radius)
        result['distance_passed'] = distance_passed
        result['distance_reason'] = distance_reason
        if not distance_passed:
            reasons.append(distance_reason)

        # Final reason
        if reasons:
            result['reason'] = ' | '.join(reasons)
        result['is_valid'] = not reasons

        return result
