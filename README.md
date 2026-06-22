# 🚀 ASTRAGRAM

## The Learning OS For The Next Generation

ASTRAGRAM is an AI-native adaptive learning platform designed for the internet generation.

Instead of long passive lectures, ASTRAGRAM transforms YouTube educational content into:
* ⏱️ 3-minute adaptive learning modules
* 📝 AI-generated summaries
* 🧠 Smart quizzes
* 🎯 Personalized learning paths
* 🎮 Gamified progression systems

The platform is designed to improve attention retention, concept understanding, engagement, and learning consistency.

---

## 💡 Core Idea

Traditional learning assumes attention is stable.
**ASTRAGRAM assumes attention is dynamic.**

The system converts long-form educational videos into high-retention micro-learning experiences powered by AI.

---

## 🔄 Current Workflow (MVP)

### 1. Sign In
Users access the platform through a modern, glassmorphism-styled secure entry gate.

### 2. Paste YouTube Link
The user pastes an educational YouTube video URL (e.g., `https://youtube.com/watch?v=example`).

### 3. AI Video Processing Pipeline
The Java/Python backend:
* Downloads the video (`yt-dlp`).
* Extracts and natively translates audio to English using **Whisper AI** (`openai/whisper-tiny`).
* Splits the content into perfectly timed 3-minute learning modules (`ffmpeg`).

### 4. AI Summary Generation
For every module:
* AI uses Latent Semantic Analysis (`sumy`) to rank sentence importance.
* Generates a clean, readable **Top 5 Key Takeaways** PDF.
* Gracefully handles silent segments with motivational fallbacks.

### 5. Adaptive Quiz System
After every module:
* NLP algorithms (`rake-nltk`) extract segment-specific mathematical and conceptual keywords.
* AI generates dynamic, context-aware multiple-choice questions.
* Unlocks the next module only after successful completion.

### 6. My Courses Dashboard
Users can:
* Access saved courses from a visually rich grid of YouTube thumbnails.
* Revisit modules and continue progress seamlessly.

---

## 🛠️ Tech Stack (Current MVP Implementation)

**Frontend:**
* Pure React (CDN)
* Vanilla JavaScript & Modern HTML5
* Vanilla CSS with Glassmorphism & Modern UI/UX

**Backend Orchestration:**
* Java Spring Boot REST API
* Cross-language execution pipelines

**AI & Processing Layer (Python):**
* `openai/whisper-tiny` (Transformers) for native Hindi-to-English translation & transcription
* `sumy` for Extractive Summarization
* `rake-nltk` for Rapid Automatic Keyword Extraction
* `yt-dlp` & `ffmpeg` for media processing

---

## 📁 Folder Structure

```txt
ASTRAgram/
│
├── backend-java/       # Spring Boot API & Python AI Processors
│   ├── src/            # Java Controllers & Services
│   ├── processor.py    # Core AI microservice pipeline
│   └── storage/        # Downloaded video chunks and PDFs
│
├── frontend-pure/      # Modern React SPA
│   ├── app.js          # Core React logic and Multi-Course state
│   ├── index.html      # Entry point
│   └── styles.css      # Design system and glassmorphism styling
│
└── Whisper-Hindi2Hinglish-main/ # Reference Whisper implementation
```

---

## 🚀 Local Development

### 1. Frontend
You can serve the frontend using any static server:
```bash
cd frontend-pure
# Ensure you serve on the port configured for the Java CORS (e.g., 3001)
npx serve .
```

### 2. Backend
Ensure Python 3 and FFmpeg are installed, and the virtual environment is set up.
```bash
cd backend-java
# Start the Spring Boot server
./gradlew bootRun
```
*The Java server will automatically invoke the Python environment for AI processing on port 8080.*

---

## 🔮 Future Roadmap
* Multiplayer learning & collaborative classrooms
* Next.js & PostgreSQL migration for full-scale production
* AI-generated interactive simulations
* Smart revision systems & Voice-based AI mentor

---

# Built With Vision
Designed for ambitious students, aspirational parents, and future-ready learning.

**ASTRAGRAM — Where Learning Adapts To You.**
