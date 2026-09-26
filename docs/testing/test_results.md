# NovaCart AI Customer Support & Ticket Automation System
## Comprehensive Test Execution Results & Scenario Reports

This document provides a detailed record of the 13 functional, integration, fault tolerance, and conversational test scenarios executed against the **NovaCart AI Customer Support & Ticket Automation System**.

---

## 1. Test Summary & Scenario Matrix

| Metric | Value |
| :--- | :--- |
| **Total Test Scenarios** | **13** |
| **Passed** | **13 (100%)** |
| **Failed** | **0 (0%)** |
| **Testing Scope** | Knowledge Base RAG, Tool Execution, Database Sync, Error Resilience, Conversation Memory, Escalations |
| **Test Frameworks** | Pytest, FastAPI TestClient, LangGraph Test Harness |
| **Execution Environment** | Python 3.14 / SQLite / ChromaDB / Groq LLM (`llama-3.3-70b-versatile`) |

### Scenario Index

| Test ID | Scenario Name | Real-World Customer Scenario | Primary Tool / Component | Status |
| :--- | :--- | :--- | :--- | :---: |
| **[TC-01](#tc-01-general-faq)** | General FAQ | Customer asks about standard shipping duration | `query_knowledge_base` | `PASS` |
| **[TC-02](#tc-02-knowledge-base-question)** | Knowledge-base question | Customer asks about order cancellation rules | `query_knowledge_base` | `PASS` |
| **[TC-03](#tc-03-refund-question)** | Refund question | Customer asks how many days they have to return an item | `query_knowledge_base` | `PASS` |
| **[TC-04](#tc-04-order-status)** | Order status | Customer checks tracking and status for Order #45821 | `check_order_status` | `PASS` |
| **[TC-05](#tc-05-payment-status)** | Payment status | Customer verifies payment transaction for Order #45824 | `check_payment_status` | `PASS` |
| **[TC-06](#tc-06-ticket-creation)** | Ticket creation | Customer requests a ticket for a damaged item in Order #45822 | `create_support_ticket` | `PASS` |
| **[TC-07](#tc-07-human-escalation)** | Human escalation | Customer reports payment deducted while order failed | Auto-Escalation Engine | `PASS` |
| **[TC-08](#tc-08-unknown-question)** | Unknown question | Customer asks an off-topic / out-of-domain question | Guardrails & Fallback | `PASS` |
| **[TC-09](#tc-09-invalid-order-id)** | Invalid order ID | Customer inquires about non-existent Order #99999 | Graceful Error Handling | `PASS` |
| **[TC-10](#tc-10-tool-failure)** | Tool failure | Backend database or tool encounters operational exception | Fault Isolation Boundary | `PASS` |
| **[TC-11](#tc-11-retrieval-failure)** | Retrieval failure | ChromaDB vector search fails or index is unavailable | Safe Fallback Generator | `PASS` |
| **[TC-12](#tc-12-conversation-follow-up)** | Conversation follow-up | Multi-turn chat where customer refers to order with pronoun "it" | LangGraph Checkpointer | `PASS` |
| **[TC-13](#tc-13-multiple-requests)** | Multiple requests | Two concurrent users inquire about different orders | Session Isolation Engine | `PASS` |

---

## 2. Detailed Test Scenarios & Execution Logs

### TC-01: General FAQ

* **Scenario Description**: A customer asks a standard logistical question regarding shipping times and delivery policies to verify that RAG semantic retrieval answers directly from documentation without generating an unnecessary escalation.
* **Traceability**: [tests/test_api_chat.py::test_basic_chat](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/tests/test_api_chat.py#L78-L110)
* **Customer Query**:
  > *"How long does standard delivery take?"*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "test-basic-chat",
    "message": "How long does standard delivery take?"
  }
  ```
* **Tools Invoked**:
  - `query_knowledge_base(query="standard delivery time shipping")`
* **Agent Response**:
  > *"Standard delivery typically takes 3 to 5 business days from the date of dispatch. You will receive a tracking link via email once your package has shipped."*
* **API Response Payload**:
  ```json
  {
    "answer": "Standard delivery typically takes 3 to 5 business days from the date of dispatch. You will receive a tracking link via email once your package has shipped.",
    "escalated": false,
    "ticket_id": null,
    "order": null,
    "payment": null,
    "tools_used": [
      { "name": "query_knowledge_base", "args": { "query": "standard delivery time shipping" } }
    ],
    "customer": null
  }
  ```
* **Result**: `PASS` (HTTP 200, strictly grounded answer, no escalation).

---

### TC-02: Knowledge-Base Question

* **Scenario Description**: A customer asks about order cancellation policies. The agent must semantically match the query against `cancellation_policy.md` stored in ChromaDB and synthesize a concise, grounded response.
* **Traceability**: [tests/test_api_chat.py::test_chat_response_structure](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/tests/test_api_chat.py#L338-L373)
* **Customer Query**:
  > *"What is your cancellation policy?"*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "test-response-structure",
    "message": "What is your cancellation policy?"
  }
  ```
* **Tools Invoked**:
  - `query_knowledge_base(query="order cancellation policy")`
* **Agent Response**:
  > *"You can cancel your order at any time before it has been dispatched or shipped. Once an order enters the 'Shipped' state, it cannot be canceled directly; instead, you may initiate a return under our 7-day refund policy upon delivery."*
* **API Response Payload**:
  ```json
  {
    "answer": "You can cancel your order at any time before it has been dispatched or shipped. Once an order enters the 'Shipped' state, it cannot be canceled directly; instead, you may initiate a return under our 7-day refund policy upon delivery.",
    "escalated": false,
    "ticket_id": null,
    "order": null,
    "payment": null,
    "tools_used": [
      { "name": "query_knowledge_base", "args": { "query": "order cancellation policy" } }
    ],
    "customer": null
  }
  ```
* **Result**: `PASS` (HTTP 200, policy retrieved correctly, response structure contains all 7 required keys).

---

### TC-03: Refund Question

* **Scenario Description**: A customer asks about return windows and refund processing conditions to verify accurate grounding in `knowledge_base/refund_policy.md`.
* **Traceability**: [scripts/test_api_integration.py::test_knowledge_base_query](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/scripts/test_api_integration.py#L38-L70)
* **Customer Query**:
  > *"What is your refund policy and how many days do I have to return an item?"*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "phase9-8-kb-001",
    "message": "What is your refund policy and how many days do I have to return an item?"
  }
  ```
* **Tools Invoked**:
  - `query_knowledge_base(query="refund policy return days eligibility")`
* **Agent Response**:
  > *"Under the NovaCart Refund Policy, you have 7 calendar days from the delivery date to request a return. Items must be unused, in their original packaging, and accompanied by proof of purchase. Refunds are processed back to the original payment method within 5 to 7 business days after inspection."*
* **Result**: `PASS` (HTTP 200, exactly matches 7 calendar days rule and 5-7 business days refund timeframe).

---

### TC-04: Order Status

* **Scenario Description**: Customer provides a valid seeded order number (`45821`) and asks for its status. The agent calls the database order lookup tool, extracts tracking information, and enriches the response with order metadata.
* **Traceability**: [scripts/test_api_integration.py::test_order_query](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/scripts/test_api_integration.py#L71-L97)
* **Customer Query**:
  > *"What is the status of order 45821?"*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "phase9-8-order-001",
    "message": "What is the status of order 45821?"
  }
  ```
* **Tools Invoked**:
  - `check_order_status(order_id=45821)`
* **Database Record Found**:
  - ID: `45821` | Product: `Wireless Noise-Canceling Headphones` | Status: `Shipped` | Tracking: `NVC45821001` | Est. Delivery: `2026-09-28`
* **Agent Response**:
  > *"Your order #45821 for Wireless Noise-Canceling Headphones has been shipped. The tracking number is NVC45821001, and the expected delivery date is September 28, 2026."*
* **API Response Payload Highlights**:
  ```json
  {
    "escalated": false,
    "ticket_id": null,
    "order": {
      "order_id": 45821,
      "product": "Wireless Noise-Canceling Headphones",
      "amount": 129.99,
      "status": "Shipped",
      "tracking_number": "NVC45821001",
      "expected_delivery_date": "2026-09-28"
    }
  }
  ```
* **Result**: `PASS` (HTTP 200, accurate live database status retrieved and formatted).

---

### TC-05: Payment Status

* **Scenario Description**: Customer asks to verify payment status for Order #45824. The agent queries financial records via `check_payment_status` and confirms payment capture.
* **Traceability**: [tests/test_tools_integration.py::test_payment_tool_returns_payment](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/tests/test_tools_integration.py#L38-L49)
* **Customer Query**:
  > *"What is the payment status for order 45824?"*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "test-payment-status-45824",
    "message": "What is the payment status for order 45824?"
  }
  ```
* **Tools Invoked**:
  - `check_payment_status(order_id=45824)`
* **Database Record Found**:
  - ID: `102` | Order ID: `45824` | Amount: `$79.99` | Status: `Captured` | Method: `Credit Card`
* **Agent Response**:
  > *"Payment for order 45824 of $79.99 was successfully Captured on September 22, 2026."*
* **Result**: `PASS` (HTTP 200, payment captured record retrieved accurately).

---

### TC-06: Ticket Creation

* **Scenario Description**: Customer reports that their package arrived with physical damage and requests a formal support ticket. The agent invokes `create_support_ticket` to insert a persistent record in SQLite.
* **Traceability**: [scripts/test_tools.py](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/scripts/test_tools.py)
* **Customer Query**:
  > *"Please create a support ticket for my order 45822. The package arrived with severe physical damage."*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "test-ticket-creation-001",
    "message": "Please create a support ticket for my order 45822. The package arrived with severe physical damage."
  }
  ```
* **Tools Invoked**:
  - `create_support_ticket(order_id=45822, issue_description="Package arrived with severe physical damage", priority="High")`
* **Database Action**:
  - Record created in `tickets` table with ID `301`, status `Open`, priority `High`.
* **Agent Response**:
  > *"I have created a support ticket for order #45822 regarding the damaged package. Your ticket ID is #301 with High priority. Our support operations team will inspect the case and follow up with replacement options."*
* **Result**: `PASS` (HTTP 200, ticket ID generated, persisted in SQLite database).

---

### TC-07: Human Escalation

* **Scenario Description**: The customer reports that money was deducted from their account, but Order #45824 shows failed in the system. The agent detects a critical state inconsistency (Payment `Captured` vs Order `Failed`), escalates immediately, sets `escalated: true`, and returns a ticket ID.
* **Traceability**: [tests/test_api_chat.py::test_payment_order_issue_escalates](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/tests/test_api_chat.py#L305-L336)
* **Customer Query**:
  > *"My payment was deducted but my order 45824 failed."*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "test-api-payment-escalation-45824",
    "message": "My payment was deducted but my order 45824 failed."
  }
  ```
* **Tools Invoked**:
  - `check_order_status(order_id=45824)` -> returns `Status: Failed`
  - `check_payment_status(order_id=45824)` -> returns `Status: Captured`
  - `create_support_ticket(order_id=45824, issue_description="Payment captured but order marked failed", priority="High")` -> returns `ticket_id: 302`
* **Agent Response**:
  > *"I see that payment was successfully captured for order #45824, but the order status shows as Failed. Because of this inconsistency, I have escalated this issue to a human support specialist. Your support ticket ID is #302. An agent will contact you shortly to ensure your order is fulfilled or refunded."*
* **API Response Payload Highlights**:
  ```json
  {
    "escalated": true,
    "ticket_id": 302
  }
  ```
* **Result**: `PASS` (HTTP 200, auto-detected discrepancy, `escalated` is `true`, valid integer `ticket_id`).

---

### TC-08: Unknown Question

* **Scenario Description**: Customer asks a question completely outside the scope of NovaCart's store documentation (e.g., current weather or stock market prices). The system must adhere to strict grounding guidelines and decline without hallucination.
* **Traceability**: [scripts/test_escalation_scenarios.py](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/scripts/test_escalation_scenarios.py)
* **Customer Query**:
  > *"What is the current stock price of Tesla and do you deliver by drone to the moon?"*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "test-unknown-guardrails",
    "message": "What is the current stock price of Tesla and do you deliver by drone to the moon?"
  }
  ```
* **Tools Invoked**:
  - `query_knowledge_base(query="Tesla stock price drone delivery moon")` -> No relevant documents found.
* **Agent Response**:
  > *"I don't have information about that. I am NovaCart's automated support assistant, and I can only help you with orders, deliveries, payments, returns, and store policies. Please let me know if you need assistance with a NovaCart order!"*
* **Result**: `PASS` (HTTP 200, strictly bounded response, zero hallucination, `escalated: false`).

---

### TC-09: Invalid Order ID

* **Scenario Description**: Customer inquiries about an order number (`99999`) that does not exist in the database. The agent must catch the not-found status and inform the customer politely without crashing.
* **Traceability**: [scripts/test_escalation_scenarios.py::main](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/scripts/test_escalation_scenarios.py#L280-L293)
* **Customer Query**:
  > *"Where is my order 99999?"*
* **API Request**:
  ```json
  POST /chat
  {
    "thread_id": "phase85-invalid-order",
    "message": "Where is my order 99999?"
  }
  ```
* **Tools Invoked**:
  - `check_order_status(order_id=99999)` -> returns `{"success": false, "error": "Order 99999 not found"}`
* **Agent Response**:
  > *"I looked up order #99999, but it could not be found in our system. Please double-check your order number or check your confirmation email. If you believe this is an error, I can connect you with a representative."*
* **Result**: `PASS` (HTTP 200, graceful negative acknowledgment, zero unhandled errors).

---

### TC-10: Tool Failure

* **Scenario Description**: Simulates a backend operational failure or database connection drop while executing an agent tool. The LangGraph error boundary catches the exception and returns a graceful message to the user.
* **Traceability**: [scripts/test_tool_failure_handling.py](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/scripts/test_tool_failure_handling.py)
* **Execution Flow**:
  1. Test graph executes `controlled_failure_tool` with payload `{"order_id": 45821}`.
  2. Tool intercepts simulated operational exception and catches it cleanly:
     `{"success": false, "error": "Database query timed out during order lookup"}`.
  3. Agent returns a safe, customer-facing notification without crashing the process.
* **Agent Response**:
  > *"I am currently unable to retrieve your order details due to a temporary system connectivity issue. Please try again in a few moments or contact support if the issue persists."*
* **Result**: `PASS` (Tool returned `success: False`, graph remained stable, server did not crash).

---

### TC-11: Retrieval Failure

* **Scenario Description**: Simulates a ChromaDB retrieval failure (corrupted vector query or unavailable store). The RAG subsystem catches the error, logs it, and provides a safe fallback.
* **Traceability**: [scripts/test_rag_failure_handling.py](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/scripts/test_rag_failure_handling.py)
* **Execution Flow**:
  1. Simulated failure triggers an exception in `retriever.get_relevant_documents()`.
  2. RAG tool catches exception and logs failure event to logger.
  3. Fallback mechanism directs the customer to general support.
* **Agent Response**:
  > *"I am having trouble accessing the knowledge base right now. For urgent questions regarding our policies or returns, please contact our support team directly."*
* **Result**: `PASS` (Exception handled cleanly, zero unhandled 500 errors).

---

### TC-12: Conversation Follow-Up

* **Scenario Description**: Tests multi-turn conversation memory within a single thread. The customer asks about Order #45821 in the first message, and in the second message refers to the order using the pronoun *"it"* without mentioning the order number again.
* **Traceability**: [tests/test_api_chat.py::test_conversation_follow_up](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/tests/test_api_chat.py#L111-L159)
* **Multi-Turn Dialogue**:
  - **Turn 1**:
    - **Customer**: *"Where is my order 45821?"*
    - **Agent**: *"Order #45821 is Shipped and expected to arrive on September 28, 2026."*
  - **Turn 2**:
    - **Customer**: *"When will it arrive?"*
    - **Agent**: *"It is scheduled for delivery on September 28, 2026."*
* **Memory Evaluation**:
  - Agent checkpointer inspected prior state messages for `thread_id: test-follow-up-45821`.
  - Resolved *"it"* to Order #45821 from the preceding turn.
* **Result**: `PASS` (Context persisted across requests; follow-up answered correctly without re-prompting).

---

### TC-13: Multiple Requests (Memory Isolation)

* **Scenario Description**: Validates that concurrent conversations with distinct `thread_id` values maintain strict data isolation, ensuring Order A's details never leak into Conversation B.
* **Traceability**: [tests/test_api_chat.py::test_conversation_memory_isolation](file:///c:/Users/Samyu/D%20Drive%28hp%29/Internship/2026/DStarix%20Techno/ai_customer_support_ticket_system/DStarix_ai_customer_support_ticket_system/tests/test_api_chat.py#L160-L228)
* **Multi-Session Dialogue Sequence**:
  - **Thread Alpha** (`test-isolation-customer-001`):
    - *Message 1*: *"Where is my order 45821?"* -> Agent confirms Order #45821 is Shipped.
  - **Thread Beta** (`test-isolation-customer-002`):
    - *Message 1*: *"Where is my order 45825?"* -> Agent confirms Order #45825 is Processing.
  - **Thread Alpha Follow-up**:
    - *Message 2*: *"When will it arrive?"* -> Agent references September 28 delivery for **Order #45821**.
  - **Thread Beta Follow-up**:
    - *Message 2*: *"When will it arrive?"* -> Agent explains **Order #45825** is still Processing and has not shipped yet.
  - **Thread Gamma (New Thread)**:
    - *Message 1*: *"When will it arrive?"* -> Agent has **zero context** and prompts: *"Could you please share your order number?"*
* **Result**: `PASS` (100% memory isolation verified; zero cross-contamination between sessions).

---

## 3. How to Run the Test Suite

All tests can be executed and reproduced locally using the following commands:

```powershell
# 1. Run the full Pytest test suite
.\venv\Scripts\pytest.exe -v

# 2. Run chat API integration tests only
.\venv\Scripts\pytest.exe tests/test_api_chat.py -v

# 3. Run escalation scenarios verification script
python scripts/test_escalation_scenarios.py

# 4. Run fault-tolerance and controlled failure scripts
python scripts/test_tool_failure_handling.py
python scripts/test_rag_failure_handling.py

# 5. Run end-to-end API integration tests
python scripts/test_api_integration.py
```


