import { useState } from "react";
import { Wrench, BookOpen, Package, CreditCard, UserCheck, ChevronDown, ChevronUp, Check } from "lucide-react";

export default function ToolIndicator({ tools }) {
  const [expanded, setExpanded] = useState(false);

  if (!tools || tools.length === 0) return null;

  const getToolMeta = (name) => {
    switch (name) {
      case "search_knowledge_base":
        return {
          title: "Knowledge Base Search",
          desc: "Searched policy documents & guides",
          icon: BookOpen,
          color: "#3b82f6",
        };
      case "get_order_details":
        return {
          title: "Order Database",
          desc: "Fetched order details from database",
          icon: Package,
          color: "#8b5cf6",
        };
      case "get_payment_status":
        return {
          title: "Payment Records",
          desc: "Verified transaction & billing records",
          icon: CreditCard,
          color: "#059669",
        };
      case "escalate_to_human":
        return {
          title: "Escalation Dispatch",
          desc: "Created human support ticket",
          icon: UserCheck,
          color: "#dc2626",
        };
      case "get_customer_tickets":
        return {
          title: "Ticket Records",
          desc: "Retrieved customer support history",
          icon: Wrench,
          color: "#d97706",
        };
      default:
        return {
          title: name.replace(/_/g, " "),
          desc: "Executed system tool",
          icon: Wrench,
          color: "#6b7280",
        };
    }
  };

  return (
    <div className="tool-indicator-wrapper">
      <button
        type="button"
        className="tool-indicator-toggle"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="tool-indicator-left">
          <Wrench size={13} className="tool-main-icon" />
          <span className="tool-indicator-label">
            Tools used ({tools.length})
          </span>
        </div>
        <div className="tool-indicator-pills">
          {tools.map((t, idx) => {
            const meta = getToolMeta(t.name);
            return (
              <span key={idx} className="tool-mini-chip">
                {meta.title}
              </span>
            );
          })}
          {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
        </div>
      </button>

      {expanded && (
        <div className="tool-indicator-details">
          {tools.map((t, idx) => {
            const meta = getToolMeta(t.name);
            const Icon = meta.icon;
            const args = t.args || {};
            const argEntries = Object.entries(args);

            return (
              <div key={idx} className="tool-detail-item">
                <div className="tool-detail-header">
                  <div className="tool-detail-icon-wrap" style={{ color: meta.color }}>
                    <Icon size={14} />
                  </div>
                  <div className="tool-detail-text">
                    <span className="tool-detail-title">{meta.title}</span>
                    <span className="tool-detail-desc">{meta.desc}</span>
                  </div>
                  <span className="tool-detail-status">
                    <Check size={12} /> Complete
                  </span>
                </div>
                {argEntries.length > 0 && (
                  <div className="tool-detail-args">
                    {argEntries.map(([k, v]) => (
                      <span key={k} className="tool-arg-pill">
                        <strong>{k}:</strong> {typeof v === "object" ? JSON.stringify(v) : String(v)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
