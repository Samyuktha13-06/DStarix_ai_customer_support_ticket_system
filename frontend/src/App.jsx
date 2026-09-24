import { useEffect, useRef, useState, useCallback } from "react";
import {
  Bot,
  Send,
  Sparkles,
  MessageSquare,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  AlertTriangle,
  Clock,
  ArrowDown,
  Menu,
  HelpCircle,
  Trash2,
  Loader2,
  Package,
  Ticket as TicketIcon
} from "lucide-react";

import "./index.css";
import { API_BASE_URL } from "./config";
import MarkdownText from "./components/MarkdownText";
import OrderLookupModal from "./components/OrderLookupModal";
import TicketsModal from "./components/TicketsModal";
import ConfirmModal from "./components/ConfirmModal";
import ConversationsSidebar from "./components/ConversationsSidebar";
import RightPanel from "./components/RightPanel";
import EmptyChatHero from "./components/EmptyChatHero";
import ToolIndicator from "./components/ToolIndicator";
import EscalationCard from "./components/EscalationCard";
import BackendHealthIndicator from "./components/BackendHealthIndicator";

const generateThreadId = () => {
  return "thread-" + Date.now().toString(36) + "-" + Math.random().toString(36).substring(2, 7);
};

const getFormattedTime = () => {
  return new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
};

const INITIAL_WELCOME_MESSAGE = {
  id: "welcome",
  role: "assistant",
  content: "Hello! I'm NovaCart AI Support. How can I help you today?",
  timestamp: "Just now",
  tools_used: [],
};

