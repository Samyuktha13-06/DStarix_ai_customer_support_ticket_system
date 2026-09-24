import { useState } from "react";
import { Search, X, Package, CreditCard, ArrowRight, Loader2, CheckCircle2 } from "lucide-react";

const SAMPLE_ORDERS = [45821, 45822, 45823];

export default function OrderLookupModal({ isOpen, onClose, onSelectOrder, apiBaseUrl }) {
  const [orderIdInput, setOrderIdInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [orderResult, setOrderResult] = useState(null);
  const [paymentResult, setPaymentResult] = useState(null);

  if (!isOpen) return null;

  const handleLookup = async (idToLookUp) => {
    const targetId = (idToLookUp || orderIdInput).toString().trim().replace(/\D/g, "");
    if (!targetId) {
      setError("Please enter a valid numeric Order ID.");
      return;
    }

    setLoading(true);
    setError("");
    setOrderResult(null);
    setPaymentResult(null);

    try {
      // 1. Fetch Order
      const orderRes = await fetch(`${apiBaseUrl}/orders/${targetId}`);
      if (!orderRes.ok) {
        if (orderRes.status === 404) {
          throw new Error(`Order #${targetId} was not found in the system.`);
        }
        throw new Error("Unable to look up order. Server error.");
      }
      const orderData = await orderRes.json();
      setOrderResult(orderData);

      // 2. Fetch Payment
      try {
        const paymentRes = await fetch(`${apiBaseUrl}/payments/${targetId}`);
        if (paymentRes.ok) {
          const paymentData = await paymentRes.json();
          setPaymentResult(paymentData);
        }
      } catch {
        // Payment lookup is secondary
      }
    } catch (err) {
      setError(err.message || "Failed to look up order.");
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (orderResult) {
      onSelectOrder(orderResult, paymentResult);
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <div className="modal-icon blue">
              <Search size={18} />
            </div>
            <div>
              <h3>Order Lookup</h3>
              <span>Search and view any NovaCart order</span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleLookup();
            }}
            className="lookup-form"
          >
            <div className="lookup-input-wrapper">
              <Search size={16} className="search-input-icon" />
              <input
                type="text"
                placeholder="Enter Order ID (e.g. 45821)"
                value={orderIdInput}
                onChange={(e) => {
                  setOrderIdInput(e.target.value);
                  setError("");
                }}
                autoFocus
              />
              <button
                type="submit"
                className="lookup-btn"
                disabled={loading || !orderIdInput.trim()}
              >
                {loading ? <Loader2 size={16} className="spin" /> : "Search"}
              </button>
            </div>
          </form>

          {/* Quick suggestions */}
          <div className="sample-orders">
            <span>Quick Sample Orders:</span>
            <div className="sample-badges">
              {SAMPLE_ORDERS.map((id) => (
                <button
                  key={id}
                  type="button"
                  className="sample-badge"
                  onClick={() => {
                    setOrderIdInput(id.toString());
                    handleLookup(id);
                  }}
                >
                  #{id}
                </button>
              ))}
            </div>
          </div>

          {error && <div className="modal-error-alert">{error}</div>}

          {orderResult && (
            <div className="order-preview-card">
              <div className="preview-header">
                <div className="preview-badge-row">
                  <span className="order-num">Order #{orderResult.order_id}</span>
                  <span className={`status-badge ${orderResult.status?.toLowerCase() || "open"}`}>
                    {orderResult.status}
                  </span>
                </div>
                <h4>{orderResult.product}</h4>
              </div>

              <div className="preview-grid">
                <div className="preview-item">
                  <span>Customer ID</span>
                  <strong>#{orderResult.customer_id}</strong>
                </div>
                <div className="preview-item">
                  <span>Amount</span>
                  <strong>₹{orderResult.amount?.toLocaleString("en-IN")}</strong>
                </div>
                <div className="preview-item">
                  <span>Tracking Number</span>
                  <strong>{orderResult.tracking_number || "Pending"}</strong>
                </div>
                <div className="preview-item">
                  <span>Expected Delivery</span>
                  <strong>{orderResult.expected_delivery_date || "Not specified"}</strong>
                </div>
              </div>

              {paymentResult && (
                <div className="preview-payment-section">
                  <div className="preview-payment-title">
                    <CreditCard size={15} />
                    <span>Payment #{paymentResult.payment_id}</span>
                    <span className={`status-badge ${paymentResult.status?.toLowerCase() || "open"}`}>
                      {paymentResult.status}
                    </span>
                  </div>
                </div>
              )}

              <button className="apply-order-btn" onClick={handleApply}>
                <CheckCircle2 size={16} />
                Set as Active Order & Update Panel
                <ArrowRight size={15} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
