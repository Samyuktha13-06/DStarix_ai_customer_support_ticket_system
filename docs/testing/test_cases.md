# NovaCart AI Customer Support & Ticket Automation System
## Test Case Specifications Document

This document defines the formal test cases, preconditions, execution steps, expected outcomes, and acceptance criteria for validating the **NovaCart AI Customer Support & Ticket Automation System**.

---

## 1. Test Plan Overview

### 1.1 Scope
The testing scope encompasses the end-to-end customer support lifecycle, including:
- **Retrieval-Augmented Generation (RAG)**: Accuracy and strict grounding of knowledge-base responses.
- **ReAct Agent & Tool Calling**: Safe execution of order lookup, delivery status, payment lookup, and ticket creation.
- **Conversation State & Memory**: Multi-turn context preservation and concurrent thread isolation via LangGraph checkpointing.
- **Automated Escalation**: Trigger detection for explicit human handoff requests and transactional discrepancies.
- **Fault Tolerance & Error Resilience**: Controlled recovery from vector database outages, tool timeouts, and invalid inputs.
- **API Contract Validation**: Compliance with HTTP status codes, schema validation, and structured JSON responses.

### 1.2 Test Environment
- **Backend Framework**: FastAPI on Python 3.14
- **Language Model**: Groq API (`llama-3.3-70b-versatile`)
- **Orchestration**: LangChain Core & LangGraph State Graph
- **Vector Database**: ChromaDB (`sentence-transformers/all-MiniLM-L6-v2` embeddings)
- **Relational Database**: SQLite via SQLAlchemy ORM
- **Test Automation**: Pytest, Starlette TestClient

---

## 2. Test Case Traceability Matrix

| Test Case ID | Test Case Name | Category | Priority | Automated Test Reference |
| :--- | :--- | :--- | :---: | :--- |
| **TC-01** | General FAQ | Knowledge Base | Medium | `tests/test_api_chat.py::test_basic_chat` |
| **TC-02** | Knowledge-Base Question | Knowledge Base | High | `tests/test_api_chat.py::test_chat_response_structure` |
| **TC-03** | Refund Question | Policy Grounding | High | `scripts/test_api_integration.py::test_knowledge_base_query` |
| **TC-04** | Order Status | Tool Calling | Critical | `scripts/test_api_integration.py::test_order_query` |
| **TC-05** | Payment Status | Tool Calling | High | `tests/test_tools_integration.py::test_payment_tool_returns_payment` |
| **TC-06** | Ticket Creation | Ticket Automation | Critical | `scripts/test_tools.py` |
| **TC-07** | Human Escalation | Escalation Engine | Critical | `tests/test_api_chat.py::test_payment_order_issue_escalates` |
| **TC-08** | Unknown Question | Guardrails & Grounding | Medium | `scripts/test_escalation_scenarios.py` |
| **TC-09** | Invalid Order ID | Input Validation | High | `scripts/test_escalation_scenarios.py` |
| **TC-10** | Tool Failure | Fault Tolerance | High | `scripts/test_tool_failure_handling.py` |
| **TC-11** | Retrieval Failure | Fault Tolerance | High | `scripts/test_rag_failure_handling.py` |
| **TC-12** | Conversation Follow-Up | Memory & Context | Critical | `tests/test_api_chat.py::test_conversation_follow_up` |
| **TC-13** | Multiple Requests | Session Isolation | Critical | `tests/test_api_chat.py::test_conversation_memory_isolation` |
| **TC-14** | Empty Message Validation | API Validation | Medium | `tests/test_api_chat.py::test_empty_message` |
| **TC-15** | Whitespace Message Validation | API Validation | Medium | `tests/test_api_chat.py::test_whitespace_message` |
| **TC-16** | System Health & Readiness | System Operations | High | `tests/test_main.py::test_health_check` |

---

## 3. Detailed Test Case Specifications

### TC-01: General FAQ
* **Test Case ID**: `TC-01`
* **Test Title**: General FAQ - Standard Shipping Inquiry
* **Module**: RAG Knowledge Base Retrieval
* **Priority**: Medium
* **Preconditions**:
  - ChromaDB contains indexed chunks of `knowledge_base/shipping_policy.md`.
  - FastAPI server is running with healthy LLM API credentials.
