"""
WealthBridge Proprietary Credit Scoring Engine.
Calculates business credit scores from tradeline data.
"""
from typing import List
from decimal import Decimal
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.tradeline import Tradeline, PaymentStatus, AccountType, CreditReport, TradelineStatus


class WealthBridgeScoringEngine:
    """
    Proprietary business credit scoring algorithm.
    Score range: 0-100 (higher is better)
    
    Weighting (configurable in .env):
    - Payment History: 35%
    - Credit Utilization: 30%
    - Credit Age: 15%
    - Credit Mix: 10%
    - New Credit: 10%
    """
    
    def __init__(self):
        # Default weights if config not loaded
        self.weight_payment_history = 0.35
        self.weight_utilization = 0.30
        self.weight_age = 0.15
        self.weight_mix = 0.10
        self.weight_new_credit = 0.10
    
    def calculate_score(self, tradelines: List[Tradeline]) -> int:
        """
        Calculate composite credit score from tradelines.
        
        Args:
            tradelines: List of Tradeline objects
        
        Returns:
            Score from 0-100
        """
        if not tradelines:
            return 0
        
        # Calculate component scores
        payment_score = self._calculate_payment_history_score(tradelines)
        utilization_score = self._calculate_utilization_score(tradelines)
        age_score = self._calculate_age_score(tradelines)
        mix_score = self._calculate_mix_score(tradelines)
        new_credit_score = self._calculate_new_credit_score(tradelines)
        
        # Weighted composite
        composite = (
            payment_score * self.weight_payment_history +
            utilization_score * self.weight_utilization +
            age_score * self.weight_age +
            mix_score * self.weight_mix +
            new_credit_score * self.weight_new_credit
        )
        
        return int(round(composite))
    
    def _calculate_payment_history_score(self, tradelines: List[Tradeline]) -> float:
        """Payment history component (35%)."""
        total_payments = 0
        on_time_payments = 0
        late_30_count = 0
        late_60_count = 0
        late_90_plus_count = 0
        
        for tl in tradelines:
            for status in tl.payment_history:
                total_payments += 1
                if status == PaymentStatus.CURRENT:
                    on_time_payments += 1
                elif status == PaymentStatus.LATE_30:
                    late_30_count += 1
                elif status == PaymentStatus.LATE_60:
                    late_60_count += 1
                elif status in [PaymentStatus.LATE_90, PaymentStatus.LATE_120]:
                    late_90_plus_count += 1
        
        if total_payments == 0:
            return 50.0
        
        on_time_pct = on_time_payments / total_payments
        base_score = on_time_pct * 100
        
        penalty = (
            late_30_count * 2 +
            late_60_count * 5 +
            late_90_plus_count * 10
        )
        
        score = max(0, base_score - penalty)
        return min(100, score)
    
    def _calculate_utilization_score(self, tradelines: List[Tradeline]) -> float:
        """Credit utilization component (30%)."""
        total_limit = Decimal(0)
        total_balance = Decimal(0)
        
        for tl in tradelines:
            if tl.account_type in [AccountType.REVOLVING, AccountType.COMMERCIAL]:
                total_limit += tl.credit_limit
                total_balance += tl.current_balance
        
        if total_limit == 0:
            return 50.0
        
        utilization = float(total_balance / total_limit)
        
        if utilization <= 0.10:
            return 100.0
        elif utilization <= 0.30:
            return 90.0
        elif utilization <= 0.50:
            return 70.0
        elif utilization <= 0.75:
            return 50.0
        else:
            return max(0, 100 - (utilization * 100))
    
    def _calculate_age_score(self, tradelines: List[Tradeline]) -> float:
        """Credit age component (15%)."""
        if not tradelines:
            return 0.0
        
        ages = [tl.account_age_days() for tl in tradelines]
        average_age_days = sum(ages) / len(ages)
        oldest_age_days = max(ages)
        
        average_age_months = average_age_days / 30
        oldest_age_months = oldest_age_days / 30
        
        avg_score = min(100, (average_age_months / 60) * 100)
        oldest_score = min(100, (oldest_age_months / 120) * 100)
        
        return (avg_score * 0.6) + (oldest_score * 0.4)
    
    def _calculate_mix_score(self, tradelines: List[Tradeline]) -> float:
        """Credit mix component (10%)."""
        account_types = set(tl.account_type for tl in tradelines)
        type_count = len(account_types)
        
        if type_count >= 3:
            return 100.0
        elif type_count == 2:
            return 75.0
        elif type_count == 1:
            return 50.0
        else:
            return 0.0
    
    def _calculate_new_credit_score(self, tradelines: List[Tradeline]) -> float:
        """New credit component (10%)."""
        new_accounts = [
            tl for tl in tradelines
            if tl.account_age_days() < 180
        ]
        
        new_count = len(new_accounts)
        total_count = len(tradelines)
        
        if total_count == 0:
            return 50.0
        
        new_ratio = new_count / total_count
        
        if new_ratio == 0:
            return 100.0
        elif new_ratio <= 0.2:
            return 80.0
        elif new_ratio <= 0.4:
            return 60.0
        elif new_ratio <= 0.6:
            return 40.0
        else:
            return 20.0
    
    def generate_report(self, tradelines: List[Tradeline], business_id: str) -> CreditReport:
        """Generate comprehensive credit report with score and analysis."""
        active_tradelines = [tl for tl in tradelines if tl.status == TradelineStatus.ACTIVE]
        
        total_limit = sum(tl.credit_limit for tl in active_tradelines)
        total_balance = sum(tl.current_balance for tl in active_tradelines)
        available_credit = total_limit - total_balance
        
        utilization = float(total_balance / total_limit * 100) if total_limit > 0 else 0
        
        total_payments = sum(len(tl.payment_history) for tl in tradelines)
        on_time = sum(
            sum(1 for p in tl.payment_history if p == PaymentStatus.CURRENT)
            for tl in tradelines
        )
        on_time_pct = (on_time / total_payments * 100) if total_payments > 0 else 0
        
        delinquent = len([tl for tl in active_tradelines if tl.is_delinquent()])
        
        if tradelines:
            ages = [tl.account_age_days() / 30 for tl in tradelines]
            oldest_age = int(max(ages))
            avg_age = int(sum(ages) / len(ages))
        else:
            oldest_age = 0
            avg_age = 0
        
        score = self.calculate_score(tradelines)
        
        risk_factors = self._identify_risk_factors(tradelines, utilization, delinquent)
        positive_factors = self._identify_positive_factors(tradelines, utilization, on_time_pct)
        recommendations = self._generate_recommendations(tradelines, utilization, score)
        
        return CreditReport(
            report_id=f"RPT-{business_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            business_id=business_id,
            report_date=datetime.now(),
            total_tradelines=len(tradelines),
            active_tradelines=len(active_tradelines),
            total_credit_limit=total_limit,
            total_balance=total_balance,
            total_available_credit=available_credit,
            overall_utilization=utilization,
            on_time_payments_pct=on_time_pct,
            delinquent_accounts=delinquent,
            collections_count=0,
            oldest_tradeline_age_months=oldest_age,
            average_account_age_months=avg_age,
            wealthbridge_score=score,
            tradelines=tradelines,
            risk_factors=risk_factors,
            positive_factors=positive_factors,
            recommendations=recommendations
        )
    
    def _identify_risk_factors(self, tradelines: List[Tradeline], 
                               utilization: float, delinquent_count: int) -> List[str]:
        """Identify negative factors impacting score."""
        factors = []
        
        if utilization > 75:
            factors.append(f"High credit utilization ({utilization:.1f}% - recommend below 30%)")
        
        if delinquent_count > 0:
            factors.append(f"{delinquent_count} delinquent account(s)")
        
        new_accounts = [tl for tl in tradelines if tl.account_age_days() < 90]
        if len(new_accounts) > 2:
            factors.append(f"{len(new_accounts)} recently opened accounts (may indicate credit stress)")
        
        if len(tradelines) < 3:
            factors.append("Limited credit history (fewer than 3 tradelines)")
        
        return factors
    
    def _identify_positive_factors(self, tradelines: List[Tradeline],
                                   utilization: float, on_time_pct: float) -> List[str]:
        """Identify positive factors boosting score."""
        factors = []
        
        if on_time_pct >= 95:
            factors.append(f"Excellent payment history ({on_time_pct:.1f}% on-time)")
        
        if utilization < 30:
            factors.append(f"Low credit utilization ({utilization:.1f}%)")
        
        old_accounts = [tl for tl in tradelines if tl.account_age_days() > 1825]
        if old_accounts:
            factors.append(f"{len(old_accounts)} well-established tradeline(s)")
        
        account_types = set(tl.account_type for tl in tradelines)
        if len(account_types) >= 3:
            factors.append("Diverse credit mix")
        
        return factors
    
    def _generate_recommendations(self, tradelines: List[Tradeline],
                                 utilization: float, score: int) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        if utilization > 50:
            recs.append("Pay down balances to reduce utilization below 30%")
        
        if score < 70:
            recs.append("Focus on consistent on-time payments to rebuild credit")
        
        if len(tradelines) < 5:
            recs.append("Consider adding vendor/supplier tradelines to build credit depth")
        
        delinquent = [tl for tl in tradelines if tl.is_delinquent()]
        if delinquent:
            recs.append("Bring delinquent accounts current immediately")
        
        if not any(tl.account_type == AccountType.REVOLVING for tl in tradelines):
            recs.append("Add a business credit card to improve credit mix")
        
        return recs
