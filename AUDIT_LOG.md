# ASTRAgram — Codebase Audit & Fix Log
> Last updated: 2026-06-20 · Session continues from here each time

---

## Architecture Overview

```
ASTRAgram-main/
├── backend-java/              ← Spring Boot (Java 26, port 8080)
│   ├── src/main/java/...      ← Java source
│   │   ├── BackendJavaApplication.java   (main entry)
│   │   ├── controller/CourseController.java
│   │   ├── service/VideoProcessingService.java
│   │   └── dto/BuildRequest.java
│   ├── src/main/resources/static/   ← Frontend served by Spring Boot
│   │   ├── index.html, app.js, styles.css, logo.mp4, graph.html
│   ├── src/test/...           ← JUnit tests
│   ├── processor.py           ← Python script (called by Java via ProcessBuilder)
│   ├── regenerate_missing.py  ← Utility script for missing PDFs
│   ├── requirements.txt       ← Python deps
│   └── venv/                  ← Python 3.11.9 virtualenv
├── frontend-pure/             ← Source of truth for frontend (sync → static/)
│   ├── app.js, styles.css, index.html, logo.mp4
└── frontend-react/            ← Vite/React (separate, not currently served)
```

### Data Flow
```
Browser → GET localhost:8080 → Spring Boot serves static/index.html
Browser → POST /api/course/build-from-youtube → CourseController
  → VideoProcessingService.processVideo()
    → Spawns: venv/Scripts/python.exe processor.py <url> <format>
      → YouTube transcript / yt-dlp download / Whisper / PDF / Quiz
      → prints JSON to stdout
  → Java reads stdout JSON → returns to browser
Browser → GET /api/course/download/{videoId}/{file} → serves from storage/
```

---

## Session 1 — 2026-06-20

