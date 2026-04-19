from statistics import median


class CalibrationScaleEstimator:
    """Estimate pixels/mm in auto/manual calibration modes"""

    def __init__(
        self,
        coin_radii_mm: dict[int, float],
        coin_names: dict[int, str],
        manual_selection_top_k: int,
        auto_outlier_error_threshold: float,
        auto_global_error_weight: float,
    ):
        self.coin_radii_mm = coin_radii_mm
        self.coin_names = coin_names
        self.manual_selection_top_k = manual_selection_top_k
        self.auto_outlier_error_threshold = auto_outlier_error_threshold
        self.auto_global_error_weight = auto_global_error_weight

    def compute_auto(self, valid_coins: list, debug_manager=None) -> float:
        """Auto mode: use all validated coins to estimate pixels/mm with outlier rejection and scoring"""
        if not valid_coins:      
            debug_manager.log("No coin found in image for auto-calibration")
            raise ValueError("No coin found in image for auto-calibration")

        # Auto mode requires at least 3 coins for robust estimation
        if len(valid_coins) < 3:
            debug_manager.log("Auto-calibration needs at least 3 validated coins for robust estimation")
            raise ValueError("Not enough validated coins for auto-calibration")

        # Estimate pixels/mm using all candidates and select best fit with outlier rejection
        new_pixels_per_mm = self._estimate_auto(valid_coins, debug_manager)
        if not new_pixels_per_mm:
            raise ValueError("Could not estimate pixels/mm from validated coins")

        return new_pixels_per_mm

    def compute_manual(self, valid_coins: list, coin_value: int, debug_manager=None) -> tuple[float, float, float]:
        """Manual mode: use selected reference coin to compute pixels/mm directly from its radius"""
        if not valid_coins:            
            debug_manager.log("No coin found in image for calibration")
            raise ValueError("No coin found in image for calibration")

        # Manual mode requires at least 1 validated coin to select reference from
        calibrated_coin = self._select_manual_candidate(valid_coins, coin_value, debug_manager)
        if calibrated_coin is None:
            raise ValueError("No candidate selected for manual calibration")

        # Compute pixels/mm from selected candidate's radius and known real-world radius
        calibrated_radius_px = float(calibrated_coin["radius"])
        real_radius_mm = float(self.coin_radii_mm[coin_value])
        new_pixels_per_mm = calibrated_radius_px / real_radius_mm
        return new_pixels_per_mm, calibrated_radius_px, real_radius_mm

    def _select_manual_candidate(self, valid_coins: list, coin_value: int, debug_manager=None):
        """Select candidate for manual calibration based on scoring of radius fit to selected coin value"""
        if not valid_coins:
            return None

        selected_radius_mm = self.coin_radii_mm[coin_value]
        detected_radii_px = [float(c["radius"]) for c in valid_coins if c.get("radius")]
        if not detected_radii_px:
            return None

        # Score candidates based on how well their radius would fit the selected coin value at some pixels/mm scale
        scored_candidates = []
        for candidate in valid_coins:
            # Only consider candidates with valid radius for scoring
            radius_px = float(candidate.get("radius", 0.0))
            if radius_px <= 0:
                continue

            # Hypothesize pixels/mm scale that would map the candidate's radius to the selected coin's real-world radius
            hypothesis_scale = radius_px / selected_radius_mm
            # Score how well this scale would fit all detected radii to their nearest coin values
            score = self._score_scale(hypothesis_scale, detected_radii_px)
            if score is None:
                continue

            scored_candidates.append((score, candidate, hypothesis_scale))

        # Select candidate with best score (lowest) among top K hypotheses, using radius as tiebreaker
        if scored_candidates:
            scored_candidates.sort(key=lambda item: item[0])
            shortlist = scored_candidates[:max(1, self.manual_selection_top_k)]
            selected = sorted(shortlist, key=lambda item: item[1]["radius"])[len(shortlist) // 2]
            selected_score, selected_candidate, selected_scale = selected
            
            debug_manager.log("Manual calibration candidate selection (scale-fit based):")
            debug_manager.log(f"   Candidate hypotheses scored: {len(scored_candidates)}")
            debug_manager.log(f"   Shortlist size: {len(shortlist)}")
            debug_manager.log(f"   Selected score: {selected_score * 100:.2f}%")
            debug_manager.log(f"   Selected hypothesis pixels/mm: {selected_scale:.2f}")
            debug_manager.log(
                f"   Selected candidate #{selected_candidate.get('number', '?')} "
                f"with radius {selected_candidate['radius']}px"
            )

            return selected_candidate

        # Fallback to median-radius candidate
        fallback = sorted(valid_coins, key=lambda c: c["radius"])[len(valid_coins) // 2]
                
        debug_manager.log("Manual calibration fallback: no scoreable hypotheses; selected median-radius candidate")
        debug_manager.log(f"   Selected candidate #{fallback.get('number', '?')} with radius {fallback['radius']}px")

        return fallback

    def _estimate_auto(self, valid_coins: list, debug_manager=None) -> float | None:
        """Estimate pixels/mm by scoring how well different scale hypotheses fit all validated candidates to known coin sizes"""
        if not valid_coins:
            return None

        known_radii_mm = list(self.coin_radii_mm.values())
        detected_radii_px = [float(c["radius"]) for c in valid_coins if c.get("radius")]
        if not detected_radii_px:
            return None

        # Generate candidate scales from all combinations of detected radii and known coin radii
        candidate_scales = []
        for radius_px in detected_radii_px:
            for radius_mm in known_radii_mm:
                candidate_scales.append(radius_px / radius_mm)

        best_scale = None
        best_score = float("inf")

        # Score each candidate scale and select the best one with outlier rejection
        for scale in candidate_scales:
            score = self._score_scale(scale, detected_radii_px)
            if score is None:
                continue
            if score < best_score:
                best_score = score
                best_scale = scale

        if best_scale is None:
            return None

        # Refine the best scale by keeping only inliers within error threshold and taking their median
        refined_scale, inlier_scales = self._refine_scale(best_scale, detected_radii_px)
        
        debug_manager.log("Auto-calibration scoring complete")
        debug_manager.log(f"   Valid candidates used: {len(detected_radii_px)}")
        debug_manager.log(f"   Scale hypotheses tested: {len(candidate_scales)}")
        debug_manager.log(f"   Best fit score: {best_score * 100:.2f}%")
        debug_manager.log(f"   Initial estimate pixels/mm: {best_scale:.2f}")
        debug_manager.log(f"   Inlier threshold: {self.auto_outlier_error_threshold * 100:.1f}%")
        debug_manager.log(f"   Inliers kept for refinement: {len(inlier_scales)}/{len(detected_radii_px)}")
        debug_manager.log(f"   Refined pixels/mm: {refined_scale:.2f}")

        debug_manager.log("   Candidate mapping at best scale:")
        for idx, radius_px in enumerate(detected_radii_px, 1):
            radius_mm_est = radius_px / refined_scale
            nearest_value, nearest_mm = min(
                self.coin_radii_mm.items(),
                key=lambda item, est=radius_mm_est: abs(est - item[1]),
            )
            coin_name = self.coin_names[nearest_value]
            debug_manager.log(
                f"      #{idx}: {radius_px:.1f}px -> {radius_mm_est:.2f}mm ~ {coin_name} ({nearest_mm:.3f}mm)"
         )

        return refined_scale

    def _score_scale(self, scale: float, detected_radii_px: list[float]) -> float | None:
        """Score a pixels/mm scale hypothesis by computing average relative error of all detected radii to their nearest known coin sizes at that scale"""
        rel_errors = []
        rel_errors_by_value = {value: [] for value in self.coin_radii_mm.keys()}

        # Score each detected radius by how well it would fit to its nearest known coin radius at the given scale
        for radius_px in detected_radii_px:
            radius_mm_est = radius_px / scale
            nearest_value, nearest_mm = min(
                self.coin_radii_mm.items(),
                key=lambda item, est=radius_mm_est: abs(est - item[1]),
            )
            # Compute relative error and accumulate for overall score and per-coin-value analysis
            rel_error = abs(radius_mm_est - nearest_mm) / nearest_mm
            rel_errors.append(rel_error)
            rel_errors_by_value[nearest_value].append(rel_error)

        # Compute overall score as weighted combination of average relative error across all candidates and average of per-coin-value median errors
        per_denom_medians = [median(errors) for errors in rel_errors_by_value.values() if errors]
        if not per_denom_medians:
            return None

        # Combine overall median error with global median error, weighted by configured parameter, to get final score for this scale hypothesis
        return (
            (1.0 - self.auto_global_error_weight) * (sum(per_denom_medians) / len(per_denom_medians))
            + self.auto_global_error_weight * (sum(rel_errors) / len(rel_errors))
        )

    def _refine_scale(self, initial_scale: float, detected_radii_px: list[float]) -> tuple[float, list[float]]:
        """Refine the initial scale estimate by keeping only inliers within error threshold and taking their median as final estimate"""
        inlier_scales = []

        # Keep only candidates whose radius would fit to a known coin size within the configured relative error threshold at the initial scale estimate
        for radius_px in detected_radii_px:
            radius_mm_est = radius_px / initial_scale
            _, nearest_mm = min(
                self.coin_radii_mm.items(),
                key=lambda item, est=radius_mm_est: abs(est - item[1]),
            )
            # Compute relative error and keep as inlier if within threshold
            rel_error = abs(radius_mm_est - nearest_mm) / nearest_mm
            if rel_error <= self.auto_outlier_error_threshold:
                inlier_scales.append(radius_px / nearest_mm)

        # Take median of inlier scales as refined estimate
        refined_scale = median(inlier_scales) if inlier_scales else initial_scale
        return refined_scale, inlier_scales
