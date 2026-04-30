import { useState } from "react";
import "./App.css";
import TranscriptInput   from "./components/TranscriptInput";
import LoadingSpinner    from "./components/LoadingSpinner";
import EvidenceCard      from "./components/EvidenceCard";
import RubricScore       from "./components/RubricScore";
import KPIMapping        from "./components/KPIMapping";
import GapAnalysis       from "./components/GapAnalysis";
import FollowupQuestions from "./components/FollowupQuestions";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
  const [error,   setError]   = useState(null);

  const handleAnalyze = async (transcript) => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res  = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Something went wrong.");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Transcript Analyzer</h1>
        <p>Paste a supervisor transcript to extract evidence, score, KPIs, gaps, and follow-up questions.</p>
      </header>

      <TranscriptInput onAnalyze={handleAnalyze} loading={loading} />

      {loading && <LoadingSpinner />}

      {error && <div className="error-box">⚠️ {error}</div>}

      {result && (
        <div className="results">
          <EvidenceCard      evidence={result.extracted_evidence} />
          <RubricScore       rubricScore={result.rubric_score} />
          <KPIMapping        kpiMapping={result.kpi_mapping} />
          <GapAnalysis       gapAnalysis={result.gap_analysis} />
          <FollowupQuestions questions={result.followup_questions} />
        </div>
      )}
    </div>
  );
}
