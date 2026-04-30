# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import re

app = FastAPI(title="Supervisor Transcript Analyzer")

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# ── Request / Response Models ─────────────────────────────────────────────────

class TranscriptRequest(BaseModel):
    transcript: str

class Evidence(BaseModel):
    quote: str
    sentiment: str   # "positive" | "negative" | "neutral"
    pattern: str     # what behavioral pattern this reveals

class RubricScore(BaseModel):
    score: int       # 1–10
    justification: str

class AnalysisResponse(BaseModel):
    extracted_evidence: list[Evidence]
    rubric_score: RubricScore
    kpi_mapping: list[str]
    gap_analysis: list[str]
    followup_questions: list[str]

# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert analyst evaluating supervisor transcripts for a fellowship program.

Your job is to analyze a supervisor's description of a Fellow (intern) and return a structured JSON analysis.

The 8 business KPIs you must map against are:
1. Revenue Growth - Did the Fellow contribute to increasing revenue?
2. Customer Acquisition - Did the Fellow help bring in new customers?
3. Customer Retention - Did the Fellow improve customer loyalty or reduce churn?
4. Operational Efficiency - Did the Fellow streamline processes or reduce waste?
5. Team Productivity - Did the Fellow improve team output or morale?
6. Product/Service Quality - Did the Fellow improve quality of deliverables?
7. Market Expansion - Did the Fellow help enter new markets or segments?
8. Systems Building - Did the Fellow build scalable systems, processes, or documentation?

The assessment dimensions are:
- Technical competency
- Communication skills
- Initiative and ownership
- Team collaboration
- Problem-solving ability
- Systems thinking
- Leadership impact
- Stakeholder management

You MUST respond with ONLY a valid JSON object. No explanation, no markdown, no extra text.

JSON format:
{
  "extracted_evidence": [
    {
      "quote": "<exact or near-exact quote from transcript>",
      "sentiment": "positive" | "negative" | "neutral",
      "pattern": "<behavioral pattern this reveals>"
    }
  ],
  "rubric_score": {
    "score": <integer 1-10>,
    "justification": "<one paragraph citing specific evidence from the transcript>"
  },
  "kpi_mapping": [
    "<KPI name> - <one sentence explaining how the Fellow's work connects to this KPI>"
  ],
  "gap_analysis": [
    "<assessment dimension not covered> - <what information is missing>"
  ],
  "followup_questions": [
    "<specific question targeting a gap identified above>"
  ]
}

Rules:
- extracted_evidence: pull 3–6 direct quotes or close paraphrases. Tag each as positive/negative/neutral.
- rubric_score: score must be 1–10 integer. Justification must cite specific evidence.
- kpi_mapping: only include KPIs that are clearly supported by the transcript. Do not guess.
- gap_analysis: list every assessment dimension the transcript did NOT address.
- followup_questions: 3–5 questions, each targeting a specific gap from gap_analysis.
- If the transcript is too short or vague to analyze, still return the JSON but note it in the justification.
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def build_prompt(transcript: str) -> str:
    return f"{SYSTEM_PROMPT}\n\nSupervisor Transcript:\n\"\"\"\n{transcript.strip()}\n\"\"\"\n\nRespond ONLY with the JSON object:"

def parse_llm_response(raw: str) -> dict:
    """Strip markdown fences and parse JSON. Raises ValueError if parsing fails."""
    # Remove ```json ... ``` or ``` ... ``` fences
    clean = re.sub(r"```(?:json)?", "", raw).strip()
    # Remove any leading/trailing non-JSON text (find first { and last })
    start = clean.find("{")
    end = clean.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in LLM response")
    json_str = clean[start:end]
    return json.loads(json_str)

def call_ollama(prompt: str) -> str:
    """Send prompt to Ollama and return raw text response."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,   # Low temp = more consistent/structured output
                    "num_predict": 2048,  # Enough tokens for full analysis
                }
            },
            timeout=120  # LLMs can be slow locally
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Make sure it's running: 'ollama serve'"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Ollama took too long to respond. Try a smaller model or shorter transcript."
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama returned an error: {str(e)}")

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "Supervisor Transcript Analyzer API is running"}

@app.get("/health")
def health_check():
    """Check if Ollama is reachable."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in response.json().get("models", [])]
        return {
            "status": "ok",
            "ollama": "connected",
            "available_models": models
        }
    except Exception:
        return {
            "status": "degraded",
            "ollama": "unreachable",
            "available_models": []
        }

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_transcript(request: TranscriptRequest):
    """Main endpoint: takes transcript, returns structured analysis."""

    # Basic validation
    if not request.transcript or len(request.transcript.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Transcript is too short. Please paste the full supervisor transcript."
        )

    # Build prompt and call Ollama
    prompt = build_prompt(request.transcript)
    raw_response = call_ollama(prompt)

    # Parse the LLM's JSON response
    try:
        parsed = parse_llm_response(raw_response)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=422,
            detail=f"LLM returned malformed output. Try running again. Details: {str(e)}"
        )

    # Validate required keys exist
    required_keys = ["extracted_evidence", "rubric_score", "kpi_mapping", "gap_analysis", "followup_questions"]
    missing = [k for k in required_keys if k not in parsed]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"LLM response missing required fields: {missing}. Try running again."
        )

    return parsed