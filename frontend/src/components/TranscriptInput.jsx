import { useState } from "react";

export default function TranscriptInput({ onAnalyze, loading }) {
  const [text, setText] = useState("");

  const handleSubmit = () => {
    if (text.trim().length < 50) {
      alert("Transcript too short — please paste more text.");
      return;
    }
    onAnalyze(text);
  };

  return (
    <div className="card">
      <div className="card-header">
        <span>📋</span>
        <h2>Supervisor Transcript</h2>
      </div>

      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        disabled={loading}
        placeholder="Paste the full supervisor transcript here..."
        style={{
          width: "100%",
          minHeight: "200px",
          background: "#0f0f0f",
          border: "1px solid var(--border)",
          borderRadius: "8px",
          color: "var(--text)",
          fontFamily: "'Source Sans 3', sans-serif",
          fontSize: "0.92rem",
          lineHeight: "1.7",
          padding: "16px",
          resize: "vertical",
          outline: "none",
          transition: "border-color 0.2s",
        }}
        onFocus={e => (e.target.style.borderColor = "var(--accent)")}
        onBlur={e  => (e.target.style.borderColor = "var(--border)")}
      />

      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginTop: "14px",
      }}>
        <span style={{
          color: "var(--muted)",
          fontSize: "0.8rem",
          fontFamily: "'JetBrains Mono', monospace",
        }}>
          {text.length} chars
        </span>

        <button
          onClick={handleSubmit}
          disabled={loading || text.trim().length < 50}
          style={{
            background: loading ? "#2a2a2a" : "var(--accent)",
            color: loading ? "var(--muted)" : "#0c0c0c",
            border: "none",
            borderRadius: "8px",
            padding: "11px 26px",
            fontFamily: "'Source Sans 3', sans-serif",
            fontWeight: "600",
            fontSize: "0.95rem",
            cursor: loading ? "not-allowed" : "pointer",
            transition: "all 0.2s",
          }}
        >
          {loading ? "Analyzing…" : "Run Analysis →"}
        </button>
      </div>
    </div>
  );
}