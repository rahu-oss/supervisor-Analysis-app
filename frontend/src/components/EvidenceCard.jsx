const SENT = {
  positive: { color: "var(--pos)", bg: "#0c1f14", label: "Positive" },
  negative: { color: "var(--neg)", bg: "#1f0c0c", label: "Negative" },
  neutral:  { color: "var(--neu)", bg: "#0c1420", label: "Neutral"  },
};

export default function EvidenceCard({ evidence }) {
  return (
    <div className="card">
      <div className="card-header">
        <span>🔍</span>
        <h2>Extracted Evidence</h2>
        <span className="badge">{evidence.length} quotes</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {evidence.map((item, i) => {
          const cfg = SENT[item.sentiment] || SENT.neutral;
          return (
            <div key={i} style={{
              background: cfg.bg,
              border: `1px solid ${cfg.color}30`,
              borderLeft: `3px solid ${cfg.color}`,
              borderRadius: "8px",
              padding: "14px 18px",
            }}>
              <span style={{
                display: "inline-block",
                background: cfg.color + "20",
                color: cfg.color,
                fontSize: "0.7rem",
                fontWeight: "600",
                fontFamily: "'JetBrains Mono', monospace",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                padding: "2px 10px",
                borderRadius: "20px",
                marginBottom: "10px",
              }}>
                {cfg.label}
              </span>

              <p style={{
                fontStyle: "italic",
                color: "var(--text)",
                fontSize: "0.91rem",
                lineHeight: "1.6",
                marginBottom: "8px",
              }}>
                "{item.quote}"
              </p>

              <p style={{
                color: "var(--muted)",
                fontSize: "0.81rem",
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                ↳ {item.pattern}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}