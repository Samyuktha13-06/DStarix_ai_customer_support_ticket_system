# NovaCart Payment Policy

Document Type: Policy
Category: Payments
Version: 1.0
Last Updated: 2026-08-01

## Supported Payment Methods

NovaCart supports:

- Credit cards
- Debit cards
- UPI
- Net banking
- Supported digital wallets

The payment methods displayed during checkout represent the currently
available options for the customer's transaction.

## Payment Status

A payment can have statuses such as:

- Pending
- Authorized
- Captured
- Failed
- Refunded
- Partially Refunded

Payment status should be checked using the payment transaction record
rather than inferred solely from the order status.

## Payment Deducted but Order Failed

If the customer's bank account or payment method was charged while the
corresponding order failed, the support system should verify both the
payment and order records.

If the payment is captured but the order failed, the issue may require
refund processing or manual reconciliation.

## Pending Payments

A pending payment has not necessarily been successfully captured.

Customers should avoid making repeated payments for the same order unless
the payment status has been confirmed.

## Failed Payments

A failed payment should not normally result in a successfully completed
order.

If an order appears successful while its payment is marked failed, the
case should be investigated.

## Refund Payments

Refunds are normally returned through the original payment method.

The exact time required for the refund to appear depends partly on the
payment provider or financial institution.

## Payment Disputes

Cases involving unauthorized transactions, repeated deductions, disputed
charges, or unclear payment ownership require human investigation.

The AI assistant should escalate such cases instead of making assumptions
about financial responsibility.