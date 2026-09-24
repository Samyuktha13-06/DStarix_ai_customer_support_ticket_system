import { Package, CreditCard, RefreshCw, Headphones, Sparkles, ArrowRight } from "lucide-react";

export default function EmptyChatHero({
  onTrackOrder,
  onCheckPayment,
  onRefundPolicy,
  onSpeakHuman,
}) {
  const actions = [
    {
      id: "track",
      title: "Track an order",
      desc: "Check shipping status & delivery date",
      icon: Package,
      action: onTrackOrder,
      color: "#256ee8",
    },
    {
      id: "payment",
      title: "Check payment",
      desc: "Verify payment records & receipts",
      icon: CreditCard,
      action: onCheckPayment,
      color: "#059669",
    },
    {
      id: "refund",
      title: "Refund policy",
      desc: "View 30-day return & refund rules",
      icon: RefreshCw,
      action: onRefundPolicy,
      color: "#7c3aed",
    },
    {
      id: "human",
      title: "Speak to human support",
      desc: "Create high-priority support ticket",
      icon: Headphones,
      action: onSpeakHuman,
      color: "#e11d48",
    },
  ];

  return (
    <div className="empty-chat-hero">
      <div className="empty-hero-icon-bubble">
        <Sparkles size={24} className="text-primary" />
      </div>

      <h2 className="empty-hero-title">How can we help?</h2>
      <p className="empty-hero-subtitle">
        Ask any question below or choose a quick action to get started immediately.
      </p>

      <div className="empty-hero-grid">
        {actions.map((act) => {
          const Icon = act.icon;
          return (
            <button
              key={act.id}
              className="empty-hero-btn"
              onClick={act.action}
              type="button"
            >
              <div
                className="empty-hero-btn-icon"
                style={{ backgroundColor: `${act.color}15`, color: act.color }}
              >
                <Icon size={18} />
              </div>
              <div className="empty-hero-btn-text">
                <span className="empty-hero-btn-title">{act.title}</span>
                <span className="empty-hero-btn-desc">{act.desc}</span>
              </div>
              <ArrowRight size={14} className="empty-hero-btn-arrow" />
            </button>
          );
        })}
      </div>
    </div>
  );
}
