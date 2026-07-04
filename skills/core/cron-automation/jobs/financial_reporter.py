#!/usr/bin/env python3
"""
J.A.R.V.I.S. Financial Reporter — Business Revenue Tracking Integration
Generates daily financial reports using BusinessRevenueTracker data.
"""

import json
from datetime import datetime, date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path("/opt/data/profiles/unrestricted/skills/finance/business-revenue-tracking/scripts")))

from business_revenue_tracking import BusinessRevenueTracker

JARVIS_ROOT = Path("/opt/data/jarvis")
LOGS_DIR = JARVIS_ROOT / "logs"
BUSINESS_PATH = Path("/opt/data/jarvis/business")


def main():
    print(f"=== J.A.R.V.I.S. FINANCIAL REPORT - {datetime.now().strftime('%B %d, %Y')} ===\n")

    tracker = BusinessRevenueTracker(BUSINESS_PATH)

    # Today's data
    today = date.today().isoformat()
    month_start = date.today().replace(day=1).isoformat()
    year_start = date.today().replace(month=1, day=1).isoformat()

    # Revenue summaries
    today_revenue = tracker.revenue_summary(today, today)
    month_revenue = tracker.revenue_summary(month_start, today)
    year_revenue = tracker.revenue_summary(year_start, today)

    # Expense summaries
    today_expenses = tracker.expense_summary(today, today)
    month_expenses = tracker.expense_summary(month_start, today)

    # Booking status counts
    bookings_today = tracker.list_bookings(start_date=today, end_date=today)
    bookings_month = tracker.list_bookings(start_date=month_start, end_date=today)

    # Service breakdown for the month
    service_breakdown = month_revenue.get("by_service", {})
    artist_breakdown = month_revenue.get("by_artist", {})

    # Calculate metrics
    total_revenue_month = month_revenue.get("total", 0)
    total_expenses_month = month_expenses.get("total", 0)
    net_income_month = total_revenue_month - total_expenses_month

    # Completed bookings this month
    completed_month = [b for b in bookings_month if b.status == "completed"]
    pending_month = [b for b in bookings_month if b.status in ["booked", "deposit_paid", "in_progress"]]

    # Average ticket
    avg_ticket = month_revenue.get("avg_ticket", 0)

    # Client metrics
    clients = tracker.list_clients()
    new_clients_month = len([c for c in clients if c.created >= month_start])

    report = {
        "date": today,
        "revenue": {
            "today": today_revenue.get("total", 0),
            "month": total_revenue_month,
            "year": year_revenue.get("total", 0),
            "by_service": service_breakdown,
            "by_artist": artist_breakdown,
            "avg_ticket": avg_ticket,
        },
        "expenses": {
            "today": today_expenses.get("total", 0),
            "month": total_expenses_month,
            "by_category": month_expenses.get("by_category", {}),
        },
        "bookings": {
            "today": len(bookings_today),
            "completed_month": len(completed_month),
            "pending_month": len(pending_month),
            "new_clients_month": new_clients_month,
        },
        "net_income_month": round(net_income_month, 2),
        "forecast": {
            "next_week_estimate": round(total_revenue_month / max(date.today().day, 1) * 7, 2),
            "next_month_estimate": round(total_revenue_month * (date.today().replace(month=date.today().month+1 if date.today().month<12 else 1, day=1) - date.today().replace(day=1)).days / date.today().day, 2) if date.today().day > 0 else 0,
            "confidence": "MEDIUM" if total_revenue_month > 0 else "LOW",
        },
    }

    print("TODAY'S REVENUE:")
    print(f"  Total:           ${report['revenue']['today']:,.2f}")

    print("\nMONTH TO DATE:")
    print(f"  Revenue:         ${report['revenue']['month']:,.2f}")
    print(f"  Expenses:        ${report['expenses']['month']:,.2f}")
    print(f"  Net Income:      ${report['net_income_month']:,.2f}")
    print(f"  Completed Jobs:  {report['bookings']['completed_month']}")
    print(f"  Pending Jobs:    {report['bookings']['pending_month']}")
    print(f"  New Clients:     {report['bookings']['new_clients_month']}")
    print(f"  Avg Ticket:      ${report['revenue']['avg_ticket']:,.2f}")

    if service_breakdown:
        print("\nSERVICE BREAKDOWN (MTD):")
        for svc, amt in sorted(service_breakdown.items(), key=lambda x: -x[1]):
            pct = (amt / total_revenue_month * 100) if total_revenue_month > 0 else 0
            print(f"  {svc}: ${amt:,.2f} ({pct:.1f}%)")

    if artist_breakdown:
        print("\nARTIST BREAKDOWN (MTD):")
        for artist, amt in sorted(artist_breakdown.items(), key=lambda x: -x[1]):
            print(f"  {artist}: ${amt:,.2f}")

    print("\nFORECAST:")
    print(f"  Next Week:  ${report['forecast']['next_week_estimate']:,.2f} ({report['forecast']['confidence']})")
    print(f"  Next Month: ${report['forecast']['next_month_estimate']:,.2f} ({report['forecast']['confidence']})")

    # Save
    LOGS_DIR.mkdir(exist_ok=True)
    financial_file = LOGS_DIR / f"financial_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(financial_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "financial": report
        }, f, indent=2)

    print(f"\n✓ Financial report saved to {financial_file}")


if __name__ == "__main__":
    main()