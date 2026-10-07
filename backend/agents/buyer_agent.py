import numpy as np
import math
from typing import Dict, Any, Optional

class BuyerAgentModel:
    """
    Autonomous Buyer Agent Model for Enterprise Procurement.
    Evaluates proposals and generates counteroffers for ANY SKU, budget, and supplier offer.
    
    Utility Function:
        U_b(p, l, q) = w_p * (1 - (p - p_min)/(p_res - p_min)) 
                     + w_l * (1 - (l - l_min)/(l_max - l_min)) 
                     + w_q * (q / 100)
    """

    def __init__(
        self,
        weight_price: float = 0.50,
        weight_lead_time: float = 0.30,
        weight_quality: float = 0.20,
        concession_beta: float = 2.0,  # >1 Boulware (firm), =1 Linear, <1 Conceder
    ):
        self.w_p = weight_price
        self.w_l = weight_lead_time
        self.w_q = weight_quality
        self.beta = concession_beta

    def compute_utility(
        self,
        price: float,
        lead_time_days: int,
        quality_score: float,
        target_price: float,
        reservation_price: float,
        target_lead_days: int = 7,
        max_lead_days: int = 30
    ) -> float:
        """Computes Buyer utility in [0, 1] for arbitrary offer."""
        p_norm = 1.0 - np.clip((price - target_price) / max(1.0, reservation_price - target_price), 0.0, 1.0)
        l_norm = 1.0 - np.clip((lead_time_days - target_lead_days) / max(1, max_lead_days - target_lead_days), 0.0, 1.0)
        q_norm = np.clip(quality_score / 100.0, 0.0, 1.0)

        utility = (self.w_p * p_norm) + (self.w_l * l_norm) + (self.w_q * q_norm)
        return float(np.round(utility, 4))

    def generate_counteroffer(
        self,
        current_round: int,
        max_rounds: int,
        target_price: float,
        reservation_price: float,
        supplier_offer_price: float,
        target_lead_days: int = 10,
        supplier_lead_days: int = 20,
        force_concession: bool = False
    ) -> Dict[str, Any]:
        """
        Generates mathematically computed counteroffer based on time-dependent concession curve.
        Works for ANY numerical price boundaries and round counts.
        """
        t = min(current_round, max_rounds)
        t_max = max(1, max_rounds)

        if force_concession:
            # Immediate jump toward mid-point
            offered_price = target_price + (supplier_offer_price - target_price) * 0.50
            offered_lead = int(target_lead_days + (supplier_lead_days - target_lead_days) * 0.50)
            message = f"Buyer Agent applied human-in-the-loop concession jump to ${offered_price:.2f}."
        else:
            # Time-dependent concession formula: P(t) = P_min + (P_res - P_min) * (t / t_max)^(1/beta)
            time_decay = math.pow(t / t_max, 1.0 / self.beta)
            price_delta = (reservation_price - target_price) * time_decay
            offered_price = min(reservation_price, target_price + price_delta)
            
            # Lead time adjustment
            lead_delta = int((supplier_lead_days - target_lead_days) * time_decay * 0.6)
            offered_lead = max(target_lead_days, target_lead_days + lead_delta)
            
            message = (
                f"Round {t}/{t_max}: Buyer Agent evaluated target boundary with beta={self.beta}. "
                f"Bidding ${offered_price:.2f}/unit with {offered_lead}-day lead time commitment."
            )

        gap = abs(offered_price - supplier_offer_price)
        converged = gap <= (reservation_price * 0.02) or t >= t_max

        return {
            "round": t,
            "offered_price": round(float(offered_price), 2),
            "offered_lead_time_days": int(offered_lead),
            "price_gap_to_supplier": round(float(gap), 2),
            "is_converged": converged,
            "message": message
        }
