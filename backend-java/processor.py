import sys
import os
import re
import math
import subprocess
import json
import random
import nltk
import ollama_agent

# Ensure nltk data is downloaded
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
# NOTE: 'from transformers import pipeline' is NOT imported at top-level.
# It is lazy-loaded only when Whisper is needed (see below), because torch/transformers
# DLLs may be blocked on some systems. Top-level import would crash the entire script.
import yt_dlp
import imageio_ffmpeg
# Add ffmpeg to PATH so transformers and other modules can call it directly
ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

from deep_translator import GoogleTranslator

# NLP Libraries
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from rake_nltk import Rake

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def generate_pdf(text, title, output_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", style='B', size=16)
        pdf.cell(w=0, h=10, text=title, new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.set_font("helvetica", size=12)
        
        pdf.cell(w=0, h=10, text="Key Takeaways:", new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.set_font("helvetica", size=11)
        
        fallback_msg = "Great job making it this far! Keep up the momentum, you are doing excellent!"
        
        # Test if the text contains a massive amount of non-Latin characters (like Hindi)
        test_replace = text.encode('latin-1', 'replace').decode('latin-1')
        if len(text) < 20 or test_replace.count('?') > len(text) * 0.2:
            pdf.multi_cell(w=0, h=8, text=fallback_msg, new_x="LMARGIN", new_y="NEXT")
        else:
            try:
                parser = PlaintextParser.from_string(text, Tokenizer("english"))
                summarizer = LsaSummarizer()
                summary = summarizer(parser.document, 5) # Top 5 sentences
                
                if not summary:
                    pdf.multi_cell(w=0, h=8, text=fallback_msg, new_x="LMARGIN", new_y="NEXT")
                else:
                    for sentence in summary:
                        safe_text = f"- {sentence}".encode('latin-1', 'ignore').decode('latin-1').strip()
                        if safe_text and safe_text != "-":
                            pdf.multi_cell(w=0, h=8, text=safe_text, new_x="LMARGIN", new_y="NEXT")
            except Exception as e:
                print(f"Summarization error: {e}", file=sys.stderr)
                pdf.multi_cell(w=0, h=8, text=fallback_msg, new_x="LMARGIN", new_y="NEXT")
            
        pdf.output(output_path)
    except Exception as e:
        print(f"Warning: PDF generation failed: {e}", file=sys.stderr)

# ── Text-quality helpers ─────────────────────────────────────────────────

def has_devanagari(text):
    """Return True if the text contains Hindi/Devanagari Unicode characters."""
    return bool(re.search(r'[\u0900-\u097F]', text or ''))

def clean_english_only(text):
    """
    Strip Devanagari and other non-Latin scripts from text.
    Keeps ASCII + extended Latin (accented European chars).
    """
    if not text:
        return ''
    # Remove Devanagari block
    cleaned = re.sub(r'[\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0B00-\u0BFF]+', ' ', text)
    # Remove other non-Latin Unicode beyond extended Latin
    cleaned = re.sub(r'[^\x00-\x7F\u00C0-\u024F\s]', ' ', cleaned)
    # Collapse whitespace
    return re.sub(r'  +', ' ', cleaned).strip()

def get_first_sentence(text):
    """Extract the first meaningful sentence (≥5 words) from cleaned text."""
    text = (text or '').strip()
    if not text:
        return ''
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for s in sentences:
        s = s.strip()
        if len(s.split()) >= 5:
            return s
    return sentences[0].strip() if sentences else text[:200]


def generate_quiz_bank(text, episode_id, num_questions=10):
    """
    Generate a full quiz bank for an episode.

    Quiz generation is 100% powered by Ollama (llama3.2) via the 10-stage
    Educational Assessment Engine system prompt.

    processor.py is responsible for structural validation ONLY:
      - questions is a non-empty list
      - each item has: question (str), options (list of 4), answer (in options), difficulty

    No AI is used for answer correctness validation — that is pure string matching.

    Returns:
        dict with keys:
            'questions' : list of {question, options, answer, difficulty}
            'ollama_used': bool — whether Ollama successfully generated the quiz
    """
    # ── 1. Call Ollama exclusively ──────────────────────────────────────────
    questions = ollama_agent.generate_full_episode_quiz(text, episode_id, num_questions)

    # ── 2. Structural validation (processor.py authority — no AI) ───────────
    if questions:
        validated = []
        for q in questions:
            # All structural checks: types, lengths, answer membership, difficulty tag
            if (
                isinstance(q.get("question"), str) and len(q["question"]) > 5
                and isinstance(q.get("options"), list) and len(q["options"]) == 4
                and all(isinstance(o, str) and len(o) > 0 for o in q["options"])
                and isinstance(q.get("answer"), str)
                and q["answer"] in q["options"]          # answer must be one of the 4 options
                and q.get("difficulty") in ("easy", "medium", "hard")
            ):
                validated.append({
                    "question":   q["question"].strip(),
                    "options":    [o.strip() for o in q["options"]],
                    "answer":     q["answer"].strip(),
                    "difficulty": q["difficulty"]
                })

        if validated:
            print(f"[processor] Quiz bank ready: {len(validated)} questions for Episode {episode_id}", file=sys.stderr)
            return {"questions": validated, "ollama_used": True}

    # ── 3. Ollama unavailable — return placeholder (not a quiz) ────────────
    print(f"[processor] Ollama unavailable for Episode {episode_id}. Returning placeholder.", file=sys.stderr)
    return {
        "questions": [{
            "question": "Ollama (llama3.2) is required to generate quiz questions. Please start Ollama and reprocess this video.",
            "options": [
                "Start Ollama: run 'ollama serve' then 'ollama pull llama3.2'",
                "Quiz generation is offline",
                "AI quiz engine not available",
                "Please restart with Ollama running"
            ],
            "answer": "Start Ollama: run 'ollama serve' then 'ollama pull llama3.2'",
            "difficulty": "easy"
        }],
        "ollama_used": False
    }

def cut_video(input_path, start_time, end_time, output_path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y", "-i", input_path,
        "-ss", str(start_time), "-to", str(end_time),
        "-c:v", "copy", "-c:a", "copy", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def extract_screenshot(video_path, output_image_path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    # Extract frame at 10 seconds and downscale to 512px width for much faster Vision LLM processing
    cmd = [
        ffmpeg_exe, "-y", "-i", video_path,
        "-ss", "00:00:10", "-vf", "scale=512:-1", "-vframes", "1", output_image_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def extract_audio(input_video_path, output_audio_path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_exe, "-i", input_video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-y", output_audio_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
        
    youtube_url = sys.argv[1]
    format_type = sys.argv[2]
    fast_mode = sys.argv[3] == "true" if len(sys.argv) > 3 else False
    
    video_id = extract_video_id(youtube_url)
    if not video_id:
        print(json.dumps({"error": "Invalid YouTube URL"}))
        sys.exit(1)
        
    try:
        print("PROGRESS:5:Extracting video info and transcript...", flush=True)
        # Check if we have YouTube Transcripts
        needs_whisper = False
        transcript = []
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            first_transcript = None
            for tr in transcript_list:
                first_transcript = tr
                break
                
            if not first_transcript:
                needs_whisper = True
            else:
                transcript = first_transcript.fetch()
        except Exception:
            needs_whisper = True
            
        # Determine Folder Name
        try:
            ydl_opts_info = {'quiet': True, 'noprogress': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                video_title = info_dict.get('title', video_id)
                video_duration = info_dict.get('duration', 0)
                clean_title = re.sub(r'[^\w\s]', '', video_title)
                words = clean_title.split()[:4]
                folder_name = "-".join(words) if words else video_id
        except Exception:
            folder_name = video_id
            video_title = f"Course for {video_id}"
            video_duration = 360 # Default to 6 mins if unknown
            
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", folder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Download Full Video
        full_video_path = f"{output_dir}/full_video.mp4"
        if not os.path.exists(full_video_path):
            print("PROGRESS:15:Downloading full video...", flush=True)
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': full_video_path,
                'quiet': True,
                'noprogress': True,
                'no_warnings': True,
                'ffmpeg_location': ffmpeg_exe,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

        chunk_duration = 300
        segments = []
        
        # Build Segment Timing Metadata
        if not needs_whisper:
            current_chunk = 1
            current_text = []
            start_time = 0.0
            
            for entry in transcript:
                start_val = entry['start'] if isinstance(entry, dict) else entry.start
                text_val = entry['text'] if isinstance(entry, dict) else entry.text
                dur_val = entry['duration'] if isinstance(entry, dict) else entry.duration
                
                if start_val >= current_chunk * chunk_duration:
                    segments.append({
                        "id": current_chunk,
                        "title": f"Episode {current_chunk} ({math.floor(start_time/60)}:00 - {math.floor((current_chunk*chunk_duration)/60)}:00)",
                        "text": " ".join(current_text),
                        "start_time": start_time,
                        "end_time": current_chunk * chunk_duration
                    })
                    current_chunk += 1
                    current_text = []
                    start_time = start_val
                    
                current_text.append(text_val)
                
            if current_text:
                last_entry = transcript[-1]
                last_start = last_entry['start'] if isinstance(last_entry, dict) else last_entry.start
                last_dur = last_entry['duration'] if isinstance(last_entry, dict) else last_entry.duration
                
                segments.append({
                    "id": current_chunk,
                    "title": f"Episode {current_chunk} ({math.floor(start_time/60)}:00+)",
                    "text": " ".join(current_text),
                    "start_time": start_time,
                    "end_time": last_start + last_dur
                })
        else:
            # If we need whisper, we build segments based on the video duration
            total_chunks = math.ceil(video_duration / chunk_duration)
            for i in range(1, total_chunks + 1):
                start_time = (i - 1) * chunk_duration
                end_time = i * chunk_duration if i < total_chunks else video_duration
                segments.append({
                    "id": i,
                    "title": f"Episode {i} ({math.floor(start_time/60)}:00 - {math.floor(end_time/60)}:00)",
                    "text": "", # Will be filled by Whisper
                    "start_time": start_time,
                    "end_time": end_time
                })
        
        processed_segments = []
        translator = GoogleTranslator(source='auto', target='en')
        whisper_pipe = None
        
        # Process Segments (Cut video, Whisper if needed, Translate, Summarize, Quiz)
        total_segs = len(segments)
        base_progress = 30
        progress_per_seg = 60 / max(1, total_segs)
        
        for i, seg in enumerate(segments):
            seg_progress = base_progress + int(i * progress_per_seg)
            print(f"PROGRESS:{seg_progress}:Processing segment {i+1}/{total_segs}...", flush=True)
            # 1. Cut Video Chunk
            chunk_video_path = f"{output_dir}/segment_{seg['id']}.mp4"
            if not os.path.exists(chunk_video_path):
                cut_video(full_video_path, seg["start_time"], seg["end_time"], chunk_video_path)
            
            # 2. Whisper Fallback
            if needs_whisper:
                if whisper_pipe is None:
                    # Lazy-import here so the script doesn't crash on systems
                    # where torch/transformers DLLs are blocked by policy.
                    try:
                        from transformers import pipeline
                    except ImportError as e:
                        print(json.dumps({"error": f"Whisper/transformers not available on this system: {e}"}))
                        sys.exit(1)
                    # Load model only once and enforce task="translate"
                    whisper_pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", chunk_length_s=30, generate_kwargs={"task": "translate"})
                    
                chunk_audio_path = f"{output_dir}/segment_{seg['id']}.wav"
                extract_audio(chunk_video_path, chunk_audio_path)
                try:
                    seg["text"] = whisper_pipe(chunk_audio_path)["text"]
                except Exception as e:
                    print(f"Whisper failed for chunk: {e}", file=sys.stderr)
                    seg["text"] = "No speech detected in this segment."
                # Cleanup audio
                if os.path.exists(chunk_audio_path):
                    os.remove(chunk_audio_path)
                    
            # 3. Translate to English (for YouTube transcripts that are not English)
            if not needs_whisper:
                try:
                    raw_text = seg["text"][:4999]
                    translated = translator.translate(raw_text)
                    # If translation still has Hindi/Devanagari, force hi→en pass
                    if has_devanagari(translated):
                        from deep_translator import GoogleTranslator as GT
                        translated = GT(source='hi', target='en').translate(raw_text[:4999])
                    # Final sanitise: strip any remaining non-Latin scripts
                    seg["text"] = clean_english_only(translated)
                except Exception as e:
                    print(f"Translation warning: {e}", file=sys.stderr)
                    # At minimum strip Devanagari from whatever we have
                    seg["text"] = clean_english_only(seg["text"])
                
            # 4. Generate & Evaluate Summary (Agentic check)
            # Basic summary extracted from text (first 3 sentences)
            sentences = [s.strip() for s in seg["text"].split('.') if len(s.strip()) > 5]
            draft_summary = ". ".join(sentences[:3]) + "." if sentences else "No summary available."
            
            # Agent evaluates and possibly rewrites
            if fast_mode:
                final_summary = draft_summary
            else:
                summary_eval = ollama_agent.evaluate_and_rewrite_summary(seg["text"], draft_summary)
                final_summary = summary_eval["summary"]
            
            # The PDF code is kept aside (not actively writing the file anymore per user request)
            # material_path = f"{output_dir}/segment_{seg['id']}.pdf"
            # generate_pdf(final_summary, seg["title"], material_path)
            
            # 5. Extract Screenshot & Generate/Validate Dynamic Quiz
            screenshot_path = f"{output_dir}/segment_{seg['id']}.jpg"
            extract_screenshot(chunk_video_path, screenshot_path)
            
            # ── Quiz generation: Ollama-only ────────────────────────────────
            print(f"PROGRESS:{seg_progress + int(progress_per_seg * 0.5)}:AI generating quiz for segment {i+1}...", flush=True)
            # Number of questions scales with transcript length
            word_count = len(seg["text"].split())
            if word_count > 2000:
                num_q = 10
            elif word_count > 800:
                num_q = 7
            else:
                num_q = 5

            quiz = generate_quiz_bank(seg["text"], seg["id"], num_q)

            # Answer validation: pure structural — no AI involved
            # The 'answer' field in each question IS the correct answer string.
            # Frontend compares selectedOption === q.answer (string match only).
            quiz["summary"] = final_summary
            
            processed_segments.append({
                "id": seg["id"],
                "title": seg["title"],
                "status": "unlocked" if seg["id"] == 1 else "locked",
                # "material_url": f"/api/course/download/{folder_name}/segment_{seg['id']}.pdf",
                "video_url": f"/api/course/download/{folder_name}/segment_{seg['id']}.mp4",
                "screenshot_url": f"/api/course/download/{folder_name}/segment_{seg['id']}.jpg",
                "quiz": quiz  # {questions: [...], summary: str, ollama_used: bool}
            })
            
        print("PROGRESS:95:Finalizing your course...", flush=True)
        result = {
            "message": "Course built successfully",
            "youtube_id": video_id,
            "course_title": video_title,
            "segments": processed_segments
        }
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": f"Processing failed: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
