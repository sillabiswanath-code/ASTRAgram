import sys
import os
import re
import math
import subprocess
import json
import random
import random
import nltk
import ollama_agent
import storage_manager

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

def clean_transcript_text(text):
    """Fix punctuation, remove fillers."""
    cleaned = re.sub(r'\b(um|uh|like|you know|sort of|kind of|I mean)\b', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def build_topic_segments(transcript, video_duration, target_duration=180):
    segments = []
    current_chunk = 1
    current_text = []
    start_time = 0.0
    last_end = 0.0
    
    for entry in transcript:
        start_val = entry['start'] if isinstance(entry, dict) else entry.start
        text_val = entry['text'] if isinstance(entry, dict) else entry.text
        dur_val = entry['duration'] if isinstance(entry, dict) else entry.duration
        
        elapsed = start_val - start_time
        pause = start_val - last_end
        
        if (elapsed > target_duration and pause > 1.0) or elapsed > 300:
            segments.append({
                "id": current_chunk,
                "title": f"Episode {current_chunk} ({math.floor(start_time/60)}:{(int(start_time)%60):02d} - {math.floor(start_val/60)}:{(int(start_val)%60):02d})",
                "text": clean_transcript_text(" ".join(current_text)),
                "start_time": start_time,
                "end_time": start_val
            })
            current_chunk += 1
            current_text = []
            start_time = start_val
            
        current_text.append(text_val)
        last_end = start_val + dur_val
        
    if current_text:
        segments.append({
            "id": current_chunk,
            "title": f"Episode {current_chunk} ({math.floor(start_time/60)}:{(int(start_time)%60):02d}+)",
            "text": clean_transcript_text(" ".join(current_text)),
            "start_time": start_time,
            "end_time": last_end if last_end > start_time else start_time + 60
        })
    return segments


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
    # Supports all three question types generated by ollama_agent.py:
    #   single_mcq    : answer is a str, must be in options (4 items)
    #   multiple_mcq  : answer is a list of strs, all must be in options (4 items)
    #   match_following: has pairs list of {left, right} dicts, no options/answer field
    if questions:
        validated = []
        for q in questions:
            q_type = q.get("type", "single_mcq")
            difficulty = q.get("difficulty", "")
            question_text = q.get("question", "")

            # Common gate: must have a real question string and valid difficulty
            if not (isinstance(question_text, str) and len(question_text) > 5
                    and difficulty in ("easy", "medium", "hard")):
                continue

            if q_type == "single_mcq":
                options = q.get("options", [])
                answer = q.get("answer", "")
                if (isinstance(options, list) and len(options) == 4
                        and all(isinstance(o, str) and len(o) > 0 for o in options)
                        and isinstance(answer, str)
                        and answer in options):
                    validated.append({
                        "type":       "single_mcq",
                        "question":   question_text.strip(),
                        "options":    [o.strip() for o in options],
                        "answer":     answer.strip(),
                        "difficulty": difficulty
                    })

            elif q_type == "multiple_mcq":
                options = q.get("options", [])
                answer = q.get("answer", [])
                if (isinstance(options, list) and len(options) == 4
                        and all(isinstance(o, str) and len(o) > 0 for o in options)
                        and isinstance(answer, list) and len(answer) >= 2
                        and all(a in options for a in answer)):
                    validated.append({
                        "type":       "multiple_mcq",
                        "question":   question_text.strip(),
                        "options":    [o.strip() for o in options],
                        "answer":     [a.strip() for a in answer],
                        "difficulty": difficulty
                    })

            elif q_type == "match_following":
                pairs = q.get("pairs", [])
                if (isinstance(pairs, list) and len(pairs) >= 2
                        and all(isinstance(p, dict) and "left" in p and "right" in p for p in pairs)):
                    validated.append({
                        "type":       "match_following",
                        "question":   question_text.strip(),
                        "pairs":      [{"left": p["left"].strip(), "right": p["right"].strip()} for p in pairs],
                        "difficulty": difficulty
                    })

        if validated:
            print(f"[processor] Quiz bank ready: {len(validated)} questions for Episode {episode_id}", file=sys.stderr)
            return {"questions": validated, "ollama_used": True}

    # ── 3. Ollama unavailable — return placeholder (not a quiz) ────────────
    print(f"[processor] Ollama unavailable for Episode {episode_id}. Returning placeholder.", file=sys.stderr)
    return {
        "questions": [{
            "question": "Ollama (qwen2.5:3b-instruct) is required to generate quiz questions. Please start Ollama and reprocess this video.",
            "options": [
                "Start Ollama: run 'ollama serve' then 'ollama pull qwen2.5:3b-instruct'",
                "Quiz generation is offline",
                "AI quiz engine not available",
                "Please restart with Ollama running"
            ],
            "answer": "Start Ollama: run 'ollama serve' then 'ollama pull qwen2.5:3b-instruct'",
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

def get_video_duration(video_path):
    # subprocess already imported at top of module (M9 fix: removed duplicate import)
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffprobe_exe = ffmpeg_exe.replace('ffmpeg', 'ffprobe')
        result = subprocess.run(
            [ffprobe_exe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        # C5 fix: result.stdout is bytes — must decode before float() conversion
        return float(result.stdout.decode('utf-8').strip())
    except Exception:
        return 360

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
        
    video_input = sys.argv[1]
    format_type = sys.argv[2]
    fast_mode = sys.argv[3] == "true" if len(sys.argv) > 3 else False
    user_id = sys.argv[4] if len(sys.argv) > 4 else "vedan123"
    
    storage_manager.USER_ID = user_id
    
    is_local_file = os.path.isfile(video_input)
    
    if not is_local_file:
        video_id = extract_video_id(video_input)
        if not video_id:
            print(json.dumps({"error": "Invalid input: neither a local file nor a valid YouTube URL"}))
            sys.exit(1)
    else:
        video_id = os.path.splitext(os.path.basename(video_input))[0]
        
    try:
        print("PROGRESS:5:Extracting video info and transcript...", flush=True)
        # Check if we have YouTube Transcripts
        needs_whisper = False
        transcript = []
        if not is_local_file:
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
        else:
            needs_whisper = True
            
        # Determine Folder Name
        if not is_local_file:
            try:
                ydl_opts_info = {'quiet': True, 'noprogress': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info_dict = ydl.extract_info(video_input, download=False)
                    video_title = info_dict.get('title', video_id)
                    video_duration = info_dict.get('duration', 0)
                    clean_title = re.sub(r'[^\w\s]', '', video_title)
                    words = clean_title.split()[:4]
                    folder_name = "-".join(words) if words else video_id
            except Exception:
                folder_name = video_id
                video_title = f"Course for {video_id}"
                video_duration = 360 # Default to 6 mins if unknown
        else:
            folder_name = video_id
            video_title = f"Local Course: {video_id}"
            video_duration = get_video_duration(video_input)
            
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users", user_id, "storage", folder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Check cache
        metadata = storage_manager.load_metadata(folder_name)
        if metadata and metadata.get("status") == "completed":
            print("PROGRESS:100:Loaded existing course from cache...", flush=True)
            course_init_data = metadata.get("course_init_data")
            if course_init_data:
                print(f"COURSE_INIT:{json.dumps(course_init_data)}", flush=True)
                for seg in course_init_data["segments"]:
                    cached_quiz = storage_manager.load_quiz(folder_name, seg["id"])
                    seg_done = {
                        "id": seg["id"],
                        "title": seg["title"],
                        "status": "unlocked" if seg["id"] == 1 else "locked",
                        "video_url": f"/api/course/download/{user_id}/{folder_name}/segment_{seg['id']}.mp4",
                        "screenshot_url": f"/api/course/download/{user_id}/{folder_name}/segment_{seg['id']}.jpg",
                        "quiz": cached_quiz if cached_quiz else {}
                    }
                    print(f"SEGMENT_DONE:{json.dumps(seg_done)}", flush=True)
            result = {
                "message": "Course loaded from cache successfully",
                "youtube_id": video_id,
                "course_title": video_title,
                "final_summary": metadata.get("final_summary", "")
            }
            print(f"COURSE_DONE:{json.dumps(result)}", flush=True)
            sys.exit(0)
        
        # Download Full Video
        full_video_path = f"{output_dir}/full_video.mp4"
        if not os.path.exists(full_video_path):
            if is_local_file:
                print("PROGRESS:15:Copying local video...", flush=True)
                import shutil
                shutil.copy2(video_input, full_video_path)
            else:
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
                    ydl.download([video_input])

        # Build Segment Timing Metadata
        if not needs_whisper:
            segments = build_topic_segments(transcript, video_duration)
        else:
            # If we need whisper, we build segments based on the video duration
            chunk_duration = 180
            total_chunks = math.ceil(video_duration / chunk_duration)
            segments = []
            for i in range(1, total_chunks + 1):
                start_time = (i - 1) * chunk_duration
                end_time = i * chunk_duration if i < total_chunks else video_duration
                segments.append({
                    "id": i,
                    "title": f"Episode {i} ({math.floor(start_time/60)}:{(int(start_time)%60):02d} - {math.floor(end_time/60)}:{(int(end_time)%60):02d})",
                    "text": "", # Will be filled by Whisper
                    "start_time": start_time,
                    "end_time": end_time
                })
        
        processed_segments = []
        translator = GoogleTranslator(source='auto', target='en')
        whisper_pipe = None
        
        course_init_data = {
            "youtube_id": video_id,
            "course_title": video_title,
            "segments": [
                {
                    "id": s["id"],
                    "title": s["title"],
                    "status": "locked",
                    "video_url": f"/api/course/download/{user_id}/{folder_name}/segment_{s['id']}.mp4",
                    "screenshot_url": f"/api/course/download/{user_id}/{folder_name}/segment_{s['id']}.jpg",
                    "quiz": None
                } for s in segments
            ]
        }
        print(f"COURSE_INIT:{json.dumps(course_init_data)}", flush=True)
        
        storage_manager.save_metadata(folder_name, {
            "status": "processing",
            "course_title": video_title,
            "youtube_id": video_id,
            "course_init_data": course_init_data
        })
        
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
            
            # M8 fix: only call Ollama if there is meaningful text (saves a pointless API call)
            if fast_mode or len(seg["text"].split()) < 20:
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
            cached_quiz = storage_manager.load_quiz(folder_name, seg["id"])
            if cached_quiz:
                print(f"PROGRESS:{seg_progress + int(progress_per_seg * 0.5)}:Loaded cached quiz for segment {i+1}...", flush=True)
                quiz = cached_quiz
            else:
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
                if quiz:
                    quiz["summary"] = final_summary
                    storage_manager.save_quiz(folder_name, seg["id"], quiz)

            storage_manager.save_episode(folder_name, seg["id"], seg["title"], final_summary, seg["text"])
            
            processed_segments.append({
                "id": seg["id"],
                "title": seg["title"],
                "status": "unlocked" if seg["id"] == 1 else "locked",
                "video_url": f"/api/course/download/{user_id}/{folder_name}/segment_{seg['id']}.mp4",
                "screenshot_url": f"/api/course/download/{user_id}/{folder_name}/segment_{seg['id']}.jpg",
                "quiz": quiz
            })
            print(f"SEGMENT_DONE:{json.dumps(processed_segments[-1])}", flush=True)
            
        print("PROGRESS:95:Finalizing your course and generating summary...", flush=True)
        # Generate full bullet-point summary
        full_text = " ".join([s.get("text", "") for s in segments])[:10000]
        final_summary = "Failed to generate summary."
        try:
            prompt_query = (
                f"Topic/Title: {video_title}\n\n"
                f"Task: Generate exactly 5 to 7 'Important Points to Remember'.\n"
                f"Instructions: Mix the insights from the provided transcript with your own expert, external knowledge regarding the topic '{video_title}'. "
                f"Do not just summarize the transcript; enrich it with your deep knowledge on this subject. Make it highly accurate and insightful. "
                f"Transcript:\n{full_text}"
            )
            sum_res = ollama_agent.query_ollama(
                prompt_query, 
                model=ollama_agent.QUIZ_MODEL, 
                system_prompt="You are a strict educational expert. Output ONLY a concise bulleted list of the most critical points. No preamble, no conversational text."
            )
            if "error" not in sum_res:
                final_summary = sum_res["response"]
        except Exception as e:
            print(f"Summary generation warning: {e}", file=sys.stderr)
            
        storage_manager.save_course(folder_name, video_title, final_summary)
        metadata = storage_manager.load_metadata(folder_name)
        if metadata:
            metadata["status"] = "completed"
            metadata["final_summary"] = final_summary
            metadata["segments"] = processed_segments
            storage_manager.save_metadata(folder_name, metadata)
            
        result = {
            "message": "Course built successfully",
            "youtube_id": video_id,
            "course_title": video_title,
            "final_summary": final_summary
        }
        print(f"COURSE_DONE:{json.dumps(result)}", flush=True)
        
    except Exception as e:
        print(json.dumps({"error": f"Processing failed: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
