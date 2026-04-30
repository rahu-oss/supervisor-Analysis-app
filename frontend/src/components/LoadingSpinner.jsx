export default function LoadingSpinner() {
  return (
    <div style={{ textAlign: "center", padding: "60px 0" }}>
      <div style={{
        width: "42px",
        height: "42px",
        margin: "0 auto 18px",
        border: "3px solid var(--border)",
        borderTop: "3px solid var(--accent)",
        borderRadius: "50%",
        animation: "spin 0.85s linear infinite",
      }} />
      <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
        Sending to Ollama…
      </p>
      <p style={{ color: "#444", fontSize: "0.8rem", marginTop: "5px" }}>
        This can take 20–60 seconds
      </p>
    </div>
  );
}