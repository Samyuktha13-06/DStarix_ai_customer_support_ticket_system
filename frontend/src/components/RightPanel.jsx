import {
  Package,
  CreditCard,
  Ticket,
  User,
  Search,
  X,
  ShieldCheck,
  Clock,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

export default function RightPanel({
  activeOrder,
  activePayment,
  activeTicket,
  customerInfo,
  onClearOrder,
  onClearTicket,
  onOpenOrderLookup,
  isMobileOpen,
  onCloseMobile,
}) {
  const hasContext = !!(activeOrder || activePayment || activeTicket || customerInfo);

  return (
    <>
      {isMobileOpen && (
        <div className="mobile-sidebar-backdrop" onClick={onCloseMobile} />
      )}

      <aside className={`support-right-panel ${isMobileOpen ? "mobile-open" : ""}`}>
        {/* Panel Header */}
        <div className="panel-header-top">
          <div className="panel-header-title-wrap">
            <Package size={18} className="text-primary" />
            <h3 className="panel-main-title">Active Details</h3>
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

        <div className="panel-scroll-content">
          {!hasContext ? (
            <div className="panel-empty-context">
              <div className="empty-panel-icon-wrap">
                <Package size={32} className="text-muted" />
              </div>
              <h4 className="empty-panel-title">No Active Order or Ticket</h4>
              <p className="empty-panel-desc">
                Order tracking, payment information, customer details, and support tickets will display here automatically when inquired in chat.
              </p>
              {onOpenOrderLookup && (
                <button
                  type="button"
                  className="empty-panel-lookup-btn"
                  onClick={onOpenOrderLookup}
                >
                  <Search size={14} />
                  <span>Look up Order Details</span>
                </button>
              )}
            </div>
          ) : (
            <div className="panel-context-section">
              {/* Customer Info Card */}
              {customerInfo && (
                <div className="detail-card customer-card">
                  <div className="card-header">
                    <div className="card-header-left">
                      <User size={15} className="text-primary" />
                      <span className="card-title">Customer Profile</span>
                    </div>
                  </div>
                  <div className="card-body">
                    <div className="detail-row">
                      <span className="detail-label">Name:</span>
                      <span className="detail-value font-medium">{customerInfo.name}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Email:</span>
                      <span className="detail-value">{customerInfo.email}</span>
                    </div>
                    {customerInfo.id && (
                      <div className="detail-row">
                        <span className="detail-label">Customer ID:</span>
                        <span className="detail-value">#{customerInfo.id}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Order Card */}
              {activeOrder && (
                <div className="detail-card order-card">
                  <div className="card-header">
                    <div className="card-header-left">
                      <Package size={15} className="text-primary" />
                      <span className="card-title">Order #{activeOrder.order_id || activeOrder.id}</span>
                    </div>
                    {onClearOrder && (
                      <button
                        type="button"
                        className="card-close-btn"
                        onClick={onClearOrder}
                        title="Dismiss order"
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>

                  <div className="card-body">
                    <div className="detail-row">
                      <span className="detail-label">Product:</span>
                      <span className="detail-value font-medium">{activeOrder.product}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Amount:</span>
                      <span className="detail-value font-semibold">
                        ${typeof activeOrder.amount === "number" ? activeOrder.amount.toFixed(2) : activeOrder.amount}
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Status:</span>
                      <span className={`status-pill status-${(activeOrder.status || "").toLowerCase().replace(/\s+/g, "-")}`}>
                        {activeOrder.status}
                      </span>
                    </div>
                    {activeOrder.tracking_number && (
                      <div className="detail-row">
                        <span className="detail-label">Tracking:</span>
                        <span className="detail-value tracking-code">
                          {activeOrder.tracking_number}
                        </span>
                      </div>
                    )}
                    {activeOrder.expected_delivery_date && (
                      <div className="detail-row">
                        <span className="detail-label">Expected:</span>
                        <span className="detail-value">
                          {new Date(activeOrder.expected_delivery_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Payment Card */}
              {activePayment && (
                <div className="detail-card payment-card">
                  <div className="card-header">
                    <div className="card-header-left">
                      <CreditCard size={15} className="text-emerald-600" />
                      <span className="card-title">Payment Information</span>
                    </div>
                  </div>
                  <div className="card-body">
                    <div className="detail-row">
                      <span className="detail-label">Order Ref:</span>
                      <span className="detail-value">#{activePayment.order_id}</span>
                    </div>
                    {activePayment.amount !== undefined && (
                      <div className="detail-row">
                        <span className="detail-label">Total Paid:</span>
                        <span className="detail-value font-semibold text-emerald-600">
                          ${typeof activePayment.amount === "number" ? activePayment.amount.toFixed(2) : activePayment.amount}
                        </span>
                      </div>
                    )}
                    <div className="detail-row">
                      <span className="detail-label">Payment Status:</span>
                      <span className={`status-pill status-${(activePayment.status || "").toLowerCase()}`}>
                        {activePayment.status}
                      </span>
                    </div>
                    {activePayment.payment_date && (
                      <div className="detail-row">
                        <span className="detail-label">Date:</span>
                        <span className="detail-value">
                          {new Date(activePayment.payment_date).toLocaleString([], {
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Ticket Card */}
              {activeTicket && (
                <div className="detail-card ticket-card">
                  <div className="card-header">
                    <div className="card-header-left">
                      <Ticket size={15} className="text-amber-500" />
                      <span className="card-title">Support Ticket #{activeTicket.ticket_id || activeTicket.id}</span>
                    </div>
                    {onClearTicket && (
                      <button
                        type="button"
                        className="card-close-btn"
                        onClick={onClearTicket}
                        title="Dismiss ticket"
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>
                  <div className="card-body">
                    <div className="detail-row">
                      <span className="detail-label">Priority:</span>
                      <span className={`priority-badge priority-${(activeTicket.priority || "high").toLowerCase()}`}>
                        {activeTicket.priority || "High"}
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Status:</span>
                      <span className="status-pill status-open">
                        {activeTicket.status || "Open"}
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Notice:</span>
                      <span className="detail-value text-muted text-xs">
                        A support representative is assigned.
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
