import { CheckCircle2, MessageSquare, Clock, UserCheck } from "lucide-react";

export default function EscalationCard({ ticket, onContinueChat }) {
  if (!ticket) return null;

  const ticketId = ticket.ticket_id || ticket.id || "Pending";
  const priority = ticket.priority || "High";
  const status = ticket.status || "Open";

  return (
    <div className="escalation-explicit-card">
      <div className="escalation-card-header">
        <div className="escalation-header-icon">
          <CheckCircle2 size={18} className="text-emerald-500" />
        </div>
        <span className="escalation-header-title">Human Support Requested</span>
      </div>

      <div className="escalation-card-body">
        <div className="escalation-ticket-num">
          Ticket #{ticketId}
        </div>
        <div className="escalation-detail-row">
          <span className="escalation-label">Priority:</span>
          <span className={`escalation-value priority-${priority.toLowerCase()}`}>
            {priority}
          </span>
        </div>
        <div className="escalation-detail-row">
          <span className="escalation-label">Status:</span>
          <span className="escalation-value status-badge">{status}</span>
        </div>

        <p className="escalation-message">
          A support representative will contact you shortly.
        </p>
      </div>

      <div className="escalation-card-footer">
        <button
          type="button"
          className="escalation-continue-btn"
          onClick={onContinueChat}
        >
          <MessageSquare size={15} />
          Continue chatting with AI
        </button>
      </div>
    </div>
  );
}
