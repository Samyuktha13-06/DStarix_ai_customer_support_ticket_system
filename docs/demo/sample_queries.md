# NovaCart AI Customer Support & Ticket Automation System
## Interactive Demo & Sample Queries Guide

This guide provides curated, tested, and categorized sample queries designed for demonstrating the full capabilities of the **NovaCart AI Customer Support System** via the interactive Web UI (`http://localhost:5173`) or the REST API (`http://localhost:8000/chat`).

---

## 1. Quick Reference: Seeded Demo Data

Use these pre-seeded customer accounts and orders to demonstrate real-time database queries and live context updates in the UI:

| Order ID | Customer Name | Product | Order Status | Payment Status | Tracking Number | Notes / Key Feature |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **`45821`** | Aarav Sharma | NovaPhone X1 (₹69,999) | **Shipped** | **Captured** | `NVC45821001` | Normal active order with tracking |
| **`45822`** | Aarav Sharma | NovaBuds Pro (₹8,999) | **Processing** | **Captured** | *None* | Pending dispatch / Pre-shipment |
| **`45823`** | Priya Nair | NovaBook Air 14 (₹74,999) | **Delivered** | **Captured** | `NVC45823001` | Delivered order / Return eligible |
| **`45824`** | Priya Nair | NovaWatch S2 (₹12,999) | **Failed** | **Captured** | *None* | 🚨 **Auto-Escalation Demo** (Payment vs Order Mismatch) |
| **`45825`** | Rahul Mehta | NovaTab 11 (₹29,999) | **Processing** | **Failed** | *None* | Payment failed issue |
| **`45826`** | Ananya Reddy | NovaCharge 65W (₹2,499) | **Cancelled** | **Refunded** | *None* | Cancelled order with refund record |
| **`99999`** | — | — | *Not Found* | — | — | **Invalid ID / Error Handling Demo** |

---

## 2. Categorized Sample Queries

### Category 1: Knowledge-Base & Store Policy FAQs (RAG Semantic Retrieval)

These queries demonstrate ChromaDB vector similarity search over NovaCart's documentation with zero hallucination.

#### 1.1 Shipping & Delivery Times
* **Query**:
  ```text
  How long does standard delivery take, and what shipping options do you offer?
  ```
* **Tool Used**: `query_knowledge_base`
* **Expected Behavior**: Explains standard shipping (3–5 business days) and express delivery options grounded in `shipping_policy.md`.
* **UI Highlight**: Displays the `query_knowledge_base` tool pill in the message bubble.

#### 1.2 Return & Refund Policy
* **Query**:
  ```text
  What is your refund policy and how many days do I have to return an item?
  ```
* **Tool Used**: `query_knowledge_base`
* **Expected Behavior**: Explains the 7-calendar-day return window, condition requirements (unused, original box), and 5–7 business day refund timeline from `refund_policy.md`.

#### 1.3 Order Cancellation Terms
* **Query**:
  ```text
  Can I cancel my order after it has shipped?
  ```
* **Tool Used**: `query_knowledge_base`
* **Expected Behavior**: Cites `cancellation_policy.md`, explaining that orders can only be canceled while in `Processing` or `Pending` state before dispatch.

#### 1.4 Payment Security & Methods
* **Query**:
  ```text
  What payment methods do you accept and is my payment secure?
  ```
* **Tool Used**: `query_knowledge_base`
* **Expected Behavior**: Confirms support for UPI, Credit/Debit cards, Net Banking, and explains 256-bit encryption and PCI-DSS compliance from `payment_policy.md`.

---

### Category 2: Order Lookup & Tracking (Live Database Tools)

These queries trigger real-time SQLite lookups and automatically populate the **Order Context Card** in the UI right panel.

#### 2.1 Track Active Shipped Order
* **Query**:
  ```text
  Where is my order 45821?
  ```
* **Tool Used**: `check_order_status`
* **Expected Behavior**: Returns status `Shipped`, tracking number `NVC45821001`, and delivery date.
* **UI Highlight**: Right panel instantly displays Order #45821 card with tracking link, product image placeholder, and status badge.

#### 2.2 Check Processing Order
* **Query**:
  ```text
  What is the status of order 45822?
  ```
* **Tool Used**: `check_order_status`
* **Expected Behavior**: Confirms order #45822 for `NovaBuds Pro` is currently `Processing` in the fulfillment center.

#### 2.3 Check Delivered Order
* **Query**:
  ```text
  Can you check if order 45823 was delivered?
  ```
* **Tool Used**: `check_order_status`
* **Expected Behavior**: Confirms delivery completed on September 3, 2026, with tracking number `NVC45823001`.

#### 2.4 Invalid / Non-Existent Order
* **Query**:
  ```text
  What is the status of order 99999?
  ```
* **Tool Used**: `check_order_status`
* **Expected Behavior**: Gracefully informs the customer that Order #99999 was not found and prompts to verify the order number. No system crash.

---

### Category 3: Financial & Payment Inquiries

These queries demonstrate real-time retrieval of payment transaction records and status checks.

#### 3.1 Verify Captured Payment
* **Query**:
  ```text
  Did my payment go through for order 45821?
  ```
