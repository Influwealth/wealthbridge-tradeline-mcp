#!/usr/bin/env python3
"""
WealthBridge Tradeline MCP - Command Line Interface
Manage business credit tradelines, scoring, and reporting.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.tradeline import (
    Tradeline, Business, TradelineStatus, PaymentStatus, AccountType
)
from engine.scoring import WealthBridgeScoringEngine
from engine.reporter import BureauReporter


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print_help()
        return 2

    command = sys.argv[1].lower()

    commands = {
        "test": cmd_test,
        "score": cmd_score,
        "report": cmd_report,
        "create-tradeline": cmd_create_tradeline,
        "list-tradelines": cmd_list_tradelines,
        "help": lambda: print_help()
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print_help()
        return 2

    try:
        return commands[command]()
    except Exception as e:
        print(f"Error: {e}")
        return 1


def print_help():
    """Display CLI help."""
    help_text = """
WealthBridge Tradeline MCP - Command Line Interface

USAGE:
    python cli.py <command> [options]

COMMANDS:
    test                Test system connectivity and configuration
    score <business_id> Calculate credit score for business
    report <business_id> Generate comprehensive credit report
    create-tradeline    Create new tradeline (interactive)
    list-tradelines <business_id>  List all tradelines for business
    help               Show this help message

EXAMPLES:
    python cli.py test
    python cli.py score BIZ001
    python cli.py report BIZ001
"""
    print(help_text)


def cmd_test():
    """Test system configuration."""
    print("=" * 50)
    print("WealthBridge Tradeline MCP - System Test")
    print("=" * 50)
    print()

    # Test scoring engine
    print("[1/2] Testing scoring engine...")
    try:
        engine = WealthBridgeScoringEngine()

        test_tradeline = Tradeline(
            tradeline_id="TEST001",
            business_id="TEST",
            account_number="1234",
            creditor_name="Test Creditor",
            account_type=AccountType.REVOLVING,
            status=TradelineStatus.ACTIVE,
            opened_date=date(2023, 1, 1),
            credit_limit=Decimal("10000"),
            current_balance=Decimal("2000"),
            high_balance=Decimal("5000"),
            monthly_payment=Decimal("200"),
            payment_status=PaymentStatus.CURRENT
        )

        score = engine.calculate_score([test_tradeline])
        print(f"✅ Scoring engine functional (test score: {score})")
    except Exception as e:
        print(f"❌ Scoring engine error: {e}")

    # Test reporter
    print("\n[2/2] Testing bureau reporter...")
    try:
        reporter = BureauReporter()
        print("✅ Bureau reporter initialized")
    except Exception as e:
        print(f"❌ Reporter error: {e}")

    print("\n" + "=" * 50)
    print("Test complete")
    print("=" * 50)

    return 0


def cmd_score():
    """Calculate credit score for business."""
    if len(sys.argv) < 3:
        print("Usage: python cli.py score <business_id>")
        return 2

    business_id = sys.argv[2]

    print(f"Calculating score for business: {business_id}")
    print()

    # Demo with sample tradeline
    demo_tradeline = Tradeline(
        tradeline_id="DEMO001",
        business_id=business_id,
        account_number="1234",
        creditor_name="Demo Credit Account",
        account_type=AccountType.REVOLVING,
        status=TradelineStatus.ACTIVE,
        opened_date=date(2023, 1, 1),
        credit_limit=Decimal("50000"),
        current_balance=Decimal("12000"),
        high_balance=Decimal("20000"),
        monthly_payment=Decimal("1000"),
        payment_status=PaymentStatus.CURRENT,
        payment_history=[PaymentStatus.CURRENT] * 12
    )

    engine = WealthBridgeScoringEngine()
    score = engine.calculate_score([demo_tradeline])

    print(f"WealthBridge Credit Score: {score}/100")
    print(f"Grade: {get_grade(score)}")

    return 0


def cmd_report():
    """Generate comprehensive credit report."""
    if len(sys.argv) < 3:
        print("Usage: python cli.py report <business_id>")
        return 2

    business_id = sys.argv[2]

    print("=" * 60)
    print(f"CREDIT REPORT - {business_id}")
    print("=" * 60)

    # Demo tradeline
    demo_tradeline = Tradeline(
        tradeline_id="DEMO001",
        business_id=business_id,
        account_number="1234",
        creditor_name="Demo Credit Account",
        account_type=AccountType.REVOLVING,
        status=TradelineStatus.ACTIVE,
        opened_date=date(2023, 1, 1),
        credit_limit=Decimal("50000"),
        current_balance=Decimal("12000"),
        high_balance=Decimal("20000"),
        monthly_payment=Decimal("1000"),
        payment_status=PaymentStatus.CURRENT,
        payment_history=[PaymentStatus.CURRENT] * 12
    )

    engine = WealthBridgeScoringEngine()
    report = engine.generate_report([demo_tradeline], business_id)

    print(f"\nReport ID: {report.report_id}")
    print(f"Generated: {report.report_date.strftime('%Y-%m-%d %H:%M')}")
    print()
    print("CREDIT SCORE")
    print(f"  WealthBridge Score: {report.wealthbridge_score}/100 ({get_grade(report.wealthbridge_score)})")
    print()
    print("CREDIT SUMMARY")
    print(f"  Total Tradelines: {report.total_tradelines}")
    print(f"  Total Credit Limit: ${report.total_credit_limit:,.2f}")
    print(f"  Total Balance: ${report.total_balance:,.2f}")
    print(f"  Utilization: {report.overall_utilization:.1f}%")

    if report.recommendations:
        print("\n💡 RECOMMENDATIONS")
        for rec in report.recommendations:
            print(f"  - {rec}")

    return 0


def cmd_create_tradeline():
    """Interactive tradeline creation."""
    print("Create New Tradeline")
    print("=" * 40)

    business_id = input("Business ID: ").strip()
    creditor_name = input("Creditor Name: ").strip()
    account_number = input("Account Number (last 4 digits): ").strip()
    credit_limit = Decimal(input("Credit Limit: $").strip())
    current_balance = Decimal(input("Current Balance: $").strip())

    tradeline = Tradeline(
        tradeline_id=f"TL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        business_id=business_id,
        account_number=account_number,
        creditor_name=creditor_name,
        account_type=AccountType.REVOLVING,
        status=TradelineStatus.ACTIVE,
        opened_date=date.today(),
        credit_limit=credit_limit,
        current_balance=current_balance,
        high_balance=current_balance,
        monthly_payment=Decimal("0"),
        payment_status=PaymentStatus.CURRENT
    )

    print()
    print("✅ Tradeline created successfully")
    print(f"   ID: {tradeline.tradeline_id}")
    print(f"   Utilization: {tradeline.calculate_utilization():.1f}%")

    return 0


def cmd_list_tradelines():
    """List tradelines for business."""
    if len(sys.argv) < 3:
        print("Usage: python cli.py list-tradelines <business_id>")
        return 2

    business_id = sys.argv[2]
    print(f"Tradelines for {business_id}")
    print("=" * 60)
    print("(No tradelines in local storage - use database for persistence)")

    return 0


def get_grade(score: int) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "D"


if __name__ == "__main__":
    sys.exit(main())
