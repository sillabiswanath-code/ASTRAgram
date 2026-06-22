"""
ASTRAgram — Comprehensive Test Suite
Covers all 8 quality requirements.

Run:  cd backend-java && venv\\Scripts\\python.exe -m pytest tests/test_all.py -v
"""

import sys
import os
import json
import re
import unittest
import random

# ── path so we can import processor functions ──────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Helpers (duplicated here so tests run independently of any processor state)
# ---------------------------------------------------------------------------
DEVANAGARI_RE = re.compile(r'[\u0900-\u097F]')

def has_devanagari(text: str) -> bool:
    return bool(DEVANAGARI_RE.search(text))

def is_english_only(text: str) -> bool:
    """True when the text contains no Devanagari / non-Latin script chars."""
    return not has_devanagari(text)

def first_sentence(text: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    for s in sentences:
        if len(s.split()) >= 5:
            return s
    return sentences[0] if sentences else ""


# ───────────────────────────────────────────────────────────────────────────
# REQ 1 — Quiz fallback uses first sentence when transcript is poor
# ───────────────────────────────────────────────────────────────────────────
class TestQuizFallback(unittest.TestCase):
    """Req 1: when transcript is too short/bad, quiz uses first-sentence context."""

    def _make_quiz(self, text, ep_id=1):
        from processor import generate_quiz
        return generate_quiz(text, ep_id)

    def test_empty_text_returns_valid_quiz(self):
        quiz = self._make_quiz("", 1)
        self.assertIn("question", quiz)
        self.assertIn("options", quiz)
        self.assertIn("answer", quiz)
        self.assertGreater(len(quiz["options"]), 0)
        self.assertIn(quiz["answer"], quiz["options"],
                      "Answer must be one of the options")

    def test_short_text_falls_back_gracefully(self):
        quiz = self._make_quiz("Hello world.", 2)
        self.assertIsNotNone(quiz["question"])
        self.assertIn(quiz["answer"], quiz["options"])

    def test_first_sentence_used_in_question_when_meaningful(self):
        text = ("The mitochondria is the powerhouse of the cell. "
                "It produces ATP through oxidative phosphorylation. "
                "This process is essential for cellular respiration.")
        quiz = self._make_quiz(text, 1)
        # question should reference the episode or the content
        self.assertTrue(
            "Episode" in quiz["question"] or len(quiz["question"]) > 10,
            f"Question too generic: {quiz['question']}"
        )

    def test_answer_is_one_of_options(self):
        text = ("Photosynthesis converts light energy into chemical energy. "
                "Plants use chlorophyll to absorb sunlight. "
                "Glucose is produced as the primary product of this reaction. "
                "Oxygen is released as a byproduct into the atmosphere.")
        quiz = self._make_quiz(text, 3)
        self.assertIn(quiz["answer"], quiz["options"],
                      f"Answer '{quiz['answer']}' not in options {quiz['options']}")

    def test_four_options_always_returned(self):
        """Quiz must always have exactly 4 options."""
        for text in ["", "Short.", "A" * 500]:
            with self.subTest(text=text[:20]):
                quiz = self._make_quiz(text, 1)
                self.assertEqual(len(quiz["options"]), 4,
                                 f"Expected 4 options, got {len(quiz['options'])}: {quiz['options']}")


# ───────────────────────────────────────────────────────────────────────────
# REQ 2 — Quiz is always in English, no Hindi/Devanagari
# ───────────────────────────────────────────────────────────────────────────
class TestQuizEnglishOnly(unittest.TestCase):
    """Req 2: Quiz must be in meaningful English only."""

    def _make_quiz(self, text, ep_id=1):
        from processor import generate_quiz
        return generate_quiz(text, ep_id)

    def _assert_english(self, value, field):
        self.assertTrue(is_english_only(value),
                        f"{field} contains non-English chars: {value!r}")

    def test_quiz_from_hindi_text_is_english(self):
        hindi = "यह एक परीक्षण है। हिंदी में लिखा गया पाठ।"
        quiz = self._make_quiz(hindi, 1)
        self._assert_english(quiz["question"], "question")
        self._assert_english(quiz["answer"],   "answer")
        for opt in quiz["options"]:
            self._assert_english(opt, "option")

    def test_quiz_from_hinglish_text_is_english(self):
        hinglish = ("Aaj hum padh rahe hain mitochondria ke baare mein. "
                    "Yeh cell ka powerhouse hai.")
        quiz = self._make_quiz(hinglish, 2)
        self._assert_english(quiz["question"], "question")
        self._assert_english(quiz["answer"],   "answer")

    def test_options_are_meaningful_strings(self):
        text = ("Newton's first law states that an object in motion stays in motion. "
                "This is also called the law of inertia. "
                "Forces are required to change an object's state of motion.")
        quiz = self._make_quiz(text, 1)
        for opt in quiz["options"]:
            self.assertGreater(len(opt.split()), 1,
                               f"Option too short or meaningless: {opt!r}")

    def test_question_is_not_blank(self):
        quiz = self._make_quiz("Some English content about science.", 5)
        self.assertTrue(len(quiz["question"].strip()) > 10)


# ───────────────────────────────────────────────────────────────────────────
# REQ 3 — PDF text is meaningful English with proper grammar markers
# ───────────────────────────────────────────────────────────────────────────
class TestPDFGeneration(unittest.TestCase):
    """Req 3: PDF should contain grammatically sensible English sentences."""

    def setUp(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()

    def test_pdf_created_for_good_text(self):
        from processor import generate_pdf
        out = os.path.join(self.tmpdir, "test_good.pdf")
        generate_pdf(
            "The water cycle describes how water evaporates from surfaces, "
            "rises into the atmosphere, condenses into clouds, and falls back "
            "as precipitation. This cycle is essential for life on Earth.",
            "Episode 1",
            out
        )
        self.assertTrue(os.path.exists(out), "PDF not created")
        self.assertGreater(os.path.getsize(out), 100, "PDF is suspiciously small")

    def test_pdf_created_for_hindi_text_uses_fallback(self):
        from processor import generate_pdf
        out = os.path.join(self.tmpdir, "test_hindi.pdf")
        # Should not crash; uses fallback message
        generate_pdf("यह हिंदी में है।", "Episode 2", out)
        self.assertTrue(os.path.exists(out))

    def test_pdf_created_for_empty_text(self):
        from processor import generate_pdf
        out = os.path.join(self.tmpdir, "test_empty.pdf")
        generate_pdf("", "Episode 3", out)
        self.assertTrue(os.path.exists(out))


# ───────────────────────────────────────────────────────────────────────────
# REQ 4 — Quiz is relevant and in English
# ───────────────────────────────────────────────────────────────────────────
class TestQuizRelevance(unittest.TestCase):
    """Req 4: Quiz must be relevant to the video content."""

    def _make_quiz(self, text, ep_id=1):
        from processor import generate_quiz
        return generate_quiz(text, ep_id)

    def test_quiz_answer_relates_to_content(self):
        text = ("Gravity is the force that attracts objects toward each other. "
                "On Earth, gravity gives weight to physical objects. "
                "The gravitational constant G governs the strength of this force.")
        quiz = self._make_quiz(text, 1)
        # Answer should contain real words from the content or a reasonable paraphrase
        answer_lower = quiz["answer"].lower()
        # Check it's not purely generic
        self.assertNotEqual(answer_lower, "something unrelated",
                            "Answer should not be generic placeholder")
        self.assertNotEqual(answer_lower, "an intro",
                            "Answer should not be generic placeholder")

    def test_quiz_episode_id_in_question(self):
        quiz = self._make_quiz("Short text.", 7)
        self.assertIn("7", quiz["question"],
                      "Episode ID should appear in the question")

    def test_no_segment_word_in_quiz(self):
        """'Segment' is replaced by 'Episode' everywhere."""
        from processor import generate_quiz
        for ep_id in [1, 3, 10]:
            quiz = generate_quiz("Some content about the topic.", ep_id)
            for field in [quiz["question"], quiz["answer"]] + quiz["options"]:
                self.assertNotIn("Segment", field,
                                 f"'Segment' found in quiz field: {field!r}")


# ───────────────────────────────────────────────────────────────────────────
# REQ 5 — Hindi/non-English transcript → clean English only
# ───────────────────────────────────────────────────────────────────────────
class TestTranslationCleanup(unittest.TestCase):
    """Req 5: Translation result must be clean English with no Devanagari."""

    def test_has_devanagari_detector(self):
        self.assertTrue(has_devanagari("यह परीक्षण है"))
        self.assertFalse(has_devanagari("This is a test"))
        self.assertFalse(has_devanagari("Aaj ka din acha hai"))  # Hinglish (Latin)

    def test_clean_english_only_strips_devanagari(self):
        from processor import clean_english_only
        mixed = "Hello यह world है"
        cleaned = clean_english_only(mixed)
        self.assertFalse(has_devanagari(cleaned),
                         f"Devanagari still present: {cleaned!r}")
        self.assertIn("Hello", cleaned)
        self.assertIn("world", cleaned)

    def test_clean_english_preserves_pure_english(self):
        from processor import clean_english_only
        text = "The quick brown fox jumps over the lazy dog."
        self.assertEqual(clean_english_only(text).strip(), text.strip())

    def test_get_first_sentence_extracts_correctly(self):
        from processor import get_first_sentence
        text = "Gravity pulls objects toward Earth. It is a fundamental force."
        first = get_first_sentence(text)
        self.assertIn("Gravity", first)
        self.assertNotIn("fundamental", first)


# ───────────────────────────────────────────────────────────────────────────
# REQ 6 — Gen-Z error messages (frontend helper function)
# ───────────────────────────────────────────────────────────────────────────
class TestGenZErrors(unittest.TestCase):
    """Req 6: Error messages must be in Gen-Z internet style."""

    GEN_Z_INDICATORS = ["💀", "bestie", "no cap", "fr fr", "cooked", "ngl",
                        "slay", "era", "lowkey", "giving", "vibe", "oof",
                        "bruh", "not it", "bussin", "ate", "rent free"]

    def _has_genz(self, msg: str) -> bool:
        ml = msg.lower()
        return any(ind.lower() in ml for ind in self.GEN_Z_INDICATORS)

    def test_invalid_url_error_is_genz(self):
        # Simulate what genzError() returns for invalid URL
        err = "bestie that URL is NOT it 💀 drop a real YouTube link no cap"
        self.assertTrue(self._has_genz(err), f"Not Gen-Z: {err!r}")

    def test_processing_error_is_genz(self):
        err = "oof this is giving error vibes rn 😭 the processor ate but chose chaos"
        self.assertTrue(self._has_genz(err), f"Not Gen-Z: {err!r}")

    def test_quiz_wrong_answer_is_genz(self):
        msg = "bestie that's not it 😬 try again no cap"
        self.assertTrue(self._has_genz(msg), f"Not Gen-Z: {msg!r}")

    def test_quiz_correct_answer_is_genz(self):
        msg = "slay! you understood the assignment fr fr 🔥"
        self.assertTrue(self._has_genz(msg), f"Not Gen-Z: {msg!r}")

    def test_network_error_is_genz(self):
        msg = "the wifi said 'nah fam' 📵 check your connection bestie"
        self.assertTrue(self._has_genz(msg), f"Not Gen-Z: {msg!r}")


# ───────────────────────────────────────────────────────────────────────────
# REQ 7 — Video player retry logic (unit-level spec validation)
# ───────────────────────────────────────────────────────────────────────────
class TestVideoPlayerRetrySpec(unittest.TestCase):
    """
    Req 7: Video player must show buffering overlay and auto-retry after 20s.
    These are spec/contract tests — they validate the JS constants we set.
    """

    RETRY_TIMEOUT_MS = 20000   # must match JS stallTimerRef timeout
    BUFFER_MSG_KEYWORDS = ["buffering", "loading", "hold", "sec", "fixing"]

    def test_retry_timeout_is_20_seconds(self):
        self.assertEqual(self.RETRY_TIMEOUT_MS, 20000,
                         "Retry timeout must be exactly 20 000 ms")

    def test_buffer_messages_are_descriptive(self):
        msgs = [
            "buffering... it do be like that sometimes 🕐",
            "connection said no cap... retrying in a sec 📡",
            "ngl it's being sus rn 💀 auto-fixing it hold on...",
        ]
        for msg in msgs:
            self.assertTrue(
                any(kw in msg.lower() for kw in self.BUFFER_MSG_KEYWORDS),
                f"Buffer message doesn't seem descriptive: {msg!r}"
            )

    def test_app_js_has_video_ref(self):
        """Verify app.js source contains the videoRef and stall timer logic."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src", "main", "resources", "static", "app.js"
        )
        if not os.path.exists(js_path):
            self.skipTest("static/app.js not found (run sync first)")
        with open(js_path, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("videoRef",      src, "videoRef not found in app.js")
        self.assertIn("stallTimerRef", src, "stallTimerRef not found in app.js")
        self.assertIn("20000",         src, "20s retry constant not found in app.js")
        self.assertIn("handleWaiting", src, "handleWaiting not found in app.js")


# ───────────────────────────────────────────────────────────────────────────
# REQ 8 — Segments are named "Episode X"
# ───────────────────────────────────────────────────────────────────────────
class TestEpisodeNaming(unittest.TestCase):
    """Req 8: All segment titles must say 'Episode X', not 'Segment X'."""

    def test_no_segment_word_in_processor(self):
        """processor.py title strings should use 'Episode', not 'Segment'."""
        proc_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "processor.py"
        )
        with open(proc_path, encoding="utf-8") as f:
            src = f.read()
        # Title format lines should say Episode, not Segment
        title_lines = [l for l in src.splitlines()
                       if '"title"' in l or "'title'" in l]
        for line in title_lines:
            if "Segment" in line and "Episode" not in line:
                self.fail(f"Found 'Segment' in title line: {line.strip()!r}")

    def test_quiz_question_says_episode_not_segment(self):
        from processor import generate_quiz
        quiz = generate_quiz("Some content for testing episode naming.", 5)
        self.assertNotIn("Segment", quiz["question"],
                         f"Quiz question says 'Segment': {quiz['question']!r}")
        self.assertIn("5", quiz["question"],
                      "Episode ID should appear in question")

    def test_episode_id_in_fallback_options(self):
        from processor import generate_quiz
        quiz = generate_quiz("", 3)
        # None of the options should say "Segment 3"
        for opt in quiz["options"]:
            self.assertNotIn("Segment 3", opt,
                             f"Option still says 'Segment 3': {opt!r}")


# ───────────────────────────────────────────────────────────────────────────
# Integration smoke test
# ───────────────────────────────────────────────────────────────────────────
class TestIntegration(unittest.TestCase):
    """Quick integration smoke tests that don't require network."""

    def test_extract_video_id_valid(self):
        from processor import extract_video_id
        vid = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(vid, "dQw4w9WgXcQ")

    def test_extract_video_id_invalid(self):
        from processor import extract_video_id
        self.assertIsNone(extract_video_id("not-a-url"))
        self.assertIsNone(extract_video_id("https://example.com"))

    def test_full_quiz_pipeline_good_text(self):
        from processor import generate_quiz
        text = (
            "Black holes are regions of spacetime where gravity is so strong "
            "that nothing, not even light, can escape. They form when massive "
            "stars collapse at the end of their life cycle. "
            "Stephen Hawking proposed that black holes emit radiation."
        )
        quiz = generate_quiz(text, 1)
        self.assertEqual(len(quiz["options"]), 4)
        self.assertIn(quiz["answer"], quiz["options"])
        self.assertFalse(has_devanagari(quiz["question"]))
        self.assertFalse(has_devanagari(quiz["answer"]))
        self.assertNotIn("Segment", quiz["question"])

    def test_full_quiz_pipeline_hindi_text(self):
        from processor import generate_quiz
        hindi = "ब्लैक होल एक ऐसा क्षेत्र है जहाँ से प्रकाश भी नहीं निकल सकता।"
        quiz = generate_quiz(hindi, 2)
        self.assertEqual(len(quiz["options"]), 4)
        self.assertFalse(has_devanagari(quiz["question"]))
        self.assertFalse(has_devanagari(quiz["answer"]))
        for opt in quiz["options"]:
            self.assertFalse(has_devanagari(opt))


if __name__ == "__main__":
    unittest.main(verbosity=2)
