"""
Core tradeline data models for WealthBridge MCP.
Represents credit tradelines, payment history, and reporting.
"""
from datetime import datetime, date
from typing import Optional, List, Literal
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum


class TradelineStatus(str, Enum):
    """Tradeline account status."""
    ACTIVE = "active"
    CLOSED = "closed"
    CHARGED_OFF = "charged_off"
    COLLECTIONS = "collections"
    PAID_OFF = "paid_off"
    PENDING = "pending"


class PaymentStatus(str, Enum):
    """Payment status codes (standard credit reporting)."""
    CURRENT = "current"  # 0 days late
    LATE_30 = "late_30"  # 30 days late
    LATE_60 = "late_60"  # 60 days late
    LATE_90 = "late_90"  # 90 days late
    LATE_120 = "late_120"  # 120+ days late
    CHARGED_OFF = "charged_off"
    COLLECTION = "collection"
    BANKRUPTCY = "bankruptcy"


class AccountType(str, Enum):
    """Type of credit account."""
    REVOLVING = "revolving"  # Credit cards, lines of credit
    INSTALLMENT = "installment"  # Term loans
    OPEN = "open"  # Charge cards (full balance due each month)
    MORTGAGE = "mortgage"
    COMMERCIAL = "commercial"  # Business credit


@dataclass
class Tradeline:
    """
    Represents a single credit tradeline (credit account).
    This is the core data structure reported to credit bureaus.
    """
    # Identification
    tradeline_id: str
    business_id: str  # Links to Business entity
    account_number: str  # Last 4 digits typically
    creditor_name: str
    
    # Account Details
    account_type: AccountType
    status: TradelineStatus
    opened_date: date
    closed_date: Optional[date] = None
    
    # Credit Limits & Balances
    credit_limit: Decimal = Decimal("0")
    current_balance: Decimal = Decimal("0")
    high_balance: Decimal = Decimal("0")  # Highest balance ever
    
    # Payment Information
    monthly_payment: Decimal = Decimal("0")
    payment_status: PaymentStatus = PaymentStatus.CURRENT
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[Decimal] = None
    
    # Payment History (24-month rolling)
    payment_history: List[PaymentStatus] = field(default_factory=list)
    
    # Reporting
    reported_to_experian: bool = False
    reported_to_equifax: bool = False
    reported_to_duns: bool = False
    last_reported_date: Optional[date] = None
    next_report_date: Optional[date] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    def calculate_utilization(self) -> float:
        """Calculate credit utilization percentage."""
        if self.credit_limit == 0:
            return 0.0
        return float((self.current_balance / self.credit_limit) * 100)
    
    def is_delinquent(self) -> bool:
        """Check if account is currently delinquent."""
        return self.payment_status in [
            PaymentStatus.LATE_30,
            PaymentStatus.LATE_60,
            PaymentStatus.LATE_90,
            PaymentStatus.LATE_120,
            PaymentStatus.CHARGED_OFF,
            PaymentStatus.COLLECTION
        ]
    
    def account_age_days(self) -> int:
        """Calculate account age in days."""
        end_date = self.closed_date or date.today()
        return (end_date - self.opened_date).days
    
    def is_reportable(self) -> bool:
        """Determine if tradeline meets reporting criteria."""
        # Must be at least minimum age (90 days default)
        if self.account_age_days() < 90:
            return False
        
        # Must have payment activity
        if not self.last_payment_date:
            return False
        
        # Must meet minimum payment threshold ($100 default)
        if self.last_payment_amount and self.last_payment_amount < Decimal("100"):
            return False
        
        return True


@dataclass
class Payment:
    """Individual payment record."""
    payment_id: str
    tradeline_id: str
    business_id: str
    
    payment_date: date
    payment_amount: Decimal
    principal_amount: Decimal = Decimal("0")
    interest_amount: Decimal = Decimal("0")
    fees_amount: Decimal = Decimal("0")
    
    payment_method: str = "ACH"  # ACH, wire, check, card
    payment_reference: str = ""  # Transaction ID
    
    # Status
    status: Literal["pending", "processed", "failed", "reversed"] = "pending"
    processed_at: Optional[datetime] = None
    
    # Reporting impact
    updates_payment_status: PaymentStatus = PaymentStatus.CURRENT
    reported_to_bureaus: bool = False
    report_date: Optional[date] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


@dataclass
class Business:
    """Business entity with credit profile."""
    business_id: str
    legal_name: str
    dba_name: Optional[str] = None
    
    # Identifiers
    ein: str = ""
    duns_number: Optional[str] = None
    cage_code: Optional[str] = None
    uei: Optional[str] = None  # SAM.gov Unique Entity ID
    
    # Contact
    address: dict = field(default_factory=dict)
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Business Details
    industry: Optional[str] = None
    naics_code: Optional[str] = None
    entity_type: Optional[str] = None  # LLC, Corp, etc.
    founded_date: Optional[date] = None
    
    # Credit Profile
    credit_score: Optional[int] = None  # WealthBridge proprietary score
    experian_score: Optional[int] = None
    equifax_score: Optional[int] = None
    duns_score: Optional[int] = None
    
    # Federal Integration
    sam_gov_active: bool = False
    federal_contractor: bool = False
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class CreditReport:
    """Complete credit report for a business."""
    report_id: str
    business_id: str
    report_date: datetime
    
    # Summary Statistics
    total_tradelines: int
    active_tradelines: int
    total_credit_limit: Decimal
    total_balance: Decimal
    total_available_credit: Decimal
    overall_utilization: float
    
    # Payment Performance
    on_time_payments_pct: float
    delinquent_accounts: int
    collections_count: int
    
    # Credit Age
    oldest_tradeline_age_months: int
    average_account_age_months: int
    
    # Scores
    wealthbridge_score: int
    experian_score: Optional[int] = None
    equifax_score: Optional[int] = None
    paydex_score: Optional[int] = None  # D&B
    
    # Tradelines
    tradelines: List[Tradeline] = field(default_factory=list)
    
    # Risk Factors
    risk_factors: List[str] = field(default_factory=list)
    positive_factors: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VendorCredit:
    """Vendor/supplier credit relationship (trade credit)."""
    vendor_credit_id: str
    business_id: str  # The business receiving credit
    vendor_id: str  # The supplier providing credit
    vendor_name: str
    
    # Terms
    credit_limit: Decimal
    payment_terms: str  # e.g., "Net 30", "Net 60"
    payment_terms_days: int
    
    # Status
    status: TradelineStatus
    established_date: date
    
    # Performance
    current_balance: Decimal = Decimal("0")
    total_purchases_ytd: Decimal = Decimal("0")
    average_days_to_pay: float = 0.0
    on_time_payment_rate: float = 0.0
    
    # Reporting
    reports_to_bureaus: bool = False
    last_reported_date: Optional[date] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
