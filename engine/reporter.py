"""
Credit Bureau Reporting Engine.
Formats and submits tradeline data to Experian, Equifax, and D&B.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.tradeline import Tradeline, PaymentStatus, Business
import requests


class BureauReporter:
    """Handles reporting of tradeline data to credit bureaus."""
    
    def __init__(self):
        self.experian_client = None
        self.equifax_client = None
        self.duns_client = None
    
    def report_tradeline(self, tradeline: Tradeline, business: Business) -> Dict[str, bool]:
        """Report tradeline to all configured bureaus."""
        results = {}
        
        if not tradeline.is_reportable():
            return {
                "experian": False,
                "equifax": False,
                "duns": False,
                "reason": "Tradeline does not meet reporting criteria"
            }
        
        # Report to each bureau (stub implementations)
        results["experian"] = self._report_to_experian(tradeline, business)
        results["equifax"] = self._report_to_equifax(tradeline, business)
        results["duns"] = self._report_to_duns(tradeline, business)
        
        if any(results.get(k, False) for k in ["experian", "equifax", "duns"]):
            tradeline.last_reported_date = date.today()
        
        return results
    
    def _report_to_experian(self, tradeline: Tradeline, business: Business) -> bool:
        """Submit tradeline to Experian Business Credit."""
        # Stub - would use actual Experian API
        print(f"[STUB] Reporting to Experian: {tradeline.tradeline_id}")
        return True
    
    def _report_to_equifax(self, tradeline: Tradeline, business: Business) -> bool:
        """Submit tradeline to Equifax."""
        # Stub - would use actual Equifax API
        print(f"[STUB] Reporting to Equifax: {tradeline.tradeline_id}")
        return True
    
    def _report_to_duns(self, tradeline: Tradeline, business: Business) -> bool:
        """Submit payment experience to D&B for PAYDEX score."""
        if not business.duns_number:
            return False
        # Stub - would use actual D&B API
        print(f"[STUB] Reporting to D&B: {tradeline.tradeline_id}")
        return True
    
    def format_metro2(self, tradeline: Tradeline, business: Business) -> str:
        """Format tradeline data in Metro 2 format (credit industry standard)."""
        segments = []
        
        # Header record
        header = "H1" + datetime.now().strftime("%Y%m%d") + "WEALTHBRIDGE"
        segments.append(header.ljust(426))
        
        # Base segment
        base = self._format_base_segment(tradeline, business)
        segments.append(base)
        
        # Trailer record
        trailer = "T1" + str(len(segments) - 1).zfill(9)
        segments.append(trailer.ljust(426))
        
        return "\n".join(segments)
    
    def _format_base_segment(self, tradeline: Tradeline, business: Business) -> str:
        """Format Metro 2 base segment (required)."""
        segment = "B1"
        segment += business.ein.replace("-", "").ljust(9)
        segment += tradeline.account_number.ljust(30)
        
        type_code = {
            "revolving": "R",
            "installment": "I",
            "open": "O",
            "mortgage": "M",
            "commercial": "C"
        }.get(tradeline.account_type.value, "O")
        segment += type_code
        
        segment += tradeline.opened_date.strftime("%m%d%Y")
        segment += str(int(tradeline.credit_limit)).zfill(9)
        segment += str(int(tradeline.current_balance)).zfill(9)
        
        status_code = {
            "current": "0",
            "late_30": "1",
            "late_60": "2",
            "late_90": "3",
            "late_120": "4",
            "charged_off": "9",
            "collection": "9"
        }.get(tradeline.payment_status.value, "0")
        segment += status_code
        
        return segment.ljust(426)
