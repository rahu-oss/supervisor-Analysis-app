export default function RubricScore({ rubricScore }) {
  const { score, justification } = rubricScore;
  const color = score >= 8 ? "var(--pos)" : score >= 5 ? "var(--accent)" : "var(--neg)";
  const label = score >= 8 ? "Exceeds Expectations"
              : score >= 5 ? "Meets Expectations"
              : "Below Expectations";

  return (
    <div className="card">
      <div className="card-header">
        <span>⭐</span>
        <h2>Rubric Score</h2>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "22px", marginBottom: "20px" }}>
        {/* Circle */}
        <div style={{
          width: "76px", height: "76px", flexShrink: 0,
          borderRadius: "50%",
          border: `3px solid ${color}`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <span style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: "2rem",
            color,
          }}>
            {score}
          </span>
        </div>

        {/* Bar */}
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "7px" }}>
            <span style={{ color: "var(--muted)", fontSize: "0.8rem" }}>out of 10</span>
            <span style={{ color, fontSize: "0.82rem", fontWeight: "600" }}>{label}</span>
          </div>
          <div style={{ background: "var(--border)", borderRadius: "4px", height: "7px" }}>
            <div style={{
              width: `${score * 10}%`,
              height: "100%",
              background: color,
              borderRadius: "4px",
              transition: "width 1s ease",
            }} />
          </div>
        </div>
      </div>

      {/* Justification */}
      <p style={{
        color: "#bbb",
        fontSize: "0.9rem",
        lineHeight: "1.75",
        borderTop: "1px solid var(--border)",
        paddingTop: "16px",
      }}>
        {justification}
      </p>
    </div>
  );
}