### Tests Run
| Test | Result |
|------|--------|
| `./gradlew test` (Java contextLoads) | ✅ PASS |
| Python syntax check (ast.parse) | ✅ PASS (both .py files) |
| Python imports check | ⚠️ PARTIAL (see issues) |
| HTTP GET / | ✅ 200 OK |
| HTTP GET /app.js | ✅ 200 OK (34741 bytes) |
| HTTP GET /styles.css | ✅ 200 OK (8569 bytes) |
| HTTP GET /logo.mp4 | ✅ 200 OK (123277 bytes) |
| HTTP POST /api/course/build-from-youtube | ❌ 500 (see Issue #1) |
| JS video tags audit | ⚠️ 1 leftover video tag in static/app.js |
| LogoMark component | ✅ Present |
| LogoSplash component | ✅ Present |
| sessionStorage splash logic | ✅ Present |

---

## Issues Found & Status

### ✅ FIXED #1 — CRITICAL: `transformers` / `torch` DLL blocked by Application Control Policy
**File:** `backend-java/processor.py` line 17  
**Error:**
```
DLL load failed while importing _C: An Application Control policy has blocked this file.
```
**Root cause:** `from transformers import pipeline` was a **top-level import**.
Script crashed immediately even for videos WITH YouTube transcripts (no Whisper needed).

**Fix applied:** Moved import to inside the `if needs_whisper:` lazy-load block with try/except.
Now the script works for all YouTube videos that have transcripts. Whisper-only videos
will gracefully fail with a clear error message instead of crashing silently.

---

### ✅ VERIFIED #2 — 1 `<video>` tag in static/app.js is intentional
The remaining `<video>` tag is in `SegmentViewer` component for course video playback.
This is correct and should remain.

---

### ✅ FIXED #3 — `regenerate_missing.py` hardcoded absolute path
Changed to `os.path.dirname(os.path.abspath(__file__))` — now works from any directory.

---

### ✅ FIXED #4 — `build.gradle` incorrect Spring Boot dependency names
Changed `spring-boot-starter-webmvc` → `spring-boot-starter-web`
Changed `spring-boot-starter-webmvc-test` → `spring-boot-starter-test`

---

### ✅ FIXED #5 — `VideoProcessingService` working directory + stderr capture
- Added `pb.directory(BASE_DIR)` to fix path resolution
- Separated stdout/stderr reading so Python warnings don't pollute JSON output
- Added `resolveBaseDir()` static method to robustly find backend-java/
- Fixed NPE: used `new File("processor.py").getAbsoluteFile()` before `getParentFile()`

---

### ✅ FIXED #6 — `regenerate_missing.py` duplicate `import os`
Removed duplicate `import os` on line 8.

---

### ✅ FIXED #7 — `application.properties` expanded
Added: server port, error detail for debugging, async timeout for long Python processing.

---

### ⚠️ KNOWN LIMITATION — `torch`/`transformers` blocked by OS policy
**Not fixable in code.** Whisper fallback (for videos without YouTube transcripts) will not
work on this machine until the Application Control policy allows torch DLLs.
Videos WITH YouTube transcripts work fine (majority of use cases).

---

---

## How to Start the Server
```powershell
cd B:\ASTRAgram-main\backend-java
.\gradlew.bat bootRun
# Open: http://localhost:8080
```

## How to Run Tests
```powershell
cd B:\ASTRAgram-main\backend-java
.\gradlew.bat test
```

## How to Check Python Environment
```powershell
cd B:\ASTRAgram-main\backend-java
venv\Scripts\python.exe processor.py "https://youtube.com/watch?v=dQw4w9WgXcQ" pdf
```

---

## Session 2 — Next-Gen Agentic Pipeline & UI Upgrade (Completed)

### Quality Tests Run
| Test | Result |
|------|--------|
| `test_all.py` - Comprehensive Quality Suite | ✅ PASS (All 8 requirements met) |

### Features Implemented
1. **Ollama Integration (`ollama_agent.py`):**
   - Successfully installed and started background pulls for `openhermes` and `llava` local models.
   - Designed integration for `openhermes` to rewrite summaries under 90% relevance.
   - Designed integration for `llava` to validate quizzes against video screenshots extracted via `ffmpeg`.
2. **Backend Processing (`processor.py`):**
   - Rewritten main processing loop to decouple audio/transcript and inject agentic evaluation checks.
   - Removed/Hid the PDF guide logic from the active workflow.
3. **Frontend UI Upgrade (`app.js` & `styles.css`):**
   - Replaced old orange sidebar layout with the modern "Grammar Pro" blue navbar and hero layout.
   - SegmentViewer updated to completely hide the Reading Guide tab per user constraints.
   - At user's request, used `openhermes` to generate the raw React scaffolding for the UI and applied it directly to demonstrate local AI capabilities.
   - **Post-Generation Fix:** The initial `openhermes` output caused a white screen because it omitted React props (`currentView`, `courses`). I fed the error back into `openhermes` via a python script (`ollama_fixer.py`). The model successfully identified the missing props and generated a corrected `Navbar` and `Home` component. These corrections were automatically applied and the application is stable.

---

## Session 3 — Syntax checks and Batch Script Fixes
- Ran all python check scripts (`check.py`, `check_models.py`, `check_jsx.py`, `ollama_fixer.py`).
- Identified that `check.py` and `check_jsx.py` reported false positives due to their naive regex logic lacking support for self-closing JSX tags.
- Fixed `START_ASTRAGRAM.bat` to prevent "Input redirection is not supported" crashes by replacing `timeout` commands with `ping 127.0.0.1`.
- Fixed `START_ASTRAGRAM.bat` to redirect Ollama output so it doesn't block the Java server startup and properly runs in the background.

---

## CRITICAL RULES FOR PREVENTING FAILURES
To ensure the application never breaks or displays a white screen after an update:
1. **Always Rebuild the JAR (`gradlew bootJar`)**: Any changes made to `frontend-pure/` or `backend-java/src/main/resources/static/` MUST be followed by running `.\gradlew.bat bootJar` inside the `backend-java` folder. The application serves files from inside the compiled JAR, not the raw source files on disk!
2. **Never Use `timeout` with Output Redirection**: Windows batch scripts crash instantly if `timeout /t X >nul` is run in the background. Always use `ping 127.0.0.1 -n X >nul` to safely pause scripts.
3. **Always Validate React JSX**: AI-generated code often misses required props or contains illegal JavaScript (e.g., `if` statements inside JSX blocks instead of ternary operators). Always verify component integrity before saving `app.js`.
4. **Isolate Ollama Startup**: Ollama must be launched asynchronously (`start /B ... cmd /c ...`) and its output redirected to a log file. If it shares the main console handle, the batch script will hang indefinitely.
