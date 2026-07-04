#!/usr/bin/env python3
"""
Stripe Payment Sync — Syncs Stripe payments to BusinessRevenueTracker.
Registered via cron-automation skill for daily financial reconciliation.
"""

import os
import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, List

# Add tracker to path
sys.path.insert(0, str(Path(__file__).parent.parent / "business-revenue-tracking" / "scripts"))
from business_revenue_tracking import BusinessRevenueTracker, RevenueEntry

import stripe

# ─── Configuration ──────────────────────────────────────────────────────
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY:
    print("ERROR: STRIPE_SECRET_KEY not set", file=sys.stderr)
    sys.exit(1)

stripe.api_key = STRIPE_SECRET_KEY

BASE_PATH = Path("/opt/data/jarvis/business")
TRACKER = BusinessRevenueTracker(BASE_PATH)

# ─── Helper Functions ───────────────────────────────────────────────────

def _cents_to_dollars(amount_cents: int) -> float:
    """Convert Stripe cents to dollars."""
    return round(Decimal(amount_cents) / Decimal(100), 2)


def _find_client_by_email(email: str) -> Optional[str]:
    """Find client ID by email, create if not exists."""
    clients = TRACKER.list_clients()
    for c in clients:
        if c.email.lower() == email.lower():
            return c.id
    
    # Create new client from Stripe customer
    client_id = TRACKER.add_client(
        name=email.split("@")[0].replace(".", " ").title(),
        email=email,
        source="stripe",
        tags=["stripe-auto"],
        notes=f"Auto-created from Stripe customer on {date.today().isoformat()}"
    )
    return client_id


def _find_service_by_amount(amount: float, category_hint: str = "tattoo") -> Optional[str]:
    """Match payment amount to a service. Returns service_id or None."""
    services = TRACKER.list_services(active_only=True)
    
    # Try exact match first
    for s in services:
        if abs(s.base_price - amount) < 0.01:
            return s.id
    
    # Try category match with closest price
    category_services = [s for s in services if s.category == category_hint]
    if category_services:
        closest = min(category_services, key=lambda s: abs(s.base_price - amount))
        if abs(closest.base_price - amount) < 50:  # Within $50
            return closest.id
    
    return None


