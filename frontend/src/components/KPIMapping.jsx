export default function KPIMapping({ kpiMapping }) {
  if (!kpiMapping?.length) return (
    <div className="card">
      <div className="card-header">
        <span>📊</span><h2>KPI Mapping</h2>
      </div>
      <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
        No KPIs clearly matched in this transcript.
      </p>
    </div>
  );

  return (
    <div className="card">
      <div className="card-header">
        <span>📊</span>
        <h2>KPI Mapping</h2>
        <span className="badge">{kpiMapping.length} of 8 matched</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {kpiMapping.map((item, i) => {
          const dash = item.indexOf(" - ");
          const name = dash !== -1 ? item.slice(0, dash) : item;
          const desc = dash !== -1 ? item.slice(dash + 3) : "";
          return (
            <div key={i} style={{
              background: "#181808",
              border: "1px solid #303010",
              borderRadius: "8px",
              padding: "13px 18px",
              display: "flex",
              gap: "14px",
              alignItems: "flex-start",
            }}>
              <span style={{
                color: "var(--accent)",
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: "0.75rem",
                fontWeight: "600",
                marginTop: "3px",
                flexShrink: 0,
              }}>
                {String(i + 1).padStart(2, "0")}
              </span>
              <div>
                <p style={{ color: "var(--accent)", fontWeight: "600", fontSize: "0.88rem", marginBottom: "3px" }}>
                  {name}
                </p>
                {desc && (
                  <p style={{ color: "#888", fontSize: "0.83rem", lineHeight: "1.5" }}>
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