* **Test Steps**:
  1. Construct HTTP POST request to `/chat`.
  2. Provide a valid `thread_id` and query: `"How long does standard delivery take?"`.
  3. Send request and capture HTTP status code and response payload.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Response contains standard delivery estimate (3–5 business days).
  - `escalated` is `false`.
  - `ticket_id` is `null`.
* **Acceptance Criteria**:
  - Answer is strictly grounded in `shipping_policy.md` without hallucinatory guarantees.

---

### TC-02: Knowledge-Base Question
* **Test Case ID**: `TC-02`
* **Test Title**: Knowledge-Base Question - Order Cancellation Policy
* **Module**: RAG Semantic Retrieval & Schema Verification
* **Priority**: High
* **Preconditions**:
  - `knowledge_base/cancellation_policy.md` is ingested in ChromaDB.
* **Test Steps**:
  1. Send POST request to `/chat` with message: `"What is your cancellation policy?"`.
  2. Verify that `query_knowledge_base` is invoked by the LangGraph agent.
  3. Validate complete JSON response structure against `ChatResponse` model.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Response explains that orders can only be canceled prior to dispatch/shipping.
  - JSON payload contains all mandatory keys: `answer`, `escalated`, `ticket_id`, `order`, `payment`, `tools_used`, `customer`.
* **Acceptance Criteria**:
  - Accurate policy synthesis with zero hallucinated exceptions.

---

### TC-03: Refund Question
* **Test Case ID**: `TC-03`
* **Test Title**: Policy Grounding - Return Window & Refund Method
* **Module**: RAG Policy Ingestion
* **Priority**: High
* **Preconditions**:
  - Vector index contains `knowledge_base/refund_policy.md`.
* **Test Steps**:
  1. Submit query: `"What is your refund policy and how many days do I have to return an item?"`.
  2. Inspect generated answer for return timeframe and payment refund details.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Response states the 7-calendar-day return window.
  - Explains that refunds are credited to the original payment method within 5–7 business days.
* **Acceptance Criteria**:
  - Explicit mention of 7 calendar days return period and refund timeline.

---

### TC-04: Order Status
* **Test Case ID**: `TC-04`
* **Test Title**: Order Status Lookup - Valid Seeded Order #45821
* **Module**: Database Tool Calling (`check_order_status`)
* **Priority**: Critical
* **Preconditions**:
  - SQLite database seeded with Order #45821 (Product: Wireless Headphones, Status: Shipped, Tracking: NVC45821001).
* **Test Steps**:
  1. Submit POST request: `"What is the status of order 45821?"`.
  2. Verify agent tool selection node triggers `check_order_status(order_id=45821)`.
  3. Verify agent extracts delivery tracking number and expected date.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Response contains "Shipped", tracking number `NVC45821001`, and expected delivery date.
  - `order` dictionary in response includes `order_id: 45821`, `status: "Shipped"`, and `product`.
* **Acceptance Criteria**:
  - Database values match SQLite records exactly; `escalated` remains `false`.

---

### TC-05: Payment Status
* **Test Case ID**: `TC-05`
* **Test Title**: Payment Status Lookup - Order #45824
* **Module**: Financial Tool Integration (`check_payment_status`)
* **Priority**: High
* **Preconditions**:
  - SQLite `payments` table contains record for Order #45824 with status `Captured` and amount `$79.99`.
* **Test Steps**:
  1. Submit query: `"What is the payment status for order 45824?"`.
  2. Check that agent calls `check_payment_status(order_id=45824)`.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Response confirms payment status is `Captured` and amount is `$79.99`.
  - `payment` object populated in API response.
* **Acceptance Criteria**:
  - Financial data retrieved securely and mapped to the corresponding order.

---

### TC-06: Ticket Creation
* **Test Case ID**: `TC-06`
* **Test Title**: Support Ticket Creation - Damaged Item Complaint
* **Module**: Ticket Automation Tool (`create_support_ticket`)
* **Priority**: Critical
* **Preconditions**:
  - Seeded Order #45822 exists in database.
  - `tickets` table is accessible and writable.
* **Test Steps**:
  1. Submit query: `"Please create a support ticket for my order 45822. The package arrived with severe physical damage."`.
  2. Agent parses issue description, assigns `High` priority, and invokes ticket tool.
  3. Verify new record created in `tickets` table.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Response provides a valid integer `ticket_id`.
  - Ticket status is `Open` and priority is `High`.
