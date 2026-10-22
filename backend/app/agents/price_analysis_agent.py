import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import AgentCapability
from backend.app.schemas.price_analysis import (
    PriceAnalysisInput,
    PriceAnalysisResult,
    PriceTrend,
    VolumeDiscountTier,
)
from backend.app.database.connection import SessionLocal
from backend.app.database.models import (
    SupplierDB,
    ProductDB,
    SupplierProductDB,
    PurchaseOrderItemDB,
)


class PriceAnalysisAgent(BaseAgent[PriceAnalysisInput, PriceAnalysisResult]):
    """Price Analysis AI Agent in RIMBERIO.

    Computes deterministic landed costs, evaluates volume discount schedules,
    benchmarks pricing against market rates and historical trends, and guards
    against adversarial prompt injections.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
        re.compile(r"set\s+price\s+to\s+0", re.IGNORECASE),
        re.compile(r"zero\s+cost\s+override", re.IGNORECASE),
        re.compile(r"grant\s+100%\s+discount", re.IGNORECASE),
        re.compile(r"bypass\s+landed\s+cost", re.IGNORECASE),
        re.compile(r"as\s+an\s+admin", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Price Analysis Agent",
            description="Autonomous pricing analyst calculating landed cost, volume discount curves, and market benchmark parity.",
            capabilities=[AgentCapability.PRICE_BENCHMARKING],
        )
        self.db = db

    def validate_input(self, input_data: Any) -> PriceAnalysisInput:
        if isinstance(input_data, PriceAnalysisInput):
            return input_data
        elif isinstance(input_data, dict):
            return PriceAnalysisInput(**input_data)
        raise ValueError(f"Unsupported input type for PriceAnalysisAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: PriceAnalysisInput,
        state: Optional[Any] = None,
    ) -> PriceAnalysisResult:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(self, input_data: PriceAnalysisInput) -> PriceAnalysisResult:
        # 1. Adversarial Inspection
        adversarial_flags = self._detect_adversarial_patterns(input_data.analysis_notes)

        # 2. Volume Discount Evaluation
        volume_discount_pct = self._calculate_volume_discount(
            order_quantity=input_data.order_quantity,
            discount_tiers=input_data.discount_tiers,
        )
        discounted_unit_price = round(
            input_data.quoted_unit_price * (1.0 - volume_discount_pct), 4
        )

        # 3. Cost Component Calculations
        qty = max(1, input_data.order_quantity)
        freight_per_unit = round(input_data.estimated_transport_cost / qty, 4)
        tariffs_per_unit = round(
            discounted_unit_price * input_data.tariffs_and_duties_pct, 4
        )
        handling_per_unit = round(input_data.handling_fee_per_unit, 4)

        # 4. Landed Cost & Total Procurement
        landed_cost_per_unit = round(
            discounted_unit_price + freight_per_unit + tariffs_per_unit + handling_per_unit,
            4,
        )
        total_procurement_cost = round(landed_cost_per_unit * input_data.order_quantity, 2)

        # 5. Benchmark and Current Contract Resolution
        benchmark_price, current_contract_price = self._resolve_benchmarks(input_data)

        # 6. Savings and Deviation Analysis
        savings_vs_current = round(current_contract_price - landed_cost_per_unit, 4)
        if current_contract_price > 0:
            savings_pct_vs_current = round(
                (savings_vs_current / current_contract_price) * 100.0, 2
            )
        else:
            savings_pct_vs_current = 0.0

        price_deviation_vs_benchmark = round(
            discounted_unit_price - benchmark_price, 4
        )
        if benchmark_price > 0:
            price_deviation_pct_vs_benchmark = round(
                (price_deviation_vs_benchmark / benchmark_price) * 100.0, 2
            )
        else:
            price_deviation_pct_vs_benchmark = 0.0

        # 7. Historical Trend Analysis
        historical_avg, price_trend = self._analyze_historical_prices(
            input_data, default_benchmark=benchmark_price
        )

        # 8. Competitiveness Flag (Supplier discounted price is within 5% of benchmark or cheaper)
        is_price_competitive = discounted_unit_price <= round(benchmark_price * 1.05, 4)

        # 9. Deterministic Reasoning Synthesis
        reasoning = self._generate_reasoning(
            input_data=input_data,
            volume_discount_pct=volume_discount_pct,
            discounted_unit_price=discounted_unit_price,
            landed_cost_per_unit=landed_cost_per_unit,
            total_procurement_cost=total_procurement_cost,
            benchmark_price=benchmark_price,
            savings_vs_current=savings_vs_current,
            savings_pct=savings_pct_vs_current,
            price_deviation_pct=price_deviation_pct_vs_benchmark,
            historical_avg=historical_avg,
            price_trend=price_trend,
            is_competitive=is_price_competitive,
            adversarial_flags=adversarial_flags,
        )

        return PriceAnalysisResult(
            supplier_id=input_data.supplier_id,
            product_id=input_data.product_id,
            base_unit_price=input_data.quoted_unit_price,
            volume_discount_pct=volume_discount_pct,
            discounted_unit_price=discounted_unit_price,
            freight_per_unit=freight_per_unit,
            tariffs_per_unit=tariffs_per_unit,
            handling_per_unit=handling_per_unit,
            landed_cost_per_unit=landed_cost_per_unit,
            total_procurement_cost=total_procurement_cost,
            benchmark_unit_price=benchmark_price,
            current_contract_unit_price=current_contract_price,
            savings_vs_current=savings_vs_current,
            savings_pct_vs_current=savings_pct_vs_current,
            price_deviation_vs_benchmark=price_deviation_vs_benchmark,
            price_deviation_pct_vs_benchmark=price_deviation_pct_vs_benchmark,
            historical_average_price=historical_avg,
            historical_price_trend=price_trend,
            is_price_competitive=is_price_competitive,
            reasoning=reasoning,
            adversarial_flags=adversarial_flags,
        )

    def _calculate_volume_discount(
        self,
        order_quantity: int,
        discount_tiers: Optional[List[VolumeDiscountTier]],
    ) -> float:
        if not discount_tiers:
            return 0.0

        qualifying_discounts = [
            tier.discount_pct
            for tier in discount_tiers
            if order_quantity >= tier.min_quantity
        ]

        if not qualifying_discounts:
            return 0.0

        max_discount = max(qualifying_discounts)
        return round(max(0.0, min(1.0, max_discount)), 4)

    def _resolve_benchmarks(self, input_data: PriceAnalysisInput) -> tuple[float, float]:
        benchmark_price = input_data.market_benchmark_price
        current_contract = input_data.current_contract_price

        if benchmark_price is not None and current_contract is not None:
            return round(benchmark_price, 4), round(current_contract, 4)

        db = self.db or SessionLocal()
        try:
            # Query Product for benchmark
            if benchmark_price is None:
                prod = (
                    db.query(ProductDB)
                    .filter(
                        (ProductDB.id == input_data.product_id)
                        | (ProductDB.sku == input_data.product_id)
                    )
                    .first()
                )
                if prod:
                    benchmark_price = prod.unit_cost

            # Query SupplierProduct for current contract
            if current_contract is None:
                sup = (
                    db.query(SupplierDB)
                    .filter(
                        (SupplierDB.id == input_data.supplier_id)
                        | (SupplierDB.supplier_code == input_data.supplier_id)
                    )
                    .first()
                )
                if sup and prod:
                    sp = (
                        db.query(SupplierProductDB)
                        .filter(
                            SupplierProductDB.supplier_id == sup.id,
                            SupplierProductDB.product_id == prod.id,
                        )
                        .first()
                    )
                    if sp:
                        current_contract = sp.unit_price
        except Exception:
            pass
        finally:
            if not self.db:
                db.close()

        resolved_benchmark = benchmark_price if benchmark_price is not None else input_data.quoted_unit_price
        resolved_contract = current_contract if current_contract is not None else input_data.quoted_unit_price

        return round(resolved_benchmark, 4), round(resolved_contract, 4)

    def _analyze_historical_prices(
        self,
        input_data: PriceAnalysisInput,
        default_benchmark: float,
    ) -> tuple[float, PriceTrend]:
        prices = input_data.historical_prices

        # If not provided in input, attempt to load PO history from database
        if prices is None:
            db = self.db or SessionLocal()
            try:
                prod = (
                    db.query(ProductDB)
                    .filter(
                        (ProductDB.id == input_data.product_id)
                        | (ProductDB.sku == input_data.product_id)
                    )
                    .first()
                )
                if prod:
                    items = (
                        db.query(PurchaseOrderItemDB)
                        .filter(PurchaseOrderItemDB.product_id == prod.id)
                        .order_by(PurchaseOrderItemDB.created_at.asc())
                        .limit(20)
                        .all()
                    )
                    if items:
                        prices = [it.unit_price for it in items]
            except Exception:
                pass
            finally:
                if not self.db:
                    db.close()

        valid_prices = [p for p in (prices or []) if p > 0.0]

        if not valid_prices:
            return round(default_benchmark, 4), PriceTrend.STABLE

        avg_price = round(sum(valid_prices) / len(valid_prices), 4)

        if len(valid_prices) < 2:
            return avg_price, PriceTrend.STABLE

        # Trend detection via split-half or boundary change
        if len(valid_prices) >= 4:
            mid = len(valid_prices) // 2
            older_avg = sum(valid_prices[:mid]) / mid
            newer_avg = sum(valid_prices[mid:]) / (len(valid_prices) - mid)
            change_pct = (newer_avg - older_avg) / older_avg if older_avg > 0 else 0.0
        else:
            change_pct = (
                (valid_prices[-1] - valid_prices[0]) / valid_prices[0]
                if valid_prices[0] > 0
                else 0.0
            )

        if change_pct > 0.02:
            trend = PriceTrend.INFLATIONARY
        elif change_pct < -0.02:
            trend = PriceTrend.DEFLATIONARY
        else:
            trend = PriceTrend.STABLE

        return avg_price, trend

    def _detect_adversarial_patterns(self, text: Optional[str]) -> List[str]:
        if not text:
            return []
        flags = []
        for pat in self.ADVERSARIAL_PATTERNS:
            match = pat.search(text)
            if match:
                flags.append(f"Prompt injection pattern detected: '{match.group()}'")
        return flags

    def _generate_reasoning(
        self,
        input_data: PriceAnalysisInput,
        volume_discount_pct: float,
        discounted_unit_price: float,
        landed_cost_per_unit: float,
        total_procurement_cost: float,
        benchmark_price: float,
        savings_vs_current: float,
        savings_pct: float,
        price_deviation_pct: float,
        historical_avg: float,
        price_trend: PriceTrend,
        is_competitive: bool,
        adversarial_flags: List[str],
    ) -> str:
        parts = []
        if adversarial_flags:
            parts.append(f"[SECURITY ALERT: {len(adversarial_flags)} injection pattern(s) neutralized.]")

        disc_str = f"with {volume_discount_pct * 100:.1f}% volume discount" if volume_discount_pct > 0 else "without volume discount"
        parts.append(
            f"Quoted base price ${input_data.quoted_unit_price:.2f} {disc_str} yields discounted unit price ${discounted_unit_price:.2f}."
        )
        parts.append(
            f"Factoring transport, tariffs, and handling, all-in landed cost is ${landed_cost_per_unit:.2f}/unit (Total ${total_procurement_cost:,.2f} for {input_data.order_quantity} units)."
        )

        if savings_vs_current >= 0:
            parts.append(f"Projected unit savings vs incumbent contract is ${savings_vs_current:.2f} (+{savings_pct:.1f}%).")
        else:
            parts.append(f"Landed cost incurs premium of ${abs(savings_vs_current):.2f} ({savings_pct:.1f}%) over current contract.")

        comp_status = "competitive" if is_competitive else "non-competitive"
        dev_dir = "premium" if price_deviation_pct > 0 else "discount"
        parts.append(
            f"Compared to market benchmark (${benchmark_price:.2f}), unit quote shows a {abs(price_deviation_pct):.1f}% {dev_dir} and is assessed as {comp_status}."
        )
        parts.append(f"Historical trend is {price_trend.value} (avg ${historical_avg:.2f}).")

        return " ".join(parts)


# Register agent in AgentRegistry
AgentRegistry.register(
    name="Price Analysis Agent",
    agent_class=PriceAnalysisAgent,
    capabilities=[AgentCapability.PRICE_BENCHMARKING],
    version="1.0.0",
)