def _create_revenue_from_payment(payment: stripe.PaymentIntent, client_id: str, service_id: str) -> Optional[str]:
    """Create a RevenueEntry from a successful PaymentIntent."""
    try:
        amount = _cents_to_dollars(payment.amount)
        fee = _cents_to_dollars(payment.charges.data[0].balance_transaction.fee) if payment.charges.data else 0
        
        # Check if already recorded (by payment intent ID)
        existing_revenue = TRACKER.get_revenue()
        for r in existing_revenue:
            if r.id and payment.id in str(r.id):
                return None  # Already recorded
        
        # Create a booking first if needed
        booking_id = f"BKG-STRIPE-{payment.id[-8:]}"
        
        # Record as revenue entry directly
        revenue_id = f"REV-STRIPE-{payment.id[-8:]}"
        
        # Add expense for Stripe fee
        if fee > 0:
            TRACKER.add_expense(
                date=datetime.fromtimestamp(payment.created).date().isoformat(),
                category="payment_processing",
                amount=fee,
                description=f"Stripe fee for payment {payment.id}",
                vendor="Stripe",
                payment_method="stripe_fee"
            )
        
        # We need a booking to link to, so create a minimal one
        bookings_file = BASE_PATH / "data" / "bookings.json"
        import fcntl
        bookings = []
        if bookings_file.exists():
            with open(bookings_file, "r") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                bookings = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        booking = {
            "id": booking_id,
            "client_id": client_id,
            "service_id": service_id,
            "status": "completed",
            "scheduled_date": datetime.fromtimestamp(payment.created).date().isoformat(),
            "start_time": "00:00",
            "estimated_hours": 0,
            "actual_hours": 0,
            "artist": "Auto-Stripe",
            "deposit_paid": amount,
            "balance_due": 0,
            "total_revenue": amount,
            "tip": 0,
            "retail_revenue": 0,
            "payment_method": payment.payment_method_types[0] if payment.payment_method_types else "card",
            "notes": f"Stripe payment {payment.id}",
            "created": datetime.fromtimestamp(payment.created).isoformat(),
            "completed_date": datetime.fromtimestamp(payment.created).date().isoformat()
        }
        
        bookings.append(booking)
        with open(bookings_file, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(bookings, f, indent=2, default=str)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Create revenue entry
        revenue_file = BASE_PATH / "data" / "revenue.json"
        revenue_data = []
        if revenue_file.exists():
            with open(revenue_file, "r") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                revenue_data = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        revenue_entry = {
            "id": revenue_id,
            "booking_id": booking_id,
            "client_id": client_id,
            "service_id": service_id,
            "date": datetime.fromtimestamp(payment.created).date().isoformat(),
            "service_revenue": amount,
            "tip": 0,
            "retail_revenue": 0,
            "total": amount,
            "payment_method": payment.payment_method_types[0] if payment.payment_method_types else "card",
            "artist": "Auto-Stripe",
            "created": datetime.now().isoformat()
        }
        
        revenue_data.append(revenue_entry)
        with open(revenue_file, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(revenue_data, f, indent=2, default=str)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Update client LTV
        TRACKER.update_client_ltv(client_id, amount)
        
        return revenue_id
        
    except Exception as e:
        print(f"Error creating revenue from payment {payment.id}: {e}", file=sys.stderr)
        return None


# ─── Main Sync Function ─────────────────────────────────────────────────

def sync_payments(days: int = 30, limit: int = 100) -> Dict[str, Any]:
    """Sync recent successful payments from Stripe to revenue tracker."""
    print(f"Syncing Stripe payments from last {days} days...")
    
    start_time = int((datetime.now() - timedelta(days=days)).timestamp())
    
    # Fetch successful payment intents
    payments = stripe.PaymentIntent.list(
        created={"gte": start_time},
        limit=limit,
    )
    
    results = {
        "synced": 0,
        "skipped": 0,
        "errors": 0,
        "total_amount": 0.0,
        "details": []
    }
    
    for pi in payments.auto_paging_iter():
        if pi.status != "succeeded":
            results["skipped"] += 1
            continue
        
        # Get customer email
        customer_email = ""
        if pi.customer:
            try:
                cust = stripe.Customer.retrieve(pi.customer)
                customer_email = cust.email or ""
            except:
                pass
        
        if not customer_email and pi.receipt_email:
            customer_email = pi.receipt_email
        
        if not customer_email:
            results["skipped"] += 1
            results["details"].append({"payment_id": pi.id, "reason": "no_customer_email"})
            continue
        
        # Find or create client
        client_id = _find_client_by_email(customer_email)
        
        # Match to service
        amount = _cents_to_dollars(pi.amount)
        service_id = _find_service_by_amount(amount)
        
        if not service_id:
            # Default to first tattoo service
            services = TRACKER.list_services(active_only=True)
            tattoo_services = [s for s in services if s.category == "tattoo"]
            service_id = tattoo_services[0].id if tattoo_services else (services[0].id if services else None)
        
        if not service_id:
            results["errors"] += 1
            results["details"].append({"payment_id": pi.id, "reason": "no_service"})
            continue
        
        # Create revenue entry
        revenue_id = _create_revenue_from_payment(pi, client_id, service_id)
        
        if revenue_id:
            results["synced"] += 1
            results["total_amount"] += amount
            results["details"].append({
                "payment_id": pi.id,
                "revenue_id": revenue_id,
                "client_id": client_id,
                "service_id": service_id,
                "amount": amount
            })
        else:
            results["skipped"] += 1
            results["details"].append({"payment_id": pi.id, "reason": "already_recorded_or_failed"})
    
    results["total_amount"] = round(results["total_amount"], 2)
    return results


# ─── CLI Entry Point ────────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(prog="stripe-sync")
    parser.add_argument("--days", type=int, default=30, help="Days back to sync")
    parser.add_argument("--limit", type=int, default=100, help="Max payments to process")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    
    args = parser.parse_args()
    
    result = sync_payments(days=args.days, limit=args.limit)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Stripe Sync Complete")
        print(f"  Synced: {result['synced']} payments (${result['total_amount']:,.2f})")
        print(f"  Skipped: {result['skipped']}")
        print(f"  Errors: {result['errors']}")

if __name__ == "__main__":
    main()