* **Acceptance Criteria**:
  - Ticket record successfully persisted in SQLite with valid foreign key to order/customer.

---

### TC-07: Human Escalation
* **Test Case ID**: `TC-07`
* **Test Title**: Automatic Escalation - Payment Captured vs Order Failed Inconsistency
* **Module**: Escalation Reasoning Engine
* **Priority**: Critical
* **Preconditions**:
  - Order #45824 status is `Failed`.
  - Associated payment record for Order #45824 is `Captured`.
* **Test Steps**:
  1. Submit message: `"My payment was deducted but my order 45824 failed."`.
  2. Agent executes `check_order_status` and `check_payment_status`.
  3. Agent reasoning detects state mismatch and triggers escalation flow.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - `escalated`: `true`
  - `ticket_id`: Integer assigned (e.g. `302`).
  - Response reassures customer that a human support specialist is assigned.
* **Acceptance Criteria**:
  - High severity issues automatically escalate without requiring explicit customer demand.

---

### TC-08: Unknown Question
* **Test Case ID**: `TC-08`
* **Test Title**: Grounding Guardrails - Out-of-Domain Query Handling
* **Module**: Anti-Hallucination & Scope Enforcement
* **Priority**: Medium
* **Preconditions**:
  - Knowledge base contains only NovaCart e-commerce policies.
* **Test Steps**:
  1. Submit query: `"What is the current stock price of Tesla and do you deliver by drone to the moon?"`.
  2. Check vector retrieval scores and similarity distance threshold.
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Agent politely states lack of information in store documentation.
  - Zero invented facts; `escalated` is `false`.
* **Acceptance Criteria**:
  - Guardrails prevent hallucinations and keep responses bounded to company domain.

---

### TC-09: Invalid Order ID
* **Test Case ID**: `TC-09`
* **Test Title**: Graceful Error Handling - Non-Existent Order Query
* **Module**: Tool Exception Handling
* **Priority**: High
* **Preconditions**:
  - Order #99999 does not exist in the database.
* **Test Steps**:
  1. Submit query: `"Where is my order 99999?"`.
  2. Tool executes lookup and returns not-found signal (`success: false`).
* **Expected Result**:
  - HTTP Status: `200 OK`
  - Agent politely informs user that order #99999 could not be located.
  - Suggests verifying the number or checking email receipt.
* **Acceptance Criteria**:
  - No 500 internal server error or unhandled database exception exposed to client.

---

### TC-10: Tool Failure
* **Test Case ID**: `TC-10`
* **Test Title**: Fault Tolerance - Controlled Tool Operational Failure
* **Module**: Agent Graph Error Boundaries
* **Priority**: High
* **Preconditions**:
  - Tool execution failure simulated via test harness (`controlled_failure_tool`).
* **Test Steps**:
  1. Trigger query invoking a tool that raises an operational exception.
  2. Verify error boundary intercepts exception and returns structured error payload.
  3. Graph continues execution to format graceful user explanation.
* **Expected Result**:
  - Process does not crash; server remains responsive.
  - Agent communicates temporary system unavailability.
* **Acceptance Criteria**:
  - Resilient error handling prevents unhandled server termination.

---

### TC-11: Retrieval Failure
* **Test Case ID**: `TC-11`
* **Test Title**: Fault Tolerance - Vector Store Outage Recovery
* **Module**: RAG Subsystem Resilience
* **Priority**: High
* **Preconditions**:
  - ChromaDB simulated offline or query throws simulated vector store error.
* **Test Steps**:
  1. Submit knowledge-base query while retrieval is disrupted.
  2. Check exception handling in `app/rag/retriever.py`.
* **Expected Result**:
  - Error logged with traceback.
  - Safe fallback message delivered to customer offering manual support.
  - HTTP 500 error avoided.
* **Acceptance Criteria**:
  - System gracefully degrades when vector indexing service is unavailable.

---

### TC-12: Conversation Follow-Up
* **Test Case ID**: `TC-12`
* **Test Title**: Multi-Turn Context Memory - Coreference Pronoun Resolution
* **Module**: LangGraph Memory Checkpointer
* **Priority**: Critical
* **Preconditions**:
  - Order #45821 exists with status `Shipped` and delivery date `2026-09-28`.