* **Tool Used**: `check_payment_status`
* **Expected Behavior**: Confirms payment of ₹69,999.00 was successfully `Captured`.
* **UI Highlight**: Right panel displays the **Payment Status Card** with amount and transaction timestamp.

#### 3.2 Inquire About Refunded Order
* **Query**:
  ```text
  What is the payment status for cancelled order 45826?
  ```
* **Tool Used**: `check_payment_status`
* **Expected Behavior**: Explains that payment of ₹2,499.00 was marked as `Refunded`.

---

### Category 4: Support Ticket Creation & Issue Logging

These queries demonstrate the agent's ability to extract issue details and insert a persistent support ticket into SQLite.

#### 4.1 Log Damaged Package Issue
* **Query**:
  ```text
  Please create a support ticket for my order 45822. The package arrived with severe physical damage.
  ```
* **Tool Used**: `create_support_ticket`
* **Expected Behavior**: Creates a ticket with `High` priority, records the damage description, and returns the assigned ticket ID.
* **UI Highlight**: Displays the ticket ID in the message and logs it in the system database.

#### 4.2 Defective Product Complaint
* **Query**:
  ```text
  My NovaBook from order 45823 has a flickering screen. Please register a complaint ticket.
  ```
* **Tool Used**: `create_support_ticket`
* **Expected Behavior**: Creates a ticket categorized under hardware defect with appropriate follow-up instructions.

---

### Category 5: Automated Anomaly Detection & Human Escalation

These queries showcase the ReAct agent's reasoning capability to detect critical business anomalies and perform automatic escalation.

#### 5.1 Critical Payment Inconsistency (The Star Demo Scenario)
* **Query**:
  ```text
  My payment was deducted but my order 45824 failed. Please help!
  ```
* **Tools Used**: `check_order_status`, `check_payment_status`, `create_support_ticket`
* **What Happens**:
  1. Agent checks order status -> returns `Failed`.
  2. Agent checks payment status -> returns `Captured`.
  3. Agent recognizes the critical mismatch (money charged for a failed order).
  4. Automatically triggers high-priority ticket creation and sets `escalated: true`.
* **UI Highlight**:
  - Displays a red **Human Escalation Alert Card** with the ticket ID.
  - Right panel updates ticket status to `Open - High Priority`.
  - Reassures the customer that a human manager is taking over.

#### 5.2 Explicit Request for Human Support
* **Query**:
  ```text
  I want to speak with a human support representative immediately about my order 45824.
  ```
* **Tools Used**: `create_support_ticket`
* **Expected Behavior**: Honors the customer's request without friction, logs a ticket, and sets `escalated: true`.

---

### Category 6: Multi-Turn Conversation & Memory Persistence

These queries demonstrate conversational state retention across turns within the same thread.

#### 6.1 Two-Turn Pronoun Resolution ("it")
* **Turn 1**:
  ```text
  Where is my order 45821?
  ```
  *(Agent answers: Order #45821 is Shipped and expected on September 16, 2026)*
* **Turn 2**:
  ```text
  When will it arrive?
  ```
* **Expected Behavior**:
  - The agent understands that *"it"* refers to Order #45821 from the previous turn.
  - Answers with the expected delivery date without asking the user to re-type the order number.

#### 6.2 Three-Turn Progressive Interaction
* **Turn 1**:
  ```text
  What is the status of order 45821?
  ```
* **Turn 2**:
  ```text
  What courier is delivering it?
  ```
* **Turn 3**:
  ```text
  Did my payment go through for this order?
  ```
* **Expected Behavior**: Seamlessly chains order status, tracking code inspection, and payment verification while maintaining a single thread context.

---

### Category 7: Out-of-Domain Guardrails (Anti-Hallucination)

These queries verify that the agent stays strictly within its role as NovaCart's customer support representative.

#### 7.1 Off-Topic General Knowledge
* **Query**:
  ```text
  What is the current stock price of Tesla and who won the 2024 World Cup?
  ```
* **Expected Behavior**:
  - Politely states that it only has access to NovaCart store policies, products, orders, and services.
  - Zero hallucinations or ungrounded claims.

#### 7.2 Non-Existent Product Features
* **Query**:
  ```text
  Does the NovaPhone X1 support holographic teleportation?
  ```
* **Expected Behavior**:
  - Clarifies product specifications based solely on `products.md` and politely notes that feature does not exist.

---

## 3. Demo Flow Checklist (Recommended Presentation Sequence)

For a complete 5-minute showcase of the project, run these queries in sequence:

1. **Step 1 (FAQ & RAG)**: *"What is your refund policy?"*
   - Shows semantic search, fast grounded answers, and clean markdown rendering.
2. **Step 2 (Tool Calling & UI Integration)**: *"Where is my order 45821?"*
   - Shows live database tool execution, tool badge pill, and right panel Order Card sync.
3. **Step 3 (Conversation Memory)**: *"When will it arrive?"*
   - Shows LangGraph checkpointer memory and coreference resolution.
4. **Step 4 (Automated Escalation)**: *"My payment was deducted but my order 45824 failed."*
   - Shows multi-tool reasoning, discrepancy detection, ticket generation, and Escalation Alert Card.
5. **Step 5 (Guardrails)**: *"Can you write a poem about Elon Musk?"*
   - Shows robust system boundaries and polite domain restriction.
