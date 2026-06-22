import urllib.request
import urllib.error
import json
import base64
import sys
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_TEXT_MODEL = "openhermes"
DEFAULT_VISION_MODEL = "llava"
QUIZ_MODEL = "llama3.2"

# ═══════════════════════════════════════════════════════════════════════════════
# 10-STAGE EDUCATIONAL ASSESSMENT ENGINE — SYSTEM PROMPT
# Saved as reference: backend-java/quiz_engine_prompt.txt
# ═══════════════════════════════════════════════════════════════════════════════
QUIZ_SYSTEM_PROMPT = """You are an Educational Assessment Engine.

Your primary objective is to generate high-quality quizzes from educational content while ensuring every question tests deep understanding rather than memorization.

STAGE 1: CONTENT UNDERSTANDING
Extract: Main topic, Subtopics, Definitions, Examples, Explanations, Analogies, Cause-effect relationships, Hidden assumptions, Practical applications.
Create a Concept Map of all concepts. Identify explicitly and implicitly taught concepts.

STAGE 2: KNOWLEDGE BOUNDARY RULE
ALLOWED: Concepts directly taught, concepts logically implied, supporting domain knowledge for deeper reasoning.
NOT ALLOWED: Unrelated concepts, external topics, questions outside learning objectives.
RULE: Every question must trace back to a concept in the transcript. If traceability fails: REJECT.

STAGE 3: QUESTION DESIGN RULES
AVOID: "What is X?", "Define Y.", "Who invented Z?", "Which statement was mentioned?"
REQUIRED: Application-based, Scenario-based, Indirect reasoning, Concept transfer, Cause-effect, Misconception detection, Concept comparison, Real-world interpretation.

STAGE 4: CONFUSION ENGINE
Each question MUST:
- Require genuine thinking and reasoning.
- Prevent lucky guessing.
- Include highly plausible distractors.
- Avoid obvious process of elimination.
- Make the correct answer non-obvious at first glance.

Difficulty distribution (STRICTLY follow the requested counts):
- EASY: Surface-level application — student still needs to think, not just recall
- MEDIUM: Requires connecting two or more concepts from the transcript
- HARD: Requires deep inference, misconception navigation, or multi-step reasoning

STAGE 5: OPTION GENERATION RULES
Every wrong option MUST:
- Be believable and conceptually related
- Represent a real common misconception
- Use similar wording/structure as the correct answer
- Be plausible enough that a student who partially understood would pick it

NEVER use: silly answers, joke answers, obviously wrong answers, answers of very different lengths.

Good distractor types: partial truth, reversed causality, misapplied concept, common misconception, correct concept in wrong context.

STAGE 6: KNOWLEDGE AUGMENTATION
Use own knowledge ONLY to strengthen reasoning. Core concept must remain identical to transcript.
RULE: Transcript = Ground Truth. Model knowledge = Enhancement only.

STAGE 7: QUALITY CHECK (run for every question)
Q1. Based on transcript concepts? Q2. Requires reasoning? Q3. Indirect? Q4. All options plausible?
Q5. Correct answer uniquely correct? Q6. Avoids memorization? Q7. Memorizer would struggle?
If ANY = NO → REGENERATE.

STAGE 8: ANSWER VALIDATION (run for every question)
Step 1: Solve as a student. Step 2: Try alternative interpretations. Step 3: Check multiple correct answers.
Step 4: Check ambiguity. Step 5: Check conceptual accuracy.
If multiple correct / ambiguous / mismatch → REJECT AND REGENERATE.

STAGE 9: VALIDATION SCORING
Score each question 0-100:
- Concept Alignment ≥ 95, Difficulty ≥ 80, Indirectness ≥ 80
- Distractor Quality ≥ 85, Answer Uniqueness = 100, Educational Value ≥ 85, Overall ≥ 90
Regenerate only failed questions. Repeat until ALL pass.

STAGE 10: FINAL APPROVAL GATE
Checklist before output:
✓ Every question maps to episode concept ✓ No unrelated knowledge ✓ Questions are indirect
✓ Require reasoning ✓ Distractors are confusing but fair ✓ No ambiguity ✓ No duplicates
✓ No memorization-only questions ✓ All validation scores passed
If all pass → OUTPUT. Else → RETURN TO STAGE 3.

NON-NEGOTIABLE: Never output immediately. Always run: Generate → Validate → Score → Audit → Regenerate failures → Revalidate → Final Approval → Output.

CRITICAL OUTPUT FORMAT:
Respond ONLY with a valid JSON array. Absolutely NO markdown, NO backticks, NO explanation text, NO preamble.
Start your response with [ and end with ].
Every element MUST match exactly:
[
  {
    "question": "The question text ending with a question mark?",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "answer": "EXACT text of correct option — must match one of the 4 options character-for-character",
    "difficulty": "easy"
  }
]
difficulty must be exactly one of: easy, medium, hard (lowercase)."""


