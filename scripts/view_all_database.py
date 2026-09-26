import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.database.models import Customer, Order, Payment, Ticket, Conversation, Message


def print_table(title: str, headers: list[str], rows: list[list]):
    print(f"\n{'=' * 95}")
    print(f" {title.upper()} ({len(rows)} records)")
    print(f"{'=' * 95}")
    if not rows:
        print("  (No records found)\n")
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val) if val is not None else "None"))

    # Cap column widths for readability
    col_widths = [min(w, 40) for w in col_widths]

    def fmt_row(items):
        formatted = []
        for i, it in enumerate(items):
            s = str(it) if it is not None else "-"
            w = col_widths[i]
            if len(s) > w:
                s = s[: w - 3] + "..."
            formatted.append(s.ljust(w))
        return " | ".join(formatted)

    header_str = fmt_row(headers)
    print(header_str)
    print("-+-".join("-" * w for w in col_widths))
    for row in rows:
        print(fmt_row(row))
    print()


def main():
    with SessionLocal() as db:
        # 1. Customers
        customers = db.query(Customer).order_by(Customer.id).all()
        print_table(
            "Customers",
            ["ID", "Name", "Email", "Created At"],
            [[c.id, c.name, c.email, c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "-"] for c in customers],
        )

        # 2. Orders
        orders = db.query(Order).order_by(Order.id).all()
        print_table(
            "Orders",
            ["Order ID", "Cust ID", "Product", "Amount", "Status", "Tracking", "Est. Delivery"],
            [
                [
                    o.id,
                    o.customer_id,
                    o.product,
                    f"Rs.{o.amount:,.2f}",
                    o.status,
                    o.tracking_number or "None",
                    str(o.expected_delivery_date) if o.expected_delivery_date else "-",
                ]
                for o in orders
            ],
        )

        # 3. Payments
        payments = db.query(Payment).order_by(Payment.id).all()
        print_table(
            "Payments",
            ["Payment ID", "Order ID", "Amount", "Status", "Payment Date"],
            [
                [
                    p.id,
                    p.order_id,
                    f"Rs.{p.amount:,.2f}",
                    p.status,
                    p.payment_date.strftime("%Y-%m-%d %H:%M") if p.payment_date else "-",
                ]
                for p in payments
            ],
        )

        # 4. Support Tickets
        tickets = db.query(Ticket).order_by(Ticket.id).all()
        print_table(
            "Support Tickets",
            ["Ticket ID", "Cust ID", "Order ID", "Priority", "Status", "Subject", "Description"],
            [
                [
                    t.id,
                    t.customer_id,
                    t.order_id or "-",
                    t.priority,
                    t.status,
                    t.subject,
                    t.description,
                ]
                for t in tickets
            ],
        )

        # 5. Conversations
        conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
        print_table(
            "Conversations",
            ["Conversation ID", "Title", "Cust ID", "Order ID", "Status", "Category"],
            [
                [
                    c.id,
                    c.title,
                    c.customer_id or "-",
                    c.order_id or "-",
                    c.status,
                    c.category or "-",
                ]
                for c in conversations
            ],
        )


if __name__ == "__main__":
    main()
