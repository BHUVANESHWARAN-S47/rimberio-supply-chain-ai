import numpy as np
import math
from typing import Dict, Any

class SupplierAgentModel:
    """
    Autonomous Supplier Agent Model representing candidate vendors.
    Protects profit margin, enforces production capacity, and calculates volume discounts
    for ANY arbitrary supplier cost profile and catalog SKU.
    
    Vendor Utility:
        U_s(p, q, l) = w_margin * ((p - c_marginal) / (p_asking - c_marginal))
                     + w_volume * (volume / max_capacity)
                     - w_rush * max(0, (lead_standard - l) / lead_standard)
    """

    def __init__(
        self,
        concession_beta: float = 1.8,
        min_acceptable_margin: float = 0.12  # 12% minimum margin floor
    ):
        self.beta = concession_beta
        self.min_margin = min_acceptable_margin

    def compute_utility(
        self,
        proposed_price: float,
        marginal_cost: float,
        initial_asking_price: float,
        order_quantity: int,
        capacity: int,
        proposed_lead_days: int,
        standard_lead_days: int
    ) -> float:
        """Computes vendor utility for any proposed contract parameters."""
        margin = max(0.0, proposed_price - marginal_cost)
        max_margin = max(1.0, initial_asking_price - marginal_cost)
        margin_score = np.clip(margin / max_margin, 0.0, 1.0)

        vol_score = np.clip(order_quantity / max(1, capacity), 0.0, 1.0)
        rush_penalty = max(0.0, (standard_lead_days - proposed_lead_days) / max(1, standard_lead_days)) * 0.25

        utility = (0.70 * margin_score) + (0.30 * vol_score) - rush_penalty
        return float(np.round(np.clip(utility, 0.0, 1.0), 4))

    def generate_counterproposal(
        self,
        current_round: int,
        max_rounds: int,
        initial_asking_price: float,
        marginal_cost: float,
        buyer_bid_price: float,
        order_quantity: int = 10000,
        standard_lead_days: int = 16
    ) -> Dict[str, Any]:
        """
        Generates dynamic supplier counterproposal for ANY input cost and quantity.
        Enforces profit floor and scales concessions dynamically.
        """
        floor_price = marginal_cost * (1.0 + self.min_margin)
        t = min(current_round, max_rounds)
        t_max = max(1, max_rounds)

        # Volume discount scaling (e.g. 5% discount for bulk > 20,000 units)
        bulk_discount = min(0.08, (order_quantity / 100000.0) * 0.08)
        adjusted_asking = initial_asking_price * (1.0 - bulk_discount)

        # Concession curve from asking down towards floor
        time_decay = math.pow(t / t_max, 1.0 / self.beta)
        allowed_concession = (adjusted_asking - floor_price) * time_decay * 0.75
        counter_price = max(floor_price, adjusted_asking - allowed_concession)

        # Proposed lead days (compromise between rush and standard)
        counter_lead = max(int(standard_lead_days * 0.75), standard_lead_days - int(t * 0.8))

        margin_percent = ((counter_price - marginal_cost) / counter_price) * 100.0

        message = (
            f"Round {t}/{t_max}: Supplier evaluated manufacturing schedule for qty {order_quantity:,}. "
            f"Quoting ${counter_price:.2f}/unit ({margin_percent:.1f}% margin) with {counter_lead}-day fulfillment."
        )

        gap = abs(counter_price - buyer_bid_price)
        accepted = buyer_bid_price >= counter_price

        return {
            "round": t,
            "counter_price": round(float(counter_price), 2),
            "counter_lead_days": int(counter_lead),
            "floor_price": round(float(floor_price), 2),
            "margin_percent": round(float(margin_percent), 1),
            "gap_to_buyer": round(float(gap), 2),
            "accepted": accepted,
            "message": message
        }
