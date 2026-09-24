import { useEffect, useState } from "react";
import { Ticket, X, RotateCcw, Search, Clock, AlertCircle, CheckCircle2 } from "lucide-react";

export default function TicketsModal({ isOpen, onClose, onSelectTicket, apiBaseUrl, currentTicket }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchId, setSearchId] = useState("");

  const fetchTickets = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${apiBaseUrl}/tickets`);
      if (!res.ok) throw new Error("Unable to retrieve tickets.");
      const data = await res.json();
      setTickets(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load support tickets.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchTickets();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const filteredTickets = searchId.trim()
    ? tickets.filter(
        (t) =>
          t.ticket_id.toString().includes(searchId.trim()) ||
          t.subject?.toLowerCase().includes(searchId.toLowerCase())
      )
    : tickets;

  const formatDate = (isoStr) => {
    if (!isoStr) return "Recent";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card modal-wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <div className="modal-icon orange">
              <Ticket size={18} />
            </div>
            <div>
              <h3>Support Tickets</h3>
              <span>View, manage, and track your escalated support tickets</span>
            </div>
          </div>
          <div className="modal-header-actions">
            <button
              className="refresh-icon-btn"
              onClick={fetchTickets}
              disabled={loading}
              title="Refresh tickets"
            >
              <RotateCcw size={16} className={loading ? "spin" : ""} />
            </button>
            <button className="modal-close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="modal-body">
          {/* Search bar inside modal */}
          <div className="ticket-search-bar">
            <Search size={15} />
            <input
              type="text"
              placeholder="Filter by Ticket ID or Subject..."
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
            />
            {searchId && (
              <button className="clear-search-btn" onClick={() => setSearchId("")}>
                <X size={14} />
              </button>
            )}
          </div>

          {error && <div className="modal-error-alert">{error}</div>}

          {loading ? (
            <div className="modal-loading-state">
              <RotateCcw size={24} className="spin text-blue" />
              <span>Loading support tickets...</span>
            </div>
          ) : filteredTickets.length === 0 ? (
            <div className="empty-tickets">
              <AlertCircle size={32} />
              <strong>No tickets found</strong>
              <p>
                {searchId
                  ? `No ticket matching "${searchId}".`
                  : "No support tickets have been created yet. You can ask NovaCart AI to escalate any issue to human support."}
              </p>
            </div>
          ) : (
            <div className="tickets-list">
              {filteredTickets.map((t) => {
                const isCurrent = currentTicket && currentTicket.ticket_id === t.ticket_id;
                return (
                  <div
                    key={t.ticket_id}
                    className={`ticket-item ${isCurrent ? "current-ticket-active" : ""}`}
                  >
                    <div className="ticket-item-header">
                      <div className="ticket-id-tag">
                        <Ticket size={14} />
                        <span>Ticket #{t.ticket_id}</span>
                      </div>
                      <div className="ticket-badges">
                        <span className={`priority-badge ${t.priority?.toLowerCase() || "normal"}`}>
                          {t.priority || "normal"}
                        </span>
                        <span className={`status-badge ${t.status?.toLowerCase() || "open"}`}>
                          {t.status}
                        </span>
                      </div>
                    </div>

                    <h4 className="ticket-subject">{t.subject || "Customer Support Inquiry"}</h4>
                    <p className="ticket-desc">{t.description}</p>

                    <div className="ticket-meta-footer">
                      <div className="ticket-meta-info">
                        {t.order_id && (
                          <span className="order-tag">Order #{t.order_id}</span>
                        )}
                        <span className="ticket-date">
                          <Clock size={12} />
                          {formatDate(t.created_at)}
                        </span>
                      </div>

                      <button
                        className="select-ticket-btn"
                        onClick={() => {
                          onSelectTicket(t);
                          onClose();
                        }}
                      >
                        {isCurrent ? (
                          <>
                            <CheckCircle2 size={14} />
                            Active in Panel
                          </>
                        ) : (
                          "View in Panel"
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
