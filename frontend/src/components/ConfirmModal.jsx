import { AlertTriangle, X } from "lucide-react";

export default function ConfirmModal({ isOpen, onClose, onConfirm, title, message, confirmText = "Confirm" }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card modal-confirm" onClick={(e) => e.stopPropagation()}>
        <div className="confirm-icon-box">
          <AlertTriangle size={24} />
        </div>

        <h3>{title || "Confirm Action"}</h3>
        <p>{message || "Are you sure you want to proceed?"}</p>

        <div className="confirm-actions">
          <button className="confirm-cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button
            className="confirm-danger-btn"
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
