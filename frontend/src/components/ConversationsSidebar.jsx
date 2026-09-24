import { useState, useMemo } from "react";
import {
  MessageSquarePlus,
  MessageSquare,
  Trash2,
  Search,
  Package,
  Ticket,
  Clock,
  HelpCircle,
  Sparkles,
  Loader2,
  X
} from "lucide-react";
import BackendHealthIndicator from "./BackendHealthIndicator";
import HelpCenter from "./HelpCenter";

export default function ConversationsSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isLoading,
  onOpenOrderLookup,
  onOpenTickets,
  onSelectTopic,
  isMobileOpen,
  onCloseMobile,
}) {
  const [activeTab, setActiveTab] = useState("chats"); // "chats" | "help"
  const [searchTerm, setSearchTerm] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  const filteredConversations = useMemo(() => {
    if (!searchTerm.trim()) return conversations;
    const term = searchTerm.toLowerCase();
    return conversations.filter(
      (c) =>
        (c.title && c.title.toLowerCase().includes(term)) ||
        (c.category && c.category.toLowerCase().includes(term)) ||
        (c.last_message && c.last_message.toLowerCase().includes(term))
    );
  }, [conversations, searchTerm]);

  const formatTimestamp = (isoString) => {
    if (!isoString) return "";
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.round(diffMs / (1000 * 60));
      const diffHours = Math.round(diffMs / (1000 * 60 * 60));

      if (diffMins < 1) return "Just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24 && date.getDate() === now.getDate()) {
        return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      }
      return date.toLocaleDateString([], { month: "short", day: "numeric" });
    } catch {
      return "";
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    setDeletingId(id);
    try {
      await onDeleteConversation(id);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div className="mobile-sidebar-backdrop" onClick={onCloseMobile} />
      )}

      <aside className={`conversations-sidebar ${isMobileOpen ? "mobile-open" : ""}`}>
        {/* Brand Header */}
        <div className="sidebar-brand-section">
          <div className="brand-logo-wrap">
            <div className="brand-logo-icon">
              <Sparkles size={18} className="text-white" />
            </div>
            <div>
              <h2 className="brand-name">NovaCart AI</h2>
              <span className="brand-badge">Customer Support</span>
            </div>
          </div>
          {isMobileOpen && (
            <button
              type="button"
              className="mobile-close-btn"
              onClick={onCloseMobile}
            >
              <X size={20} />
            </button>
          )}
        </div>

        {/* New Chat Button */}
        <div className="sidebar-action-wrap">
          <button
            type="button"
            className="new-chat-btn"
            onClick={() => {
              onNewConversation();
              setActiveTab("chats");
              if (isMobileOpen) onCloseMobile();
            }}
          >
            <MessageSquarePlus size={16} />
            <span>New Conversation</span>
          </button>
        </div>

        {/* Sidebar Nav Tabs: Chats vs Help Center */}
        <div className="sidebar-tabs-row">
          <button
            type="button"
            className={`sidebar-tab-btn ${activeTab === "chats" ? "active" : ""}`}
            onClick={() => setActiveTab("chats")}
          >
            <MessageSquare size={13} />
            <span>Chats ({conversations.length})</span>
          </button>
          <button
            type="button"
            className={`sidebar-tab-btn ${activeTab === "help" ? "active" : ""}`}
            onClick={() => setActiveTab("help")}
          >
            <HelpCircle size={13} />
            <span>Help Center</span>
          </button>
        </div>

        {/* TAB 1: HELP CENTER */}
        {activeTab === "help" ? (
          <div className="sidebar-help-container">
            <HelpCenter
              onSelectTopic={(topic) => {
                onSelectTopic(topic);
                setActiveTab("chats");
                if (isMobileOpen) onCloseMobile();
              }}
              onOpenOrderLookup={() => {
                onOpenOrderLookup();
                if (isMobileOpen) onCloseMobile();
              }}
            />
          </div>
        ) : (
          /* TAB 2: CONVERSATIONS LIST */
          <>
            {/* Search Input */}
            <div className="sidebar-search-wrap">
              <Search size={14} className="sidebar-search-icon" />
              <input
                type="text"
                className="sidebar-search-input"
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button
                  type="button"
                  className="search-clear-btn"
                  onClick={() => setSearchTerm("")}
                >
                  <X size={12} />
                </button>
              )}
            </div>

            {/* Conversation List */}
            <div className="sidebar-history-container">
              <div className="history-header">
                <span className="history-title">Recent Chats</span>
                <span className="history-count">{filteredConversations.length}</span>
              </div>

              {isLoading ? (
                <div className="history-loading-state">
                  <Loader2 size={20} className="animate-spin text-muted" />
                  <span>Loading conversations...</span>
                </div>
              ) : filteredConversations.length === 0 ? (
                <div className="history-empty-state">
                  <MessageSquare size={28} className="empty-icon" />
                  <p className="empty-title">
                    {searchTerm ? "No matches found" : "No previous chats"}
                  </p>
                  <p className="empty-desc">
                    {searchTerm
                      ? "Try another search term"
                      : "Your support conversations will appear here"}
                  </p>
                </div>
              ) : (
                <div className="history-list">
                  {filteredConversations.map((conv) => {
                    const isActive = conv.id === activeConversationId;
                    const isBeingDeleted = deletingId === conv.id;

                    return (
                      <div
                        key={conv.id}
                        className={`history-item ${isActive ? "active" : ""}`}
                        onClick={() => {
                          onSelectConversation(conv.id);
                          if (isMobileOpen) onCloseMobile();
                        }}
                      >
                        <div className="history-item-top">
                          <span className="history-item-title" title={conv.title}>
                            {conv.title || "Support Conversation"}
                          </span>
                          <button
                            type="button"
                            className="history-delete-btn"
                            title="Delete conversation"
                            disabled={isBeingDeleted}
                            onClick={(e) => handleDelete(e, conv.id)}
                          >
                            {isBeingDeleted ? (
                              <Loader2 size={13} className="animate-spin" />
                            ) : (
                              <Trash2 size={13} />
                            )}
                          </button>
                        </div>

                        <div className="history-item-meta">
                          {conv.category && (
                            <span className="history-category-pill">
                              {conv.category}
                            </span>
                          )}
                          <span className="history-time">
                            <Clock size={11} className="inline mr-1" />
                            {formatTimestamp(conv.updated_at || conv.created_at)}
                          </span>
                          {conv.message_count > 0 && (
                            <span className="history-count-pill">
                              {conv.message_count}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}

        {/* Quick Tools & Modals */}
        <div className="sidebar-tools-section">
          <div className="sidebar-tools-title">Support Tools</div>
          <div className="sidebar-tools-grid">
            <button
              type="button"
              className="sidebar-tool-btn"
              onClick={() => {
                onOpenOrderLookup();
                if (isMobileOpen) onCloseMobile();
              }}
            >
              <Package size={15} />
              <span>Order Lookup</span>
            </button>
            <button
              type="button"
              className="sidebar-tool-btn"
              onClick={() => {
                onOpenTickets();
                if (isMobileOpen) onCloseMobile();
              }}
            >
              <Ticket size={15} />
              <span>My Tickets</span>
            </button>
          </div>
        </div>

        {/* Footer with Backend Health */}
        <div className="sidebar-footer">
          <BackendHealthIndicator />
        </div>
      </aside>
    </>
  );
}
