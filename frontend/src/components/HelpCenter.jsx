import { Package, CreditCard, RefreshCw, UserCheck, ChevronRight } from "lucide-react";

export default function HelpCenter({ onSelectTopic, onOpenOrderLookup }) {
  const categories = [
    {
      id: "orders",
      title: "Orders",
      description: "Track orders, delivery and shipping",
      icon: Package,
      action: () => onOpenOrderLookup ? onOpenOrderLookup() : onSelectTopic("Track an order"),
      prompt: "Can you help me track my order and check shipping delivery status?",
      badge: "Lookup",
    },
    {
      id: "payments",
      title: "Payments",
      description: "Payment status, failed payments and refunds",
      icon: CreditCard,
      action: () => onSelectTopic("How can I check the payment status or refund for an order?"),
      prompt: "How can I check payment status, resolve failed payments, or get a refund?",
      badge: "Billing",
    },
    {
      id: "returns",
      title: "Returns & Refunds",
      description: "Refund eligibility and return policy",
      icon: RefreshCw,
      action: () => onSelectTopic("What is NovaCart's refund eligibility and return policy?"),
      prompt: "What is NovaCart's refund eligibility and return policy?",
      badge: "Policy",
    },
    {
      id: "account",
      title: "Account",
      description: "Account and profile support",
      icon: UserCheck,
      action: () => onSelectTopic("How can I update my account information or reset my password?"),
      prompt: "How can I update my account details or profile settings?",
      badge: "Support",
    },
  ];

  return (
    <div className="help-center-container">
      <div className="help-center-header">
        <h4 className="help-center-title">Help Center</h4>
        <p className="help-center-subtitle">How can we help?</p>
      </div>

      <div className="help-center-grid">
        {categories.map((cat) => {
          const Icon = cat.icon;
          return (
            <button
              key={cat.id}
              className="help-center-card"
              onClick={cat.action}
              type="button"
            >
              <div className="help-card-icon-wrap">
                <Icon size={18} className="help-card-icon" />
              </div>
              <div className="help-card-body">
                <div className="help-card-title-row">
                  <span className="help-card-title">{cat.title}</span>
                  <ChevronRight size={14} className="help-card-arrow" />
                </div>
                <p className="help-card-desc">{cat.description}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
