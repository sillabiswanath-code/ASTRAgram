import urllib.request
import urllib.error
import json
import base64
import sys
import re
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
# NOTE: qwen2.5:3b is used for all tasks
DEFAULT_TEXT_MODEL = "qwen2.5:3b-instruct"
DEFAULT_VISION_MODEL = "qwen2.5:3b-instruct"
QUIZ_MODEL = "qwen2.5:3b-instruct"

# M2 fix: use abspath so paths resolve correctly regardless of working directory
_HERE = os.path.dirname(os.path.abspath(__file__))

# Load Quiz Template Library
template_path = os.path.join(_HERE, "QUIZ_TEMPLATE_LIBRARY.md")
try:
    with open(template_path, "r", encoding="utf-8") as f:
        QUIZ_TEMPLATES = f.read()
except Exception as e:
    print(f"Warning: Could not load QUIZ_TEMPLATE_LIBRARY.md: {e}", file=sys.stderr)
    QUIZ_TEMPLATES = ""

# Load Question Confusion Framework
confusion_path = os.path.join(_HERE, "Question_Confusion_Framework.md")
try:
    with open(confusion_path, "r", encoding="utf-8") as f:
        CONFUSION_FRAMEWORK = f.read()
except Exception as e:
    print(f"Warning: Could not load Question_Confusion_Framework.md: {e}", file=sys.stderr)
    CONFUSION_FRAMEWORK = ""

# ═══════════════════════════════════════════════════════════════════════════════
# Load Master System Prompt
master_prompt_path = os.path.abspath(os.path.join(_HERE, "..", "ASTRAGRAM_MASTER_SYSTEM_PROMPT.md"))
try:
    with open(master_prompt_path, "r", encoding="utf-8") as f:
        ASTRAGRAM_MASTER_SYSTEM_PROMPT = f.read()
except Exception as e:
    print(f"Warning: Could not load ASTRAGRAM_MASTER_SYSTEM_PROMPT.md: {e}", file=sys.stderr)
    ASTRAGRAM_MASTER_SYSTEM_PROMPT = "You are an Educational Assessment Engine."

QUIZ_SYSTEM_PROMPT = ASTRAGRAM_MASTER_SYSTEM_PROMPT + "\n\n" + """
=== QUIZ TEMPLATE LIBRARY ===
{QUIZ_TEMPLATES}
=============================

=== QUESTION CONFUSION FRAMEWORK ===
{CONFUSION_FRAMEWORK}
====================================

CRITICAL OUTPUT FORMAT:
Respond ONLY with a valid JSON array. Absolutely NO markdown, NO backticks, NO explanation text, NO preamble.
Start your response with [ and end with ].

Your JSON must contain a mix of question types. The `type` must be exactly one of: `single_mcq`, `multiple_mcq`, `match_following`.

Example structure for `single_mcq` or `multiple_mcq`:
[
  {
    "type": "single_mcq",
    "question": "The question text ending with a question mark?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "EXACT text of correct option",
    "difficulty": "easy"
  },
  {
    "type": "multiple_mcq",
    "question": "Select TWO correct statements...",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": ["Option A", "Option C"],
    "difficulty": "hard"
  },
  {
    "type": "match_following",
    "question": "Match the concepts with their definitions.",
    "pairs": [
      {"left": "Concept 1", "right": "Definition 1"},
      {"left": "Concept 2", "right": "Definition 2"},
      {"left": "Concept 3", "right": "Definition 3"},
      {"left": "Concept 4", "right": "Definition 4"}
    ],
    "difficulty": "medium"
  }
]

RULES FOR OPTIONS: For MCQ types, the `options` array MUST contain exactly 4 perfectly unique items. Do NOT duplicate options.
difficulty must be exactly one of: easy, medium, hard (lowercase).""".replace("{QUIZ_TEMPLATES}", QUIZ_TEMPLATES).replace("{CONFUSION_FRAMEWORK}", CONFUSION_FRAMEWORK)


