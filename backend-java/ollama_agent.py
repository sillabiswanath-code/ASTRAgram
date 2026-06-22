import urllib.request
import urllib.error
import json
import base64
import sys
import re
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_TEXT_MODEL = "openhermes"
DEFAULT_VISION_MODEL = "llava"
QUIZ_MODEL = "llama3.1"

# Load Quiz Template Library
template_path = os.path.join(os.path.dirname(__file__), "QUIZ_TEMPLATE_LIBRARY.md")
try:
    with open(template_path, "r", encoding="utf-8") as f:
        QUIZ_TEMPLATES = f.read()
except Exception as e:
    print(f"Warning: Could not load QUIZ_TEMPLATE_LIBRARY.md: {e}", file=sys.stderr)
    QUIZ_TEMPLATES = ""

# Load Question Confusion Framework
confusion_path = os.path.join(os.path.dirname(__file__), "Question_Confusion_Framework.md")
try:
    with open(confusion_path, "r", encoding="utf-8") as f:
        CONFUSION_FRAMEWORK = f.read()
except Exception as e:
    print(f"Warning: Could not load Question_Confusion_Framework.md: {e}", file=sys.stderr)
    CONFUSION_FRAMEWORK = ""

# ═══════════════════════════════════════════════════════════════════════════════
# 10-STAGE EDUCATIONAL ASSESSMENT ENGINE — SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
QUIZ_SYSTEM_PROMPT = """You are an Educational Assessment Engine.

Your primary objective is to generate high-quality quizzes from educational content while ensuring every question tests deep understanding rather than memorization.

STAGE 1: CONTENT UNDERSTANDING
Extract: Main topic, Subtopics, Definitions, Examples, Explanations, Analogies, Cause-effect relationships, Hidden assumptions, Practical applications.
Create a Concept Map of all concepts. Identify explicitly and implicitly taught concepts.

STAGE 2: STRICT DOMAIN RULES
- Accuracy MUST be >99.9%. Absolutely no factual errors.
- NEVER mention "the video", "the transcript", "the speaker", or "the platform".
- Phrase all questions natively as if derived from an authoritative textbook.
- Use your own combined knowledge to make distractors incredibly confusing and highly plausible.

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

STAGE 6: TEMPLATE USAGE & CONFUSION FRAMEWORK
You MUST use the provided templates from the Universal Quiz Template Library whenever possible. If none of the templates perfectly fit a highly specialized concept, only then may you create your own format.
You MUST also follow the Question Confusion Framework rules to ensure the questions require deep thinking rather than direct recall.

=== QUIZ TEMPLATE LIBRARY ===
{QUIZ_TEMPLATES}
=============================

=== QUESTION CONFUSION FRAMEWORK ===
{CONFUSION_FRAMEWORK}
====================================

STAGE 7: QUALITY CHECK (run for every question)
Q1. Accurate? Q2. Avoids words like 'video/transcript'? Q3. Confusing distractors?
If ANY = NO → REGENERATE.

STAGE 8: FINAL APPROVAL GATE
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
difficulty must be exactly one of: easy, medium, hard (lowercase).""".replace("{QUIZ_TEMPLATES}", QUIZ_TEMPLATES).replace("{CONFUSION_FRAMEWORK}", CONFUSION_FRAMEWORK)


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
        f"TASK: Generate exactly {num_questions} quiz questions. Focus on generating quickly.\n"
        f"Difficulty distribution:\n"
        f"  - {easy_count} question(s) with difficulty: \"easy\"\n"
        f"  - {medium_count} question(s) with difficulty: \"medium\"\n"
        f"  - {hard_count} question(s) with difficulty: \"hard\"\n\n"
        f"CRITICAL RULES:\n"
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
