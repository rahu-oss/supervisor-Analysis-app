# backend/prompts.py

# ── KPI Definitions ───────────────────────────────────────────────────────────

KPI_DEFINITIONS = {
    "Revenue Growth": "Fellow contributed to increasing revenue through sales, pricing, or monetization work.",
    "Customer Acquisition": "Fellow helped bring in new customers, leads, or users.",
    "Customer Retention": "Fellow improved customer loyalty, satisfaction, or reduced churn.",
    "Operational Efficiency": "Fellow streamlined processes, reduced waste, or automated tasks.",
    "Team Productivity": "Fellow improved team output, morale, workflows, or collaboration.",
    "Product/Service Quality": "Fellow improved the quality, reliability, or performance of a product or service.",
    "Market Expansion": "Fellow helped the organization enter new markets, geographies, or customer segments.",
    "Systems Building": "Fellow built scalable systems, documented processes, or created reusable infrastructure.",
}

# ── Assessment Dimensions ─────────────────────────────────────────────────────

ASSESSMENT_DIMENSIONS = [
    "Technical competency",
    "Communication skills",
    "Initiative and ownership",
    "Team collaboration",
    "Problem-solving ability",
    "Systems thinking",
    "Leadership impact",
    "Stakeholder management",
]

# ── Rubric Reference ──────────────────────────────────────────────────────────

RUBRIC_REFERENCE = """
Scoring Rubric (1–10):
1–2:  Fellow caused harm, created more work, or was disengaged entirely.
3–4:  Fellow completed tasks but showed little initiative, needed constant supervision.
5–6:  Fellow met expectations, completed assigned work, occasionally showed initiative.
7–8:  Fellow exceeded expectations, drove outcomes independently, added clear value.
9–10: Fellow performed at a full-time employee level, created lasting impact.
"""

# ── Few-Shot Examples ─────────────────────────────────────────────────────────

FEW_SHOT_EXAMPLE = """
EXAMPLE INPUT:
"She was always on time, completed every task we gave her, and even built a tracker 
that the whole team now uses. She sometimes struggled to speak up in meetings with 
senior stakeholders but was excellent one-on-one."

EXAMPLE OUTPUT:
{
  "extracted_evidence": [
    {
      "quote": "always on time, completed every task we gave her",
      "sentiment": "positive",
      "pattern": "Reliability and consistent task completion"
    },
    {
      "quote": "built a tracker that the whole team now uses",
      "sentiment": "positive",
      "pattern": "Initiative and systems building beyond assigned scope"
    },
    {
      "quote": "sometimes struggled to speak up in meetings with senior stakeholders",
      "sentiment": "negative",
      "pattern": "Gap in stakeholder communication confidence"
    },
    {
      "quote": "excellent one-on-one",
      "sentiment": "positive",
      "pattern": "Strong interpersonal communication in smaller settings"
    }
  ],
  "rubric_score": {
    "score": 7,
    "justification": "The Fellow demonstrated strong reliability and exceeded expectations by proactively building a team-wide tracker, showing initiative and systems thinking. The score is capped at 7 rather than higher due to a noted gap in senior stakeholder communication, which is an important leadership skill. Overall, she added clear, measurable value to the team."
  },
  "kpi_mapping": [
    "Operational Efficiency - Built a tracker now used by the whole team, directly improving team workflows.",
    "Systems Building - Created a reusable tool adopted across the team, demonstrating scalable thinking."
  ],
  "gap_analysis": [
    "Technical competency - No mention of the Fellow's technical skills or tools used.",
    "Problem-solving ability - No specific examples of how the Fellow handled challenges or blockers.",
    "Leadership impact - No information about whether the Fellow mentored others or led any initiatives.",
    "Revenue Growth - No mention of any revenue-related contributions."
  ],
  "followup_questions": [
    "Can you describe a specific challenge the Fellow faced and how they resolved it?",
    "Did the Fellow work with any technical tools or systems? How proficient were they?",
    "Did the Fellow take the lead on any project or mentor anyone on the team?",
    "How did the Fellow handle feedback — did you notice them improving over time?"
  ]
}
"""

# ── Main Prompt Builder ───────────────────────────────────────────────────────

def build_analysis_prompt(transcript: str) -> str:
    kpi_list = "\n".join(
        f"- {name}: {definition}"
        for name, definition in KPI_DEFINITIONS.items()
    )

    dimensions_list = "\n".join(f"- {d}" for d in ASSESSMENT_DIMENSIONS)

    prompt = f"""You are an expert program evaluator analyzing supervisor transcripts for a fellowship program.
Your task is to evaluate how a Fellow (intern) performed based on their supervisor's description.

════════════════════════════════════════
CONTEXT: THE 8 BUSINESS KPIs
════════════════════════════════════════
{kpi_list}

════════════════════════════════════════
CONTEXT: THE 8 ASSESSMENT DIMENSIONS
════════════════════════════════════════
{dimensions_list}

════════════════════════════════════════
CONTEXT: SCORING RUBRIC
════════════════════════════════════════
{RUBRIC_REFERENCE}

════════════════════════════════════════
EXAMPLE (study this carefully)
════════════════════════════════════════
{FEW_SHOT_EXAMPLE}

════════════════════════════════════════
YOUR TASK
════════════════════════════════════════
Analyze the supervisor transcript below and return a JSON object with EXACTLY these 5 keys:

1. "extracted_evidence" — array of objects, each with:
   - "quote": exact or near-exact words from the transcript
   - "sentiment": MUST be one of: "positive", "negative", "neutral"
   - "pattern": the behavioral pattern this quote reveals (1 sentence)
   Extract 3–6 pieces of evidence. Only use what is actually in the transcript.

2. "rubric_score" — object with:
   - "score": integer from 1 to 10 (use the rubric above)
   - "justification": one paragraph explaining the score, citing specific evidence

3. "kpi_mapping" — array of strings.
   Format each as: "KPI Name - one sentence explaining connection to the Fellow's work"
   ONLY include KPIs clearly supported by the transcript. Do not guess or infer.

4. "gap_analysis" — array of strings.
   List every assessment dimension the transcript did NOT address.
   Format each as: "Dimension name - what specific information is missing"
   Be thorough — if a dimension wasn't mentioned, list it.

5. "followup_questions" — array of 3–5 strings.
   Each question must target a specific gap from gap_analysis.
   Make them concrete and actionable, not generic.

════════════════════════════════════════
STRICT RULES
════════════════════════════════════════
- Respond ONLY with valid JSON. No explanation, no markdown fences, no extra text.
- Do NOT wrap output in ```json or ``` blocks.
- Do NOT add any text before or after the JSON object.
- Start your response with {{ and end with }}
- If the transcript is very short or vague, still return all 5 keys but note limitations in the justification.
- Never invent quotes. Only use words that appear in the transcript.

════════════════════════════════════════
SUPERVISOR TRANSCRIPT
════════════════════════════════════════
{transcript.strip()}

════════════════════════════════════════
YOUR JSON RESPONSE (start with {{):
════════════════════════════════════════"""

    return prompt


# ── Utility: Get dimension and KPI lists (used by frontend health checks) ──────

def get_kpi_names() -> list:
    return list(KPI_DEFINITIONS.keys())

def get_assessment_dimensions() -> list:
    return ASSESSMENT_DIMENSIONS