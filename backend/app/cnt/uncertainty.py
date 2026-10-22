import numpy as np
from typing import List, Dict, Any, Tuple
from backend.app.cnt.models import UncertaintyRange


class UncertaintyEngine:
    """Computes empirical quantiles and confidence metrics for stochastic variables.

    Generates strictly reproducible Monte Carlo distributions using dedicated RandomState instances.
    """

    @staticmethod
    def aggregate_distribution(
        values: np.ndarray,
        confidence_nominal: float = 0.90,
    ) -> UncertaintyRange:
        """Computes mean, median, P10, P50, P90, std dev, and extrema."""
        if len(values) == 0:
            return UncertaintyRange(
                mean=0.0,
                median=0.0,
                p10=0.0,
                p50=0.0,
                p90=0.0,
                std_dev=0.0,
                min_val=0.0,
                max_val=0.0,
                confidence=confidence_nominal,
            )

        mean_val = float(np.mean(values))
        median_val = float(np.median(values))
        p10 = float(np.percentile(values, 10))
        p50 = float(np.percentile(values, 50))
        p90 = float(np.percentile(values, 90))
        std_val = float(np.std(values))
        min_v = float(np.min(values))
        max_v = float(np.max(values))

        # Confidence metric decreases slightly if distribution has high variance
        dispersion_ratio = std_val / (abs(mean_val) + 1e-6)
        calibrated_confidence = max(0.50, min(0.99, confidence_nominal - min(0.30, dispersion_ratio * 0.15)))

        return UncertaintyRange(
            mean=round(mean_val, 2),
            median=round(median_val, 2),
            p10=round(p10, 2),
            p50=round(p50, 2),
            p90=round(p90, 2),
            std_dev=round(std_val, 2),
            min_val=round(min_v, 2),
            max_val=round(max_v, 2),
            confidence=round(calibrated_confidence, 2),
        )
