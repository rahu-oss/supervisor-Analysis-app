# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import re
from prompts import build_analysis_prompt, get_kpi_names, get_assessment_dimensions

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
    sentiment: str
    pattern: str

class RubricScore(BaseModel):
    score: int
    justification: str

class AnalysisResponse(BaseModel):
    extracted_evidence: list[Evidence]
    rubric_score: RubricScore
    kpi_mapping: list[str]
    gap_analysis: list[str]
    followup_questions: list[str]

# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_llm_response(raw: str) -> dict:
    """Strip markdown fences and parse JSON. Raises ValueError if parsing fails."""
    # Remove ```json ... ``` or ``` ... ``` fences
    clean = re.sub(r"```(?:json)?", "", raw).strip()
    # Find first { and last } to extract JSON object
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
                    "temperature": 0.2,
                    "num_predict": 2048,
                    "num_ctx": 2048
                }
            },
            timeout=300
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

@app.get("/context")
def get_context():
    """Returns KPI names and assessment dimensions for the frontend."""
    return {
        "kpis": get_kpi_names(),
        "dimensions": get_assessment_dimensions()
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

    # Build prompt using prompts.py and call Ollama
    prompt = build_analysis_prompt(request.transcript)
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