* **Test Steps**:
  1. Send Turn 1 using `thread_id="test-follow-up-45821"`:
     `"Where is my order 45821?"`
  2. Receive response confirming order status.
  3. Send Turn 2 on the same `thread_id`:
     `"When will it arrive?"`
* **Expected Result**:
  - Turn 1 returns status of Order #45821.
  - Turn 2 resolves pronoun *"it"* to Order #45821 and answers with expected arrival date.
  - Agent does NOT prompt customer to repeat order number.
* **Acceptance Criteria**:
  - Conversational context persists across multiple HTTP requests on identical thread IDs.

---

### TC-13: Multiple Requests (Session Isolation)
* **Test Case ID**: `TC-13`
* **Test Title**: Thread Isolation - Multi-Session State Separation
* **Module**: LangGraph Multi-Tenancy State Engine
* **Priority**: Critical
* **Preconditions**:
  - Order #45821 is `Shipped`; Order #45825 is `Processing`.
* **Test Steps**:
  1. Thread A (`cust-001`): `"Where is my order 45821?"`.
  2. Thread B (`cust-002`): `"Where is my order 45825?"`.
  3. Thread A follow-up: `"When will it arrive?"`.
  4. Thread B follow-up: `"When will it arrive?"`.
  5. Thread C (brand new thread): `"When will it arrive?"`.
* **Expected Result**:
  - Thread A refers strictly to Order #45821.
  - Thread B refers strictly to Order #45825.
  - Thread C prompts customer for an order number.
* **Acceptance Criteria**:
  - Zero context leakage or data contamination across distinct `thread_id` sessions.

---

### TC-14: Empty Message Validation
* **Test Case ID**: `TC-14`
* **Test Title**: Input Validation - Empty String Rejection
* **Module**: API Request Validation
* **Priority**: Medium
* **Preconditions**:
  - Server is running.
* **Test Steps**:
  1. Send POST request to `/chat` with payload:
     `{"thread_id": "test-empty", "message": ""}`.
* **Expected Result**:
  - HTTP Status: `422 Unprocessable Entity`
  - Detail message specifies validation failure on field `message`.
* **Acceptance Criteria**:
  - Pydantic schema validation rejects zero-length input strings.

---

### TC-15: Whitespace Message Validation
* **Test Case ID**: `TC-15`
* **Test Title**: Input Validation - Whitespace-Only Message Rejection
* **Module**: API Endpoint & Business Logic Validation
* **Priority**: Medium
* **Preconditions**:
  - Server is running.
* **Test Steps**:
  1. Send POST request to `/chat` with payload:
     `{"thread_id": "test-whitespace", "message": "   "}`.
* **Expected Result**:
  - HTTP Status: `400 Bad Request`
  - Error message: `"Customer message cannot be empty."`
* **Acceptance Criteria**:
  - Endpoint rejects blank or whitespace-only inputs without executing LLM pipeline or creating empty DB records.

---

### TC-16: System Health & Readiness
* **Test Case ID**: `TC-16`
* **Test Title**: System Operations - Health and Readiness Probes
* **Module**: System Observability & Monitoring
* **Priority**: High
* **Preconditions**:
  - SQLite database is initialized.
* **Test Steps**:
  1. Send GET request to `/health`.
  2. Send GET request to `/ready`.
* **Expected Result**:
  - `/health` returns HTTP 200 with `{"status": "healthy"}`.
  - `/ready` returns HTTP 200 with `{"status": "ready", "database": "available"}`.
* **Acceptance Criteria**:
  - Monitoring probes accurately report application and database operational state.

---

## 4. Test Execution Guidelines

### Executing the Test Suite

```powershell
# Run full Pytest regression suite
.\venv\Scripts\pytest.exe -v

# Run API contract and integration tests
.\venv\Scripts\pytest.exe tests/test_api_chat.py -v

# Run escalation reasoning and failure resilience tests
python scripts/test_escalation_scenarios.py
python scripts/test_tool_failure_handling.py
python scripts/test_rag_failure_handling.py
```

### Pass Criteria
- **100% of Critical and High priority test cases must pass.**
- **Zero unhandled 500 Internal Server Errors under any test condition.**
- **All RAG queries must strictly adhere to knowledge base content with zero hallucination.**