export default function App() {
  /*
   * ---------------------------------------------------------
   * STATE
   * ---------------------------------------------------------
   */
  const [threadId, setThreadId] = useState(() => {
    return localStorage.getItem("novacart_current_thread_id") || generateThreadId();
  });

  const [conversations, setConversations] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(false);

  const [messages, setMessages] = useState([INITIAL_WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [activeToolActivity, setActiveToolActivity] = useState("");

  const [activeOrder, setActiveOrder] = useState(null);
  const [activePayment, setActivePayment] = useState(null);
  const [activeTicket, setActiveTicket] = useState(null);
  const [customerInfo, setCustomerInfo] = useState(null);

  // Modals state
  const [isOrderLookupOpen, setIsOrderLookupOpen] = useState(false);
  const [isTicketsOpen, setIsTicketsOpen] = useState(false);
  const [isConfirmClearOpen, setIsConfirmClearOpen] = useState(false);

  // Mobile drawer states
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [isMobileRightPanelOpen, setIsMobileRightPanelOpen] = useState(false);

  // Scroll to bottom state
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  // Copy indicator & feedback state
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [feedbackState, setFeedbackState] = useState({});

  const messagesContainerRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  /*
   * ---------------------------------------------------------
   * PERSISTENCE: LOAD & SYNC CONVERSATIONS
   * ---------------------------------------------------------
   */
  const fetchConversations = useCallback(async () => {
    try {
      setLoadingConversations(true);
      const res = await fetch(`${API_BASE_URL}/conversations`);
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (err) {
      console.warn("Could not fetch conversations list from backend:", err);
    } finally {
      setLoadingConversations(false);
    }
  }, []);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  // Save current thread ID
  useEffect(() => {
    if (threadId) {
      localStorage.setItem("novacart_current_thread_id", threadId);
    }
  }, [threadId]);

  // Load a conversation from backend
  const loadConversation = async (targetThreadId) => {
    try {
      setLoadingHistory(true);
      setThreadId(targetThreadId);

      const res = await fetch(`${API_BASE_URL}/conversations/${targetThreadId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
          const loadedMsgs = data.messages.map((m) => {
            const meta = m.meta || {};
            return {
              id: m.id,
              role: m.sender,
              content: m.content,
              timestamp: m.created_at
                ? new Date(m.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })
                : "Just now",
              order: meta.order || null,
              payment: meta.payment || null,
              escalated: meta.escalated || false,
              ticket_id: meta.ticket_id || null,
              tools_used: meta.tools_used || [],
              feedback: meta.feedback || null,
            };
          });
          setMessages(loadedMsgs);

          // Update right panel active context from latest message or conversation
          const lastMsgWithOrder = [...loadedMsgs].reverse().find((m) => m.order);
          if (lastMsgWithOrder) {
            setActiveOrder(lastMsgWithOrder.order);
            if (lastMsgWithOrder.payment) setActivePayment(lastMsgWithOrder.payment);
          } else {
            setActiveOrder(null);
            setActivePayment(null);
          }

          const lastMsgWithTicket = [...loadedMsgs].reverse().find((m) => m.escalated && m.ticket_id);
          if (lastMsgWithTicket) {
            setActiveTicket({
              id: lastMsgWithTicket.ticket_id,
              priority: "High",
              status: "Open",
            });
          } else {
            setActiveTicket(null);
          }

          if (data.customer_name || data.customer_email) {
            setCustomerInfo({
              id: data.customer_id,
              name: data.customer_name,
              email: data.customer_email,
            });
          } else {
            setCustomerInfo(null);
          }
        } else {
          setMessages([INITIAL_WELCOME_MESSAGE]);
          setActiveOrder(null);
          setActivePayment(null);
          setActiveTicket(null);
          setCustomerInfo(null);
        }
      } else {
        // Fallback for new empty thread
        setMessages([INITIAL_WELCOME_MESSAGE]);
        setActiveOrder(null);
        setActivePayment(null);
        setActiveTicket(null);
        setCustomerInfo(null);
      }
    } catch (err) {
      console.warn("Could not load conversation from backend:", err);
      setMessages([INITIAL_WELCOME_MESSAGE]);
    } finally {
      setLoadingHistory(false);
      scrollToBottom();
    }
  };

  // Start a fresh new conversation
  const handleNewConversation = () => {
    const newId = generateThreadId();
    setThreadId(newId);
    setMessages([INITIAL_WELCOME_MESSAGE]);
    setActiveOrder(null);
    setActivePayment(null);
    setActiveTicket(null);
    setCustomerInfo(null);
    setInput("");
    inputRef.current?.focus();
    scrollToBottom();
  };

  // Delete a conversation
  const handleDeleteConversation = async (convId) => {
    try {
      await fetch(`${API_BASE_URL}/conversations/${convId}`, { method: "DELETE" });
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (convId === threadId) {
        handleNewConversation();
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  /*
   * ---------------------------------------------------------
   * SCROLLING
   * ---------------------------------------------------------
   */
  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  };

  const handleScroll = () => {
    if (!messagesContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const isScrolledUp = scrollHeight - scrollTop - clientHeight > 140;
    setShowScrollBottom(isScrolledUp);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  /*
   * ---------------------------------------------------------
   * SEND MESSAGE & CHAT HANDLER
   * ---------------------------------------------------------
   */
  const handleSend = async (customMessage = null) => {
    const messageToSend = typeof customMessage === "string" ? customMessage : input;
    const clean = messageToSend.trim();
    if (!clean || loading) return;

    const userTimestamp = getFormattedTime();
    const newUserMsg = {
      role: "user",
      content: clean,
      timestamp: userTimestamp,
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInput("");
    setLoading(true);

    // Dynamic tool activity message
    const lower = clean.toLowerCase();
    if (lower.includes("order") || lower.includes("track")) {
      setActiveToolActivity("Looking up order in database...");
    } else if (lower.includes("refund") || lower.includes("return") || lower.includes("policy")) {
      setActiveToolActivity("Searching NovaCart knowledge base...");
    } else if (lower.includes("human") || lower.includes("support") || lower.includes("agent")) {
      setActiveToolActivity("Checking agent availability and ticket queue...");
    } else {
      setActiveToolActivity("Processing support request...");
    }

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: clean,
          thread_id: threadId,
          customer_id: customerInfo?.id || activeOrder?.customer_id || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      const asstTimestamp = getFormattedTime();

      const newAsstMsg = {
        role: "assistant",
        content: data.answer,
        timestamp: asstTimestamp,
        order: data.order,
        payment: data.payment,
        escalated: data.escalated,
        ticket_id: data.ticket_id,
        tools_used: data.tools_used || [],
      };

      setMessages((prev) => [...prev, newAsstMsg]);

      // Update right panel context
      if (data.order) setActiveOrder(data.order);
      if (data.payment) setActivePayment(data.payment);
      if (data.customer) setCustomerInfo(data.customer);
      if (data.escalated && data.ticket_id) {
        setActiveTicket({
          id: data.ticket_id,
          priority: "High",
          status: "Open",
        });
      }

      // Refresh conversations list in sidebar to reflect title & updated timestamp
      fetchConversations();
    } catch (err) {
      console.error("Chat request failed:", err);
      const errorMsg = {
        role: "assistant",
        isError: true,
        content: "Sorry, I encountered an issue connecting to the AI support server. Please verify the backend connection and try again.",
        failedUserMessage: clean,
        timestamp: getFormattedTime(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      setActiveToolActivity("");
      inputRef.current?.focus();
    }
  };

  // Retry failed response
  const handleRetry = (failedText) => {
    setMessages((prev) => prev.slice(0, -1));
    handleSend(failedText);
  };

  // Copy AI message
  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  // Feedback (Thumbs Up / Down)
  const handleFeedback = async (index, type, messageId = null) => {
    const current = feedbackState[index];
    const newFeedback = current === type ? null : type;

    setFeedbackState((prev) => ({
      ...prev,
      [index]: newFeedback,
    }));

    if (threadId) {
      try {
        await fetch(`${API_BASE_URL}/conversations/${threadId}/feedback`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message_id: messageId,
            feedback: newFeedback || "clear",
          }),
        });
      } catch (e) {
        console.warn("Feedback submission ignored:", e);
      }
    }
  };

  // Has only initial greeting
  const isChatEmpty = messages.length <= 1 && !messages.some((m) => m.role === "user");

  return (
    <div className="app-container">
      {/* ------------------------------------------------------- */}
      {/* 1. PREVIOUS CONVERSATIONS SIDEBAR */}
      {/* ------------------------------------------------------- */}
      <ConversationsSidebar
        conversations={conversations}
        activeConversationId={threadId}
        onSelectConversation={loadConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isLoading={loadingConversations}
        onOpenOrderLookup={() => setIsOrderLookupOpen(true)}
        onOpenTickets={() => setIsTicketsOpen(true)}
        onSelectTopic={(prompt) => handleSend(prompt)}
        isMobileOpen={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
      />

      {/* ------------------------------------------------------- */}
      {/* 2. MAIN CHAT AREA */}
      {/* ------------------------------------------------------- */}
      <main className="chat-main-area">
        {/* Top Header */}
        <header className="chat-top-header">
          <div className="chat-header-left">
            <button
              type="button"
              className="mobile-nav-toggle-btn"
              onClick={() => setIsMobileSidebarOpen(true)}
              title="Open Conversations"
            >
              <Menu size={18} />
            </button>

            <div className="active-conv-info">
              <h2 className="active-conv-title">
                {conversations.find((c) => c.id === threadId)?.title || "NovaCart AI Customer Support"}
              </h2>
              <div className="active-conv-badges">
                <span className="live-status-pill">
                  <span className="live-pulse" /> Live Assistant
                </span>
                {customerInfo && (
                  <span className="customer-tag">
                    Customer: {customerInfo.name}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="chat-header-right">
            {/* Clear conversation button */}
            <button
              type="button"
              className="header-action-btn"
              onClick={() => setIsConfirmClearOpen(true)}
              title="Clear current chat"
            >
              <RotateCcw size={15} />
              <span className="hidden-mobile">Clear</span>
            </button>

            {/* Mobile Right Panel Toggle */}
            <button
              type="button"
              className="header-action-btn mobile-hub-btn"
              onClick={() => setIsMobileRightPanelOpen(true)}
              title="Help & Details Hub"
            >
              <HelpCircle size={16} />
              <span>Help & Details</span>
            </button>
          </div>
        </header>

        {/* Messages Scroll Area */}
        <div
          className="chat-messages-container"
          ref={messagesContainerRef}
          onScroll={handleScroll}
        >
          {loadingHistory ? (
            <div className="history-loading-view">
              <Loader2 size={28} className="animate-spin text-primary" />
              <p>Restoring conversation...</p>
            </div>
          ) : (
            <>
              {/* Empty Chat Welcome Hero with 4 Quick Actions */}
              {isChatEmpty && (
                <EmptyChatHero
                  onTrackOrder={() => setIsOrderLookupOpen(true)}
                  onCheckPayment={() => handleSend("How can I check the payment status of an order?")}
                  onRefundPolicy={() => handleSend("What is NovaCart's return and refund policy?")}
                  onSpeakHuman={() => handleSend("I want to speak with a human support representative.")}
                />
              )}

              {/* Message List */}
              {messages.map((msg, idx) => {
                const isUser = msg.role === "user";
                const isError = msg.isError;
                const feedback = feedbackState[idx] || msg.feedback;

                return (
                  <div
                    key={msg.id || idx}
                    className={`message-row ${isUser ? "user-row" : "assistant-row"}`}
                  >
                    {!isUser && (
                      <div className="message-avatar assistant-avatar">
                        <Bot size={18} />
                      </div>
                    )}

                    <div className="message-bubble-wrapper">
                      <div className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"} ${isError ? "error-bubble" : ""}`}>
                        {isError ? (
                          <div className="error-content-row">
                            <AlertTriangle size={18} className="text-danger flex-shrink-0" />
                            <div>
                              <p>{msg.content}</p>
                              {msg.failedUserMessage && (
                                <button
                                  type="button"
                                  className="retry-action-btn"
                                  onClick={() => handleRetry(msg.failedUserMessage)}
                                >
                                  <RotateCcw size={13} /> Retry response
                                </button>
                              )}
                            </div>
                          </div>
                        ) : (
                          <>
                            <MarkdownText content={msg.content} />

                            {/* Better Ticket Escalation State Card */}
                            {msg.escalated && msg.ticket_id && (
                              <EscalationCard
                                ticket={{
                                  ticket_id: msg.ticket_id,
                                  priority: "High",
                                  status: "Open",
                                }}
                                onContinueChat={() => {
                                  inputRef.current?.focus();
                                  scrollToBottom();
                                }}
                              />
                            )}
                          </>
                        )}
                      </div>

                      {/* Message Meta: Timestamps, Copy, Feedback */}
                      <div className="message-meta-row">
                        <span className="message-timestamp">
                          <Clock size={11} /> {msg.timestamp || "Just now"}
                        </span>

                        {!isUser && !isError && (
                          <div className="message-actions">
                            {/* Copy button */}
                            <button
                              type="button"
                              className="msg-action-btn"
                              title="Copy AI response"
                              onClick={() => handleCopy(msg.content, idx)}
                            >
                              {copiedIndex === idx ? (
                                <span className="copied-indicator">
                                  <Check size={12} /> Copied
                                </span>
                              ) : (
                                <Copy size={12} />
                              )}
                            </button>

                            {/* Thumbs Up / Down */}
                            <button
                              type="button"
                              className={`msg-action-btn ${feedback === "like" ? "active-like" : ""}`}
                              title="Helpful response"
                              onClick={() => handleFeedback(idx, "like", msg.id)}
                            >
                              <ThumbsUp size={12} />
                            </button>
                            <button
                              type="button"
                              className={`msg-action-btn ${feedback === "dislike" ? "active-dislike" : ""}`}
                              title="Not helpful"
                              onClick={() => handleFeedback(idx, "dislike", msg.id)}
                            >
                              <ThumbsDown size={12} />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    {isUser && (
                      <div className="message-avatar user-avatar">
                        <span>You</span>
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Loading / Thinking Indicator */}
              {loading && (
                <div className="message-row assistant-row">
                  <div className="message-avatar assistant-avatar">
                    <Bot size={18} />
                  </div>
                  <div className="message-bubble-wrapper">
                    <div className="message-bubble assistant-bubble thinking-bubble">
                      <div className="thinking-dots">
                        <span className="dot" />
                        <span className="dot" />
                        <span className="dot" />
                      </div>
                      <span className="thinking-text">
                        NovaCart AI is thinking...
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Scroll-to-bottom Floating Button */}
        {showScrollBottom && (
          <button
            type="button"
            className="scroll-to-bottom-btn"
            onClick={scrollToBottom}
          >
            <ArrowDown size={14} />
            <span>Scroll to latest</span>
          </button>
        )}

        {/* Input Bar */}
        <div className="chat-composer-container">
          <form
            className="chat-composer-form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              ref={inputRef}
              type="text"
              className="chat-input"
              placeholder="Ask about orders, delivery, refunds, or support..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />

            <button
              type="submit"
              className="chat-send-btn"
              disabled={!input.trim() || loading}
              title="Send message"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
            </button>
          </form>
          <div className="composer-footer-note">
            <span>Powered by Groq LLM & NovaCart RAG Knowledge Base.</span>
          </div>
        </div>
      </main>

      {/* ------------------------------------------------------- */}
      {/* 3. RIGHT PANEL (HELP CENTER, ORDER, PAYMENT, TICKET) */}
      {/* ------------------------------------------------------- */}
      <RightPanel
        activeOrder={activeOrder}
        activePayment={activePayment}
        activeTicket={activeTicket}
        customerInfo={customerInfo}
        onClearOrder={() => setActiveOrder(null)}
        onClearTicket={() => setActiveTicket(null)}
        onOpenOrderLookup={() => setIsOrderLookupOpen(true)}
        isMobileOpen={isMobileRightPanelOpen}
        onCloseMobile={() => setIsMobileRightPanelOpen(false)}
      />

      {/* ------------------------------------------------------- */}
      {/* 4. MODALS */}
      {/* ------------------------------------------------------- */}
      <OrderLookupModal
        isOpen={isOrderLookupOpen}
        onClose={() => setIsOrderLookupOpen(false)}
        apiBaseUrl={API_BASE_URL}
        onSelectOrder={(orderData, paymentData) => {
          setActiveOrder(orderData);
          if (paymentData) setActivePayment(paymentData);
          if (orderData.customer_id) {
            setCustomerInfo((prev) => ({
              ...prev,
              id: orderData.customer_id,
            }));
          }
          handleSend(`I'm looking at Order #${orderData.order_id || orderData.id}. Can you give me the latest tracking and delivery details?`);
        }}
      />

      <TicketsModal
        isOpen={isTicketsOpen}
        onClose={() => setIsTicketsOpen(false)}
        apiBaseUrl={API_BASE_URL}
        onSelectTicket={(selectedTicket) => {
          setActiveTicket(selectedTicket);
          handleSend(`Can you provide an update on my support ticket #${selectedTicket.id}?`);
        }}
      />

      <ConfirmModal
        isOpen={isConfirmClearOpen}
        title="Start Fresh Conversation?"
        message="This will start a new conversation. Your previous conversation is saved in your sidebar history."
        confirmText="New Conversation"
        onConfirm={() => {
          setIsConfirmClearOpen(false);
          handleNewConversation();
        }}
        onClose={() => setIsConfirmClearOpen(false)}
      />
    </div>
  );
}