def query_ollama(prompt, model=DEFAULT_TEXT_MODEL, image_path=None, system_prompt=None, timeout=1800):
    """
    Query the local Ollama API.
    Gracefully returns an error object if Ollama is unreachable.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1,
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
    # M1 fix: raised timeout from 180s to 300s — qwen2.5:3b-instruct with 10-stage prompt can exceed 3 min on slow hardware
    res = query_ollama(prompt, model=QUIZ_MODEL, system_prompt=QUIZ_SYSTEM_PROMPT, timeout=1800)

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
    seen_questions = set()
    for q in questions:
        if not isinstance(q, dict) or "type" not in q or "question" not in q or "difficulty" not in q:
            print(f"[QuizEngine] Rejected malformed question (missing base fields): {str(q)[:200]}", file=sys.stderr)
            continue
            
        q_type = q["type"]
        is_valid = False
        
        if q_type == "single_mcq":
            if (
                "options" in q and "answer" in q
                and isinstance(q["options"], list)
                and len(q["options"]) == 4
                and len(set(q["options"])) == 4  # No duplicates
                and isinstance(q["answer"], str)
                and q["answer"] in q["options"]
            ):
                is_valid = True
        elif q_type == "multiple_mcq":
            if (
                "options" in q and "answer" in q
                and isinstance(q["options"], list)
                and len(q["options"]) == 4
                and len(set(q["options"])) == 4  # No duplicates
                and isinstance(q["answer"], list)
                and all(a in q["options"] for a in q["answer"])
            ):
                is_valid = True
        elif q_type == "match_following":
            if (
                "pairs" in q
                and isinstance(q["pairs"], list)
                and all(isinstance(p, dict) and "left" in p and "right" in p for p in q["pairs"])
            ):
                is_valid = True
                
        if is_valid and q["difficulty"] in ("easy", "medium", "hard"):
            # Duplicate detector
            q_norm = re.sub(r'[^a-zA-Z0-9]', '', q["question"].lower())
            if q_norm not in seen_questions:
                seen_questions.add(q_norm)
                valid.append(q)
            else:
                print(f"[QuizEngine] Rejected duplicate question: {q['question'][:50]}", file=sys.stderr)
        else:
            print(f"[QuizEngine] Rejected malformed or duplicate-option question: {str(q)[:200]}", file=sys.stderr)

    print(f"[QuizEngine] {len(valid)}/{len(questions)} passed structural and duplicate validation.", file=sys.stderr)

    # Fast batch AI Validation (Target < 2 sec)
    if valid:
        val_prompt = "Evaluate these questions for clarity, logical distractors, and one correct answer. Return a JSON array of the indices of VALID questions (e.g., [0, 1, 2]). Only return the JSON array.\n\n"
        for idx, vq in enumerate(valid):
            val_prompt += f"[{idx}] Q: {vq['question']} | Opts: {vq.get('options', [])} | Ans: {vq.get('answer', '')}\n"
        
        val_res = query_ollama(val_prompt, model=QUIZ_MODEL, system_prompt="You are a strict QA validator. Output ONLY a valid JSON array of integers representing the valid indices.")
        if "error" not in val_res:
            try:
                raw_val = val_res["response"].strip()
                raw_val = re.sub(r'```json\s*', '', raw_val)
                raw_val = re.sub(r'```\s*', '', raw_val)
                valid_indices = json.loads(raw_val)
                if isinstance(valid_indices, list):
                    filtered = [valid[i] for i in valid_indices if 0 <= i < len(valid)]
                    print(f"[QuizEngine] AI Validator approved {len(filtered)}/{len(valid)} questions.", file=sys.stderr)
                    valid = filtered
            except Exception as e:
                print(f"[QuizEngine] Validation parsing error: {e}, passing all structurally valid.", file=sys.stderr)

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
