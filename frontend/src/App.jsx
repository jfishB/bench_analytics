import { useState } from "react";

// Use frontend env if set; fallback to 127.0.0.1:8000
const API_BASE =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE) ||
  `http://${window.location.hostname}:8000`;

export default function App() {
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  async function checkDb() {
    try {
      setError("");
      setStatus("checking…");
      const res = await fetch(`${API_BASE}/api/health/db/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setStatus(data.db === "ok" ? "Connected ✅" : "Unknown ❓");
    } catch (e) {
      setStatus("");
      setError(e.message || "Request failed");
    }
  }

  return (
    <div style={{ fontFamily: "system-ui", padding: 20, maxWidth: 640 }}>
      <h1>BenchAnalytics</h1>
      <p style={{ color: "#555" }}>
        Click the button to verify the frontend → backend → Postgres path.
      </p>
      <button onClick={checkDb}>Check DB</button>
      {status && <span style={{ marginLeft: 10 }}>{status}</span>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
    </div>
  );
}