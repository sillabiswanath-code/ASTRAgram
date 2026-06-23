import os
import sys
import subprocess
import json
import math
import imageio_ffmpeg
# Add ffmpeg to PATH so transformers can find it
ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

from fpdf import FPDF
# NOTE: transformers/pipeline is lazy-loaded below (torch may be blocked on some systems)
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def extract_audio(input_video_path, output_audio_path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_exe, "-i", input_video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-y", output_audio_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
        print(f"Generated PDF: {output_path}")
    except Exception as e:
        print(f"Warning: PDF generation failed: {e}", file=sys.stderr)

def main():
    # M11 fix: accept CLI args instead of hardcoded dev paths
    # Usage: python regenerate_missing.py <course_folder_name> [seg_id1 seg_id2 ...]
    if len(sys.argv) < 2:
        print("Usage: python regenerate_missing.py <course_folder_name> [seg_id1 seg_id2 ...]")
        print("Example: python regenerate_missing.py IOQM-2026-Achievers-Batch 1 3 5")
        sys.exit(1)

    course_folder = sys.argv[1]
    # Parse optional segment IDs; default to [1] if not given
    try:
        seg_ids = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else [1]
    except ValueError:
        print("Error: segment IDs must be integers")
        sys.exit(1)

    # Use __file__ so path works regardless of where script is invoked from
    base_dir = os.path.dirname(os.path.abspath(__file__))
    storage_dir = os.path.join(base_dir, "storage")
    course_dir = os.path.join(storage_dir, course_folder)
    if not os.path.exists(course_dir):
        print(f"Course directory not found: {course_dir}")
        print(f"Available courses: {os.listdir(storage_dir) if os.path.exists(storage_dir) else 'storage/ not found'}")
        return

    print(f"Processing course: {course_dir}")
    print(f"Segment IDs to regenerate: {seg_ids}")
    print("Loading whisper pipeline...")
    try:
        from transformers import pipeline
    except ImportError as e:
        print(f"ERROR: transformers not available: {e}")
        return
    whisper_pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", chunk_length_s=30, generate_kwargs={"task": "translate"})

    for seg_id in seg_ids:
        pdf_path = os.path.join(course_dir, f"segment_{seg_id}.pdf")
        mp4_path = os.path.join(course_dir, f"segment_{seg_id}.mp4")
        wav_path = os.path.join(course_dir, f"segment_{seg_id}.wav")

        if not os.path.exists(mp4_path):
            print(f"Segment video not found: {mp4_path}")
            continue

        print(f"Processing segment {seg_id}...")
        
        # 1. Extract audio
        extract_audio(mp4_path, wav_path)

        # 2. Transcribe
        print("Transcribing with Whisper...")
        text = whisper_pipe(wav_path)["text"]
        print(f"Transcript preview: {text[:100]}...")

        # 3. Generate PDF
        title = f"Segment {seg_id}"
        generate_pdf(text, title, pdf_path)

        # 4. Clean up audio
        if os.path.exists(wav_path):
            os.remove(wav_path)

    print("All missing PDFs regenerated!")

if __name__ == "__main__":
    main()
