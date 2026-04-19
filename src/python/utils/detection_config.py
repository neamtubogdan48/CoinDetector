import math

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# Coin real dimensions by currency (radius in mm)
COIN_RADII_BY_CURRENCY_MM: Dict[str, Dict[int, float]] = {
    "RON": {
        1: 8.375,   # 1 ban: 16.75mm diameter
        5: 9.375,   # 5 bani: 18.75mm diameter
        10: 10.00,  # 10 bani: 20.00mm diameter
        50: 12.00,  # 50 bani: 24.00mm diameter
    },
    "EUR": {
        1: 8.125,    # 1 cent: 16.25mm
        2: 9.375,    # 2 cents: 18.75mm
        5: 10.625,   # 5 cents: 21.25mm
        10: 9.875,   # 10 cents: 19.75mm
        20: 11.125,  # 20 cents: 22.25mm
        50: 12.125,  # 50 cents: 24.25mm
        100: 11.625, # 1 euro: 23.25mm
        200: 12.875, # 2 euro: 25.75mm
    },
    "USD": {
        1: 9.525,    # 1 cent: 19.05mm
        5: 10.605,   # 5 cents: 21.21mm
        10: 8.955,   # 10 cents: 17.91mm
        25: 12.13,   # 25 cents: 24.26mm
        50: 15.305,  # 50 cents: 30.61mm
        100: 13.25,  # 1 dollar coin: 26.50mm
    },
    "GBP": {
        1: 10.15,   # 1 penny: 20.3mm
        2: 12.95,   # 2 pence: 25.9mm
        5: 9.00,    # 5 pence: 18.0mm
        10: 12.25,  # 10 pence: 24.5mm
        20: 10.70,  # 20 pence: 21.4mm
        50: 13.65,  # 50 pence: 27.3mm
        100: 11.715, # 1 pound: 23.43mm
        200: 14.20,  # 2 pounds: 28.40mm
    },
}

COIN_LABELS_BY_CURRENCY: Dict[str, Dict[int, str]] = {
    "RON": {1: "1 ban", 5: "5 bani", 10: "10 bani", 50: "50 bani"},
    "EUR": {
        1: "1 cent",
        2: "2 cents",
        5: "5 cents",
        10: "10 cents",
        20: "20 cents",
        50: "50 cents",
        100: "1 euro",
        200: "2 euro",
    },
    "USD": {
        1: "1 cent",
        5: "5 cents",
        10: "10 cents",
        25: "25 cents",
        50: "50 cents",
        100: "1 dollar",
    },
    "GBP": {
        1: "1 penny",
        2: "2 pence",
        5: "5 pence",
        10: "10 pence",
        20: "20 pence",
        50: "50 pence",
        100: "1 pound",
        200: "2 pounds",
    },
}

def normalize_currency_code(currency_code: str | None) -> str:
    if not currency_code:
        return "RON"
    normalized = currency_code.upper()
    return normalized if normalized in COIN_RADII_BY_CURRENCY_MM else "RON"


def get_coin_radii_for_currency(currency_code: str | None) -> Dict[int, float]:
    normalized = normalize_currency_code(currency_code)
    return dict(COIN_RADII_BY_CURRENCY_MM[normalized])


def get_coin_names_for_currency(currency_code: str | None) -> Dict[int, str]:
    normalized = normalize_currency_code(currency_code)
    return dict(COIN_LABELS_BY_CURRENCY[normalized])

@dataclass
class DetectionConfig:
    """Detection parameters for HoughCircles and image processing"""
    
    min_radius: int = 30
    max_radius: int = 300
    pixels_per_mm: Optional[float] = None

    blur_kernel: int = 7
    hough_param1: int = 100
    hough_param2: int = 40
    reference_resolution: Tuple[int, int] = (800, 600)
    currency_code: Optional[str] = None
    
    def auto_adjust_for_image(self, image_shape: Tuple[int, int]) -> 'DetectionConfig':
        """Create config adjusted for image size"""
        
        # Calculate scale factor based on image area compared to reference resolution
        height, width = image_shape
        image_area = height * width
        ref_area = self.reference_resolution[0] * self.reference_resolution[1]
        scale_factor = math.sqrt(image_area / ref_area)
        
        # Create new adjusted config
        adjusted = DetectionConfig(
            min_radius=max(15, int(self.min_radius * scale_factor)),
            max_radius=min(500, int(self.max_radius * scale_factor)),
            pixels_per_mm=self.pixels_per_mm,
            blur_kernel=self.blur_kernel,
            hough_param1=self.hough_param1,
            hough_param2=self.hough_param2,
            reference_resolution=self.reference_resolution,
            currency_code=self.currency_code,
        )
        
        return adjusted
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        
        return {
            'min_radius': self.min_radius,
            'max_radius': self.max_radius,
            'blur_kernel': self.blur_kernel,
            'hough_param1': self.hough_param1,
            'hough_param2': self.hough_param2,
            'pixels_per_mm': self.pixels_per_mm,
            'currency_code': self.currency_code,
        }
