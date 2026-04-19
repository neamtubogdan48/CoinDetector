import io
import os
import shutil
import time
import traceback
from typing import Dict, List


class DebugManager:
    """Handles debug output, logging, and file management"""

    _CURRENCY_UNITS = {
        "RON": ("leu", "lei", "ban", "bani"),
        "EUR": ("euro", "euro", "cent", "cents"),
        "USD": ("dollar", "dollars", "cent", "cents"),
        "GBP": ("pound", "pounds", "penny", "pence"),
    }

    def __init__(self, debug_mode: bool = False, debug_folder: str = None):
        self.debug_mode = debug_mode
        if debug_folder is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.debug_folder = os.path.join(root_dir, "debug")
        else:
            self.debug_folder = debug_folder
        self.summary_file_path = ""

    def setup(self) -> bool:
        """Configure debug environment"""
        if not self.debug_mode:
            return True

        # Ensure debug folder exists and is empty
        try:
            if not os.path.exists(self.debug_folder):
                os.makedirs(self.debug_folder)
                self.log(f"Created debug folder: {self.debug_folder}")
            else:
                self.clear_folder(self.debug_folder)
                self.log(f"Cleared existing debug folder: {self.debug_folder}")

            # Initialize detection summary file
            self.summary_file_path = self.init_detection_summary()
            return True
        except Exception as exc:
            print(f"Error setting up debug: {exc}")
            return False

    def log(self, message: str):
        """Write message to log file if debug mode is enabled"""
        if not self.debug_mode:
            return

        if self.summary_file_path:
            with open(self.summary_file_path, "a", encoding="utf-8") as file_obj:
                file_obj.write(message + "\n")

    @staticmethod
    def start_timer() -> float:
        return time.perf_counter()

    def log_operation_duration(self, operation_name: str, start_time: float):
        elapsed_seconds = time.perf_counter() - start_time
        self.log("")
        self.log(f"{operation_name} duration: {elapsed_seconds:.3f}s")

    def log_error(self, error: Exception, args_debug: bool = False):
        """Log error with optional traceback."""
        error_msg = f"Error: {error}"
        self.log(error_msg)

        if args_debug and self.debug_mode:
            traceback_str = io.StringIO()
            traceback.print_exc(file=traceback_str)
            self.log(traceback_str.getvalue())

        if not self.debug_mode:
            print(error_msg)

    def clear_folder(self, folder_path: str):
        """Clear all contents from folder"""
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as exc:
                    if self.summary_file_path:
                        with open(self.summary_file_path, "a", encoding="utf-8") as file_obj:
                            file_obj.write(f"Failed to delete {file_path}. Reason: {exc}\n")

    def init_detection_summary(self) -> str:
        """Initialize detection summary file and return file path"""
        summary_file_path = os.path.join(self.debug_folder, "00_detection_summary.txt")
        open(summary_file_path, "w", encoding="utf-8").close()
        return summary_file_path

    def save_detailed_summary(self, results: Dict, detector_params: Dict, all_candidates: List = None):
        """Save detailed processing information to summary file"""
        try:
            self._log_detector_parameters(detector_params)
            self._log_candidate_details(all_candidates)
            self._log_final_statistics(results)
        except Exception as exc:
            self.log_error(exc)

    def _log_detector_parameters(self, detector_params: Dict):
        self.log("\nDetection parameters:")
        self.log(f"   Min/max radius: {detector_params['min_radius']}/{detector_params['max_radius']} px")
        self.log(f"   Blur kernel: {detector_params['blur_kernel']}")
        self.log(f"   HoughCircles param1/param2: {detector_params['hough_param1']}/{detector_params['hough_param2']}")

        if "analyser" in detector_params:
            specs = detector_params["analyser"]
            self.log("\nCoin specifications:")
            self.log(f"   Currency: {getattr(specs, 'currency_code', 'RON')}")
            ppm = getattr(specs, 'pixels_per_mm', None)
            ppm_text = f"{ppm:.2f}" if ppm is not None else "unset"
            self.log(f"   Pixels per mm: {ppm_text}")
            self.log(f"   Tolerance: +/-{specs.tolerance_mm}mm")
            radii = getattr(specs, 'coin_radii_mm', {})
            names = getattr(specs, 'coin_names', {})
            if radii:
                formatted = ", ".join(
                    f"{names.get(value, value)}={radius:.3f}mm"
                    for value, radius in sorted(radii.items())
                )
                self.log(f"   Coin radii: {formatted}")

    def _log_candidate_details(self, all_candidates: List):
        self.log("")
        if not all_candidates:
            return

        self.log("Candidate validation details:")
        for candidate in all_candidates:
            radius_mm = candidate.get('radius_mm', None)
            radius_mm_text = f"{radius_mm:.1f}" if radius_mm is not None else "n/a"
            self.log(
                f"    Candidate #{candidate['number']}: Radius {candidate['radius']}px ({radius_mm_text}mm)"
            )

            overlap_reason = candidate.get("overlap_reason", None)
            self.log(f"        Overlap: {overlap_reason if overlap_reason else 'N/A'}")

            orb_reason = candidate.get("orb_reason", None)
            self.log(f"        ORB: {orb_reason if orb_reason else 'N/A'}")

            distance_reason = candidate.get("distance_reason", None)
            self.log(f"        Distance: {distance_reason if distance_reason else 'N/A'}")

            overlap_passed = candidate.get("overlap_passed")
            orb_passed = candidate.get("orb_passed")
            distance_passed = candidate.get("distance_passed")
            if overlap_passed and orb_passed and distance_passed:
                self.log("        Result: VALIDATED")
            else:
                self.log("        Result: REJECTED")
            self.log("")

    def _log_final_statistics(self, results: Dict):
        coin_names = results.get("coin_names", {})
        currency_code = results.get("currency_code", "")
        if results["total_count"] > 0:
            self.log("Detected coins:")
            for index, coin in enumerate(results["coins"], 1):
                radius_mm = coin.get("radius_mm", 0)
                coin_label = coin.get("coin_type") or coin_names.get(coin['value'], str(coin['value']))
                self.log(f"   {index}. {coin_label}, radius: {coin['radius']}px ({radius_mm:.1f}mm)")
            self.log("")

            invalid_coins = results.get("invalid_coins", [])
            if invalid_coins:
                self.log(f"Invalid coins: {len(invalid_coins)}")
                self.log("")

            self.log("Final Statistics:")
            formatted_total = self._format_total_value(results["total_value"], currency_code)
            
            self.log(f"   - Total value: {formatted_total}")
            for value in sorted(results.get("count_by_value", {}).keys(), reverse=True):
                count = results["count_by_value"].get(value, 0)
                if count > 0:
                    label = coin_names.get(value, str(value))
                    self.log(f"   - {label}: {count} {self._format_piece_word(count)}")

    @staticmethod
    def _format_piece_word(count: int) -> str:
        return "piece" if count == 1 else "pieces"

    @staticmethod
    def _format_total_value(total_value: int, currency_code: str) -> str:
        """Format total value into major/minor currency units"""
        code = (currency_code or "RON").upper()
        units = DebugManager._CURRENCY_UNITS.get(code, DebugManager._CURRENCY_UNITS["RON"])
        
        return DebugManager._format_major_minor_value(
            total_value,
            major_singular=units[0],
            major_plural=units[1],
            minor_singular=units[2],
            minor_plural=units[3],
        )

    @staticmethod
    def _format_major_minor_value(
        total_value: int,
        major_singular: str,
        major_plural: str,
        minor_singular: str,
        minor_plural: str,
    ) -> str:
        """Formats a total value into major and minor currency units"""
        major_divisor = 100
        if total_value >= major_divisor:
            major = total_value // major_divisor
            minor = total_value % major_divisor
            major_word = major_singular if major == 1 else major_plural
            
            if minor == 0:
                return f"{major} {major_word}"
            
            minor_word = minor_singular if minor == 1 else minor_plural
            return f"{major} {major_word} and {minor} {minor_word}"

        minor_word = minor_singular if total_value == 1 else minor_plural
        return f"{total_value} {minor_word}"
