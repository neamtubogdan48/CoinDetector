import numpy as np

from typing import List, Dict
from utils.image_utils import ImageAnnotator


class ResultsManager:
    """Results construction and formatting"""
    
    @staticmethod
    def empty_results(image: np.ndarray) -> Dict:
        """Return empty result structure"""
        
        return {
            'total_count': 0,
            'coins': [],
            'image_with_annotations': image.copy(),
            'total_value': 0,
            'count_by_value': {},
        }

    @staticmethod
    def build_results(
        image: np.ndarray,
        coins: List[Dict],
        all_candidates: List[Dict] = None,
        draw_total_value: bool = False,
    ) -> Dict:
        """Build final results with annotations"""
        
        # Initialize results structure
        results = {
            'coins': [],
            'count_by_value': {},
            'total_count': 0,
            'total_value': 0,
            'image_with_annotations': image.copy()
        }
        
        # Populate coin details and annotations
        for i, coin in enumerate(coins):
            coin_data = {
                'id': i + 1,
                'value': coin['value'],
                'center': coin['center'],
                'radius': coin['radius'],
                'radius_mm': coin.get('radius_mm', 0),
                'coin_type': coin.get('coin_type', str(coin.get('value', ''))),
                'diameter_pixels': 2 * coin['radius'],
                'diameter_mm': 2 * coin.get('radius_mm', 0)
            }
            
            # Append coin data to results
            results['coins'].append(coin_data)

            # Update counts and total value
            value = coin['value']
            results['count_by_value'][value] = results['count_by_value'].get(value, 0) + 1
            results['total_count'] += 1
            results['total_value'] += value

            # Draw annotations on image
            ImageAnnotator.draw_large_annotation(
                results['image_with_annotations'],
                coin['center'],
                coin['radius'],
                coin['value'],
                coin.get('candidate_number'),
                coin_label=coin.get('coin_type', str(coin.get('value', ''))),
            )
            
        # Annotate invalid coins if candidates provided
        invalid_coins = [c for c in all_candidates if not c.get('validated')]
        ImageAnnotator.annotate_invalid_coins(results['image_with_annotations'], invalid_coins)

        # Draw total value on image if debug mode enabled
        if draw_total_value:
            ImageAnnotator.draw_total_value(results['image_with_annotations'], results['total_value'])
        
        return results
