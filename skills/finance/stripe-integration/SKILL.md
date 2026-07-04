---
name: finance/stripe-integration
description: Stripe payment processing integration for JARVIS business revenue tracking. Syncs Stripe payments to BusinessRevenueTracker, handles webhooks, refunds, and payouts.
category: finance
tags: [stripe, payments, revenue, webhooks, business]
version: 1.0.0
---

# Stripe Integration Skill

Integrates Stripe payment processing with JARVIS BusinessRevenueTracker for the Great Sage Tattoos & Tarot business.

## Features

- **Payment Sync**: Automatic sync of Stripe payments to revenue tracker
- **Webhook Handler**: Processes Stripe events (payment_intent.succeeded, charge.refunded, etc.)
- **Refund Handling**: Tracks refunds and adjusts revenue accordingly
- **Payout Reconciliation**: Matches Stripe payouts to bank deposits
- **Fee Tracking**: Records Stripe fees as expenses
- **Customer Sync**: Links Stripe customers to business clients

## Configuration

Required environment variables (stored in config, not in repo):
- `STRIPE_SECRET_KEY` - Secret API key
- `STRIPE_PUBLISHABLE_KEY` - Publishable key for frontend
- `STRIPE_WEBHOOK_SECRET` - Webhook signing secret
- `STRIPE_ACCOUNT_ID` - Connected account ID (if using Connect)

## Usage

```bash
# Sync recent payments
python -m scripts.stripe_sync --days 30

# Process webhook event (for serverless/webhook endpoint)
python -m scripts.stripe_webhook --event-json '{"type":"payment_intent.succeeded",...}'

# Reconcile payouts
python -m scripts.stripe_payout_reconcile --start 2026-07-01 --end 2026-07-31
```

## Integration Points

- **BusinessRevenueTracker**: Payments create RevenueEntry records
- **Client Database**: Stripe customers linked to CLI-XXX client IDs
- **Cron Automation**: Daily sync job via cron-automation skill
- **Financial Reporting**: Feeds monthly/quarterly reports