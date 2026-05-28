import cv2
import numpy as np
import os

from typing import Tuple, List, Dict


class ImageProcessor:
    """Mask generation and pixel extraction"""
    
    @staticmethod
    def create_circular_mask(shape: Tuple[int, int], center: Tuple[int, int], radius: int, 
                            thickness: int = -1) -> np.ndarray:
        mask = np.zeros(shape, dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, thickness)
        return mask

    @staticmethod
    def create_ring_mask(shape: Tuple[int, int], center: Tuple[int, int], 
                        inner_radius: int, outer_radius: int) -> np.ndarray:
        mask = ImageProcessor.create_circular_mask(shape, center, outer_radius)
        cv2.circle(mask, center, inner_radius, 0, -1)
        return mask

    @staticmethod
    def get_masked_pixels(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        return image[mask > 0]


class DebugVisualizer:
    """Debug image creation and saving"""
    
    @staticmethod
    def create_debug_visualization(image: np.ndarray, circles: List[Tuple[int, int, int]], 
                                  color: Tuple[int, int, int] = (0, 0, 255),
                                  thickness: int = 3) -> np.ndarray:
        """Draw circles on image for debugging"""

        # Convert to BGR if grayscale
        if len(image.shape) == 2:
            debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            debug_image = image.copy()
        
        # Draw circles
        for i, (x, y, r) in enumerate(circles):
            cv2.circle(debug_image, (x, y), r, color, thickness)
            cv2.putText(debug_image, f"{i+1}", (x-10, y-r-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        return debug_image

    @staticmethod
    def save_debug_image(debug_mode: bool, debug_folder: str, debug_step: int, image, 
                        step_name: str, description: str = "") -> int:
        """Save debug image with step counter and returns incremented step"""
        if not debug_mode:
            return debug_step

        # Ensure debug folder exists
        if not os.path.isabs(debug_folder):
            debug_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "debug")
        os.makedirs(debug_folder, exist_ok=True)

        # Save image
        debug_step += 1
        filename = f"{debug_step:02d}_{step_name}.jpg"
        filepath = os.path.join(debug_folder, filename)

        # Add description if provided
        if len(description) > 0:
            debug_image = image.copy()
            cv2.putText(debug_image, description, (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 255, 255), 6)
            cv2.imwrite(filepath, debug_image)
        else:
            cv2.imwrite(filepath, image)

        return debug_step
    
    @staticmethod
    def save_validation_debug_image(image: np.ndarray, valid_coins: List[Dict], all_candidates: List[Dict], total_circles: int, coin_detector=None):
        """Save validation debug image with annotated candidates"""
        if not coin_detector:
            return
        
        # Convert to BGR if grayscale
        debug_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Draw circles
        if len(valid_coins) > 0:
            ImageAnnotator.annotate_valid_coins(debug_image, valid_coins)

        # Draw invalid coins
        candidate_orb_failed = [c for c in all_candidates if not c.get('validated')]
        ImageAnnotator.annotate_invalid_coins(debug_image, candidate_orb_failed)
        
        coin_detector._save_debug_step(debug_image, "all_circles_validated", f"Validated: {len(valid_coins)}/{total_circles}")


class ImageAnnotator:
    """Drawing annotations on images"""
    
    @staticmethod
    def draw_total_value(image: np.ndarray, total_value: int):
        """Draw total value text on image"""
        text = f"Total value: {total_value}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, text, (20, 100), font, 3.0, (255, 255, 255), 6)

    @staticmethod
    def draw_large_annotation(image: np.ndarray, center: Tuple[int, int], 
                             radius: int, value: int, candidate_number: int = None,
                             coin_label: str = None):
        """Draw coin annotation with value and candidate number"""
        
        # Select color based on coin value
        colors = {
            1: (255, 255, 0),    # Cyan
            2: (0, 165, 255),    # Orange
            5: (0, 255, 0),      # Green
            10: (255, 0, 0),     # Blue
            20: (0, 255, 255),   # Yellow
            50: (255, 0, 255),    # Magenta
            100: (0, 128, 255),  # Deep orange
            200: (128, 0, 255),  # Purple
        }
        color = colors.get(value, (128, 128, 128))
        
        # Draw circle
        x, y = center
        cv2.circle(image, (x, y), radius, color, 5)
        cv2.circle(image, (x, y), 8, color, -1)

        # Draw text
        text = coin_label if coin_label else f"{value}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        thickness = 3
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = x - text_size[0] // 2
        text_y = y - radius + 80

        # Draw white background for text
        cv2.rectangle(image,
                     (text_x - 10, text_y - text_size[1] - 10),
                     (text_x + text_size[0] + 10, text_y + 10),
                     (255, 255, 255), -1)
        
        cv2.rectangle(image,
                     (text_x - 10, text_y - text_size[1] - 10),
                     (text_x + text_size[0] + 10, text_y + 10),
                     color, 3)
        
        cv2.putText(image, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)

        # Draw candidate number if provided
        if candidate_number is not None:
            candidate_text = f"#{candidate_number}"
            
            candidate_size = cv2.getTextSize(candidate_text, font, font_scale, thickness)[0]
            candidate_x = x - candidate_size[0] // 2
            candidate_y = y + radius - 40
            
            cv2.rectangle(image,
                         (candidate_x - 10, candidate_y - candidate_size[1] - 10),
                         (candidate_x + candidate_size[0] + 10, candidate_y + 10),
                         (255, 255, 255), -1)
            
            cv2.rectangle(image,
                         (candidate_x - 10, candidate_y - candidate_size[1] - 10),
                         (candidate_x + candidate_size[0] + 10, candidate_y + 10),
                         color, 3)
            
            cv2.putText(image, candidate_text, (candidate_x, candidate_y), 
                       font, font_scale, (0, 0, 0), thickness)

    @staticmethod
    def annotate_valid_coins(image: np.ndarray, coins: List[dict]):
        """Draw green annotations for validated coins"""
        for i, coin in enumerate(coins):
            x, y = coin['center']
            r = coin['radius']
            
            # Use candidate for annotation
            candidate_num = coin.get('candidate_number', i+1)
            color = (0, 255, 0)
            
            # Draw green circle around validated coin
            cv2.circle(image, (x, y), r, color, 3)
            cv2.putText(image, f"#{candidate_num}", (x-40, y-r+65), 
                         cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
            cv2.putText(image, f"V{i+1}", (x-40, y+r-45), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)

    @staticmethod
    def annotate_invalid_coins(image: np.ndarray, coins: List[dict]):
        """Draw red annotations for invalid coins"""
        for coin in coins:
            x, y = coin['center']
            r = coin['radius']
            color = (0, 0, 255)
            
            # Draw red circle around invalid coin
            cv2.circle(image, (x, y), r, color, 5)
            cv2.circle(image, (x, y), 8, color, -1)
            
            # Draw "INVALID" text above the coin
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            thickness = 3
            text = "INVALID"
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = x - text_size[0] // 2
            text_y = y - r + 80
            
            cv2.rectangle(image,
                         (text_x - 10, text_y - text_size[1] - 10),
                         (text_x + text_size[0] + 10, text_y + 10),
                         (255, 255, 255), -1)
            
            cv2.rectangle(image,
                         (text_x - 10, text_y - text_size[1] - 10),
                         (text_x + text_size[0] + 10, text_y + 10),
                         color, 3)
            
            cv2.putText(image, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)
