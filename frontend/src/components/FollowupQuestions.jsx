export default function FollowupQuestions({ questions }) {
  return (
    <div className="card">
      <div className="card-header">
        <span>💬</span>
        <h2>Suggested Follow-up Questions</h2>
        <span className="badge">{questions.length} questions</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {questions.map((q, i) => (
          <div key={i} style={{
            background: "#0e1818",
            border: "1px solid #1a3030",
            borderRadius: "8px",
            padding: "14px 18px",
            display: "flex",
            gap: "16px",
            alignItems: "flex-start",
          }}>
            <span style={{
              fontFamily: "'Playfair Display', serif",
              color: "var(--neu)",
              fontSize: "1rem",
              flexShrink: 0,
              marginTop: "2px",
            }}>
              Q{i + 1}
            </span>
            <p style={{ color: "var(--text)", fontSize: "0.9rem", lineHeight: "1.65" }}>
              {q}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}