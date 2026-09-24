import { useState, useEffect } from "react";
import { Activity, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { API_BASE_URL } from "../config";

export default function BackendHealthIndicator() {
  const [health, setHealth] = useState({
    status: "checking",
    version: null,
    db: null,
    latency: null,
    lastChecked: null,
  });
  const [showTooltip, setShowTooltip] = useState(false);

  const checkHealth = async () => {
    const start = performance.now();
    try {
      const res = await fetch(`${API_BASE_URL}/health`, {
        cache: "no-store",
        headers: { "Cache-Control": "no-cache" },
      });
      const end = performance.now();
      const latency = Math.round(end - start);

      if (res.ok) {
        const data = await res.json();
        setHealth({
          status: data.status === "healthy" ? "online" : "degraded",
          version: data.version || "0.1.0",
          db: data.database || "connected",
          latency,
          lastChecked: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        });
      } else {
        setHealth({
          status: "offline",
          version: null,
          db: "unknown",
          latency: null,
          lastChecked: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        });
      }
    } catch {
      setHealth({
        status: "offline",
        version: null,
        db: "unavailable",
        latency: null,
        lastChecked: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      });
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const isOnline = health.status === "online";
  const isChecking = health.status === "checking";

  return (
    <div
      className="health-indicator-container"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className={`health-pill ${health.status}`}>
        <span className={`status-dot ${health.status}`} />
        <span className="health-label">
          {isChecking ? "Connecting..." : isOnline ? "Backend Connected" : "Backend Offline"}
        </span>
        {isOnline && health.version && (
          <span className="health-version-tag">v{health.version}</span>
        )}
      </div>

      {showTooltip && (
        <div className="health-tooltip">
          <div className="health-tooltip-row">
            <strong>API Status:</strong>
            <span className={isOnline ? "text-success" : "text-danger"}>
              {health.status.toUpperCase()}
            </span>
          </div>
          <div className="health-tooltip-row">
            <strong>Endpoint:</strong>
            <span>{API_BASE_URL}</span>
          </div>
          <div className="health-tooltip-row">
            <strong>Database:</strong>
            <span>{health.db || "N/A"}</span>
          </div>
          {health.latency !== null && (
            <div className="health-tooltip-row">
              <strong>Latency:</strong>
              <span>{health.latency} ms</span>
            </div>
          )}
          <div className="health-tooltip-row">
            <strong>Checked:</strong>
            <span>{health.lastChecked || "Just now"}</span>
          </div>
        </div>
      )}
    </div>
  );
}