def query_ollama(prompt, model=DEFAULT_TEXT_MODEL, image_path=None, system_prompt=None, timeout=60):
    """
    Query the local Ollama API.
    Gracefully returns an error object if Ollama is unreachable.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.4
        }
    }

    if system_prompt:
        payload["system"] = system_prompt

    if image_path:
        try:
            with open(image_path, "rb") as img_file:
                b64_img = base64.b64encode(img_file.read()).decode('utf-8')
                payload["images"] = [b64_img]
        except Exception as e:
            print(f"Error reading image {image_path}: {e}", file=sys.stderr)
            return {"error": f"Failed to read image: {e}"}

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode('utf-8'))
            return {"response": result.get("response", "").strip()}
    except urllib.error.URLError as e:
        print(f"Ollama connection error: {e}", file=sys.stderr)
        return {"error": "Ollama service unavailable or model not found."}
    except Exception as e:
        print(f"Ollama unknown error: {e}", file=sys.stderr)
        return {"error": str(e)}


def evaluate_and_rewrite_summary(transcript, original_summary):
    """
    Uses the agent to evaluate the summary.
    If relevance < 90%, it rewrites the summary.
    """
    sys_prompt = (
        "You are a strict evaluation agent. Your job is to compare a video transcript against its summary. "
        "If the summary's relevance/accuracy is above 90%, respond exactly with 'APPROVED'. "
        "If the relevance is lower, provide a few suggestions for improvement, and then provide a completely rewritten, highly accurate summary."
    )

    prompt = f"TRANSCRIPT:\n{transcript}\n\nSUMMARY TO EVALUATE:\n{original_summary}\n\nEVALUATION:"

    res = query_ollama(prompt, model=DEFAULT_TEXT_MODEL, system_prompt=sys_prompt)
    if "error" in res:
        return {"approved": True, "summary": original_summary, "fallback": True}

    text = res["response"]
    if "APPROVED" in text[:20]:
        return {"approved": True, "summary": original_summary, "fallback": False}
    else:
        return {"approved": False, "summary": text, "fallback": False}


def generate_full_episode_quiz(transcript, episode_id, num_questions=10):
    """
    Generate a full quiz bank for one episode using the 10-stage Educational Assessment Engine.

    Difficulty distribution:
        Easy   → 10% of total  (conceptual application)
        Medium → 20% of total  (connecting concepts)
        Hard   → 70% of total  (deep inference / misconception navigation)

    Powered entirely by Ollama llama3.2. No fallback generation here — processor.py
    handles structural validation and fallback only.

    Returns: list of dicts [{question, options, answer, difficulty}] or None on failure.
    """
    easy_count   = max(1, round(num_questions * 0.10))
    medium_count = max(1, round(num_questions * 0.20))
    hard_count   = num_questions - easy_count - medium_count  # ≈ 70%

    prompt = (
        f"Episode {episode_id} — Educational Content Transcript:\n"
        f"{transcript[:6000]}\n\n"
        f"TASK: Generate exactly {num_questions} quiz questions with the following STRICT difficulty distribution:\n"
        f"  - {easy_count} question(s) with difficulty: \"easy\"\n"
        f"  - {medium_count} question(s) with difficulty: \"medium\"\n"
        f"  - {hard_count} question(s) with difficulty: \"hard\"\n\n"
        f"Apply ALL 10 stages of the Educational Assessment Engine to every question.\n"
        f"Run the complete validation pipeline (Stages 7-10) before outputting.\n\n"
        f"CRITICAL SPEED RULES:\n"
        f"1. DO NOT print any intermediate steps, reasoning, or evaluations.\n"
        f"2. DO NOT output any preamble or conversational text.\n"
        f"3. Directly output the FINAL JSON array immediately.\n\n"
        f"Output ONLY the JSON array. Nothing else."
    )

    print(f"[QuizEngine] Generating {num_questions} questions for Episode {episode_id} via Ollama ({QUIZ_MODEL})...", file=sys.stderr)
    res = query_ollama(prompt, model=QUIZ_MODEL, system_prompt=QUIZ_SYSTEM_PROMPT, timeout=180)

    if "error" in res:
        print(f"[QuizEngine] Ollama error: {res['error']}", file=sys.stderr)
        return None

    raw = res["response"].strip()

    # Strip markdown code fences if present
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)
    raw = raw.strip()

    # Extract outermost JSON array
    try:
        start = raw.index('[')
        end   = raw.rindex(']') + 1
        questions = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as e:
        print(f"[QuizEngine] JSON parse error: {e}\nRaw (first 500): {raw[:500]}", file=sys.stderr)
        return None

    # Structural validation — processor.py is the authority on correctness
    valid = []
    for q in questions:
        if (
            isinstance(q, dict)
            and "question" in q
            and "options"  in q
            and "answer"   in q
            and "difficulty" in q
            and isinstance(q["options"], list)
            and len(q["options"]) == 4
            and q["answer"] in q["options"]
            and q["difficulty"] in ("easy", "medium", "hard")
        ):
            valid.append(q)
        else:
            print(f"[QuizEngine] Rejected malformed question: {str(q)[:200]}", file=sys.stderr)

    print(f"[QuizEngine] {len(valid)}/{len(questions)} questions passed structural validation.", file=sys.stderr)
    return valid if valid else None


def validate_quiz_with_vision(quiz_json, screenshot_path):
    """
    Uses a vision model to evaluate if the quiz question and answer
    have a 96%+ accurate match/relevance to the visual context.
    NOTE: This is kept for optional use. Quiz generation is Ollama-only.
    """
    sys_prompt = (
        "You are a strict QA agent. Look at the provided screenshot from a video. "
        "Evaluate the provided quiz question and answer. Do they accurately reflect the context shown in the image? "
        "If the accuracy/relevance is >= 95%, respond exactly with 'VALID'. "
        "Otherwise, respond with 'INVALID' followed by a brief reason."
    )

    quiz_str = json.dumps(quiz_json, indent=2)
    prompt = f"QUIZ:\n{quiz_str}\n\nEVALUATION:"

    res = query_ollama(prompt, model=DEFAULT_VISION_MODEL, image_path=screenshot_path, system_prompt=sys_prompt)

    if "error" in res:
        return {"valid": True, "reason": "Ollama vision unavailable - assumed valid", "fallback": True}

    text = res["response"]
    if "VALID" in text[:15].upper():
        return {"valid": True, "reason": text, "fallback": False}
    else:
        return {"valid": False, "reason": text, "fallback": False}
