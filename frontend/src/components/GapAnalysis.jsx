export default function GapAnalysis({ gapAnalysis }) {
  return (
    <div className="card">
      <div className="card-header">
        <span>⚠️</span>
        <h2>Gap Analysis</h2>
        <span className="badge">{gapAnalysis.length} gaps</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {gapAnalysis.map((item, i) => {
          const dash = item.indexOf(" - ");
          const dim  = dash !== -1 ? item.slice(0, dash) : item;
          const desc = dash !== -1 ? item.slice(dash + 3) : "";
          return (
            <div key={i} style={{
              background: "#181210",
              border: "1px solid #302010",
              borderRadius: "8px",
              padding: "12px 18px",
              display: "flex",
              gap: "12px",
              alignItems: "flex-start",
            }}>
              <span style={{ color: "var(--warn)", marginTop: "2px", flexShrink: 0 }}>◆</span>
              <div>
                <p style={{ color: "var(--warn)", fontWeight: "600", fontSize: "0.87rem", marginBottom: "3px" }}>
                  {dim}
                </p>
                {desc && (
                  <p style={{ color: "#888", fontSize: "0.82rem", lineHeight: "1.5" }}>
                    {desc}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}