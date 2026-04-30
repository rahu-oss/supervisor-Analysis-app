# Supervisor Transcript Analyzer

A web app that analyzes supervisor transcripts using a local LLM (Ollama) to extract
behavioral evidence, score Fellows on a rubric, map KPIs, identify gaps, and suggest
follow-up questions.

---

## Setup Instructions

### 1. Install Ollama

Download and install from [ollama.com](https://ollama.com).

Then pull the model:

```bash
ollama pull llama3.2
```

Start Ollama (runs as a background service after install):

```bash
ollama serve
```

Verify it works:

```bash
ollama run llama3.2 "say hello"
```

---

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

---

### 3. Set Up the Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

- **Mac/Linux:**

```bash
source venv/bin/activate
```

- **Windows:**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend server:

```bash
uvicorn main:app --reload
```

Backend will run at `http://localhost:8000`.
Verify it's working: open `http://localhost:8000/health` in your browser.

---

### 4. Set Up the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm start
```

Frontend will open automatically at `http://localhost:3000`.

---

### 5. Run the App

1. Make sure Ollama is running (`ollama serve`)
2. Make sure backend is running (`uvicorn main:app --reload`)
3. Make sure frontend is running (`npm start`)
4. Open `http://localhost:3000`
5. Paste a supervisor transcript and click **Run Analysis**

---

## Model Used

**Model:** `llama3.2` (3B parameters)

**Why I chose it:**
- Small enough to run on most laptops (requires ~4GB RAM)
- Strong instruction-following — reliably returns structured JSON output
- Fast enough for local use (20–60 seconds per analysis)
- No API key or internet connection required after download

I chose llama3.2 over larger models like llama3.1 (8B) because the analysis task
requires structured output and careful instruction following — not creative generation.
A smaller, more precise model outperforms a larger, slower one for this use case.

---

## Architecture Overview

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│                     │  POST   │                     │  POST   │                     │
│   React Frontend    │────────▶│   FastAPI Backend   │────────▶│   Ollama (local)    │
│   localhost:3000    │◀────────│   localhost:8000    │◀────────│   localhost:11434   │
│                     │  JSON   │                     │  JSON   │                     │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
```

- **Frontend (React):** Single-page app with a transcript textarea and 5 result
  components (Evidence, Score, KPIs, Gaps, Follow-up Questions). Talks to the backend
  via `fetch()`.

- **Backend (FastAPI + Python):** Receives the transcript, builds a structured prompt
  using KPI definitions and rubric context from `prompts.py`, sends it to Ollama,
  parses the JSON response, validates it with Pydantic, and returns it to the frontend.

- **Ollama:** Runs the `llama3.2` LLM entirely locally. No data leaves your machine.
  The backend calls it via HTTP POST to `http://localhost:11434/api/generate`.

---

## Design Challenges

### Challenge 1: Getting Consistent Structured JSON from the LLM

**Problem:** LLMs don't naturally return clean JSON. They add explanations, markdown
fences, preambles like "Sure! Here's the analysis:", and sometimes hallucinate extra
fields or skip required ones.

**Approach:**
- Injected the full KPI definitions and scoring rubric directly into the prompt so
  the model scores against real criteria, not its own assumptions.
- Added a one-shot example showing exact input → exact JSON output, which reduced
  malformed responses significantly.
- Instructed the model explicitly: "Start your response with `{` and end with `}`"
  which forces JSON-first output.
- Built a `parse_llm_response()` function that strips markdown fences with regex,
  then finds the first `{` and last `}` to extract valid JSON even from messy output.
- Set `temperature: 0.2` to minimize randomness and maximize output consistency.

---

### Challenge 2: Identifying Gaps from Absence of Information

**Problem:** Detecting what the transcript did not mention is harder than extracting
what it did. A standard extraction prompt will only surface what is present, not what
is missing.

**Approach:**
- Explicitly listed all 8 assessment dimensions in the prompt and instructed the model
  to check each one individually against the transcript.
- Framed the instruction as: "List every assessment dimension the transcript did NOT
  address" — forcing the model to treat absence as a signal, not a non-event.
- Required a specific format: "Dimension name - what specific information is missing"
  so gaps are actionable, not vague.
- Linked the gap analysis directly to follow-up questions, so each question must
  target a named gap — creating a closed loop between what is missing and what to ask.

---

## What I'd Improve With More Time

1. **Side-by-side transcript and analysis view** — currently the transcript disappears
   after analysis. A split-panel layout would let the psychology intern refer back to
   the original text while reading the evidence cards.

2. **Retry logic for malformed LLM output** — if the model returns invalid JSON, the
   app currently shows an error. I would add automatic retry up to 3 times with a
   slightly modified prompt before surfacing the error to the user.

3. **Export to PDF** — interns need to share analysis reports with supervisors. A
   one-click PDF export of the full analysis would make this production-ready.

4. **Transcript history** — save past analyses in localStorage so the intern can
   compare how a Fellow's feedback has changed across multiple calls.

5. **Confidence indicators per evidence quote** — let the model rate how strongly
   each quote supports the identified pattern (high/medium/low), so interns can
   prioritize which evidence to discuss in follow-up calls.

6. **Model selector in the UI** — let the user pick which Ollama model to use from
   a dropdown, pulling available models from the `/health` endpoint. Useful for
   teams with different hardware capabilities.

---

## Project Structure

```
supervisor-transcript-analyzer/
├── backend/
│   ├── main.py          # FastAPI app, routes, Ollama integration
│   ├── prompts.py       # Prompt engineering, KPI definitions, rubric
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TranscriptInput.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── EvidenceCard.jsx
│   │   │   ├── RubricScore.jsx
│   │   │   ├── KPIMapping.jsx
│   │   │   ├── GapAnalysis.jsx
│   │   │   └── FollowupQuestions.jsx
│   │   ├── App.js
│   │   └── App.css
│   └── package.json
└── README.md
```

---

## Sample Transcript (for testing)

Paste this into the app to test it:

```
The Fellow has been an outstanding addition to our team. She independently
redesigned our customer onboarding process, reducing drop-off by 30%. She
communicates clearly in meetings and writes detailed documentation. However,
I have not seen her take initiative in team discussions or push back when she
disagrees. She works well with her direct teammates but has not interacted much
with senior stakeholders. Overall she delivers high quality work consistently
and on time.
```

---

## Tech Stack

| Layer     | Technology               |
|-----------|--------------------------|
| Frontend  | React (Create React App) |
| Backend   | Python, FastAPI, Uvicorn |
| LLM       | Ollama (llama3.2)        |
| Styling   | CSS Variables, Google Fonts |
