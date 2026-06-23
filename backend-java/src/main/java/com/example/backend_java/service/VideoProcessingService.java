package com.example.backend_java.service;

import org.springframework.stereotype.Service;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.logging.Logger;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@Service
public class VideoProcessingService {
    private static final Logger LOGGER = Logger.getLogger(VideoProcessingService.class.getName());

    // Resolve the backend-java directory from the running jar/class location
    private static final File BASE_DIR = resolveBaseDir();

    private final ScheduledExecutorService monitorExecutor = Executors.newSingleThreadScheduledExecutor();
    private String ollamaStatus = "unknown";

    public VideoProcessingService() {
        // Delay first check by 10s to let Ollama (started by START_ASTRAGRAM.bat) settle
        monitorExecutor.scheduleAtFixedRate(this::checkAndRestartOllama, 10, 15, TimeUnit.SECONDS);
    }

    private void checkAndRestartOllama() {
        try {
            // Check if ollama.exe is in the process list
            Process checkProcess = new ProcessBuilder("tasklist", "/FI", "IMAGENAME eq ollama.exe", "/NH")
                .redirectErrorStream(true)
                .start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(checkProcess.getInputStream()));
            String line;
            boolean isRunning = false;
            while ((line = reader.readLine()) != null) {
                if (line.toLowerCase().contains("ollama.exe")) {
                    isRunning = true;
                    break;
                }
            }
            checkProcess.waitFor();

            if (!isRunning) {
                // Always attempt restart regardless of previous status
                ollamaStatus = "restarting";
                LOGGER.info("Ollama is not running. Attempting to restart...");

                // Resolve ollama executable path
                String ollamaExe = null;
                String localAppData = System.getenv("LOCALAPPDATA");
                if (localAppData != null) {
                    File candidate = new File(localAppData, "Programs\\Ollama\\ollama.exe");
                    if (candidate.exists()) ollamaExe = candidate.getAbsolutePath();
                }
                if (ollamaExe == null) {
                    File candidate = new File("C:\\Program Files\\Ollama\\ollama.exe");
                    if (candidate.exists()) ollamaExe = candidate.getAbsolutePath();
                }
                if (ollamaExe == null) {
                    ollamaExe = "ollama"; // Rely on PATH
                }

                LOGGER.info("Starting Ollama via: " + ollamaExe);

                // Launch ollama serve directly — no cmd/start wrapper that can fail silently
                // M5 fix: removed redundant redirectErrorStream(true) — inheritIO() overrides it
                ProcessBuilder pb = new ProcessBuilder(ollamaExe, "serve");
                pb.inheritIO();
                pb.start();

                Thread.sleep(3000);
                ollamaStatus = "restarted";
                LOGGER.info("Ollama restart command issued.");
            } else {
                if (!"running".equals(ollamaStatus)) {
                    LOGGER.info("Ollama is running.");
                }
                ollamaStatus = "running";
            }
        } catch (Exception e) {
            LOGGER.warning("Error checking/restarting Ollama: " + e.getMessage());
            ollamaStatus = "error";
        }
    }

    public String getOllamaStatus() {
        return ollamaStatus;
    }

    private static File resolveBaseDir() {
        // When running via gradlew bootRun, working dir is backend-java/
        // Use getAbsoluteFile() first so getParentFile() is never null
        File candidate = new File("processor.py").getAbsoluteFile();
        if (candidate.exists()) {
            return candidate.getParentFile();
        }
        // Fallback to user.dir (same as working directory in most cases)
        return new File(System.getProperty("user.dir")).getAbsoluteFile();
    }

    public String processVideo(String youtubeUrl, String format, boolean fastMode, String userId) throws Exception {
        LOGGER.info("BASE_DIR resolved to: " + BASE_DIR.getAbsolutePath());
        LOGGER.info("Starting video processing for: " + youtubeUrl);

        File venvPython = new File(BASE_DIR, "venv/Scripts/python.exe");
        String pythonExe = venvPython.exists() ? venvPython.getAbsolutePath() : "python";
        File scriptFile = new File(BASE_DIR, "processor.py");

        LOGGER.info("Python: " + pythonExe);
        LOGGER.info("Script: " + scriptFile.getAbsolutePath());

        ProcessBuilder pb = new ProcessBuilder(
            pythonExe,
            scriptFile.getAbsolutePath(),
            youtubeUrl,
            format,
            fastMode ? "true" : "false",
            userId
        );
        pb.directory(BASE_DIR);
        pb.redirectErrorStream(false);
        Process process = pb.start();

        // C4 fix: drain stderr concurrently on a background thread to prevent deadlock.
        // If stderr fills its OS pipe buffer while Java is blocked reading stdout,
        // Python blocks writing stderr and Java blocks reading stdout — deadlock.
        final StringBuilder stderr = new StringBuilder();
        Thread stderrThread = new Thread(() -> {
            try {
                BufferedReader r = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                String ln;
                while ((ln = r.readLine()) != null) stderr.append(ln).append("\n");
            } catch (Exception ignored) {}
        });
        stderrThread.start();

        // Read stdout (JSON output from Python)
        BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder stdout = new StringBuilder();
        String line;
        while ((line = stdoutReader.readLine()) != null) {
            stdout.append(line).append("\n");
        }

        int exitCode = process.waitFor();
        stderrThread.join(); // wait for stderr thread to finish

        if (stderr.length() > 0) {
            LOGGER.warning("Python stderr:\n" + stderr);
        }

        if (exitCode != 0) {
            LOGGER.severe("Python script failed (exit " + exitCode + "):\nSTDOUT: " + stdout + "\nSTDERR: " + stderr);
            String errMsg = stdout.toString().trim();
            if (errMsg.isEmpty()) errMsg = stderr.toString().trim();
            throw new Exception("Processing failed: " + errMsg);
        }

        LOGGER.info("Video processing completed successfully.");

        // Find the actual JSON response (skip any debug print lines before it)
        String fullOutput = stdout.toString();
        int jsonStart = fullOutput.indexOf('{');
        if (jsonStart != -1) {
            return fullOutput.substring(jsonStart).trim();
        }

        return fullOutput.trim();
    }

    public SseEmitter streamProcessVideo(String youtubeUrl, String format, boolean fastMode, String userId) {
        // Set timeout to 0 for infinite timeout since processing can take minutes
        SseEmitter emitter = new SseEmitter(0L);
        ScheduledExecutorService pingExecutor = Executors.newSingleThreadScheduledExecutor();

        // Keep-alive ping every 10 seconds to prevent silent browser timeout
        pingExecutor.scheduleAtFixedRate(() -> {
            try {
                emitter.send(SseEmitter.event().name("ping").data("keep-alive"));
            } catch (Exception e) {
                pingExecutor.shutdown();
            }
        }, 10, 10, TimeUnit.SECONDS);

        new Thread(() -> {
            try {
                LOGGER.info("Starting streaming video processing for: " + youtubeUrl);

                File venvPython = new File(BASE_DIR, "venv/Scripts/python.exe");
                String pythonExe = venvPython.exists() ? venvPython.getAbsolutePath() : "python";
                File scriptFile = new File(BASE_DIR, "processor.py");

                ProcessBuilder pb = new ProcessBuilder(
                    pythonExe,
                    scriptFile.getAbsolutePath(),
                    youtubeUrl,
                    format,
                    fastMode ? "true" : "false",
                    userId
                );
                pb.directory(BASE_DIR);
                pb.redirectErrorStream(false);
                Process process = pb.start();

                BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                StringBuilder jsonOutput = new StringBuilder();
                String line;

                while ((line = stdoutReader.readLine()) != null) {
                    if (line.startsWith("PROGRESS:")) {
                        emitter.send(SseEmitter.event().name("progress").data(line.substring(9)));
                    } else if (line.startsWith("COURSE_INIT:")) {
                        emitter.send(SseEmitter.event().name("course_init").data(line.substring(12)));
                    } else if (line.startsWith("SEGMENT_DONE:")) {
                        emitter.send(SseEmitter.event().name("segment_done").data(line.substring(13)));
                    } else if (line.startsWith("COURSE_DONE:")) {
                        emitter.send(SseEmitter.event().name("course_done").data(line.substring(12)));
                    } else if (line.trim().startsWith("{")) {
                        // Fallback for legacy JSON error outputs
                        jsonOutput.append(line).append("\n");
                    }
                }

                // Read stderr
                BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                StringBuilder stderr = new StringBuilder();
                while ((line = stderrReader.readLine()) != null) {
                    stderr.append(line).append("\n");
                }

                int exitCode = process.waitFor();
                pingExecutor.shutdown();

                if (stderr.length() > 0) {
                    LOGGER.warning("Python stderr:\n" + stderr);
                }

                if (exitCode != 0) {
                    String errMsg = jsonOutput.toString().trim();
                    if (errMsg.isEmpty()) errMsg = stderr.toString().trim();
                    emitter.send(SseEmitter.event().name("result").data("{\"error\": \"Processing failed: " + errMsg.replace("\"", "\\\"").replace("\n", " ") + "\"}"));
                }

                emitter.complete();
            } catch (Exception e) {
                pingExecutor.shutdown();
                try {
                    emitter.send(SseEmitter.event().name("result").data("{\"error\": \"" + e.getMessage() + "\"}"));
                    emitter.complete();
                } catch (Exception ex) {
                    emitter.completeWithError(ex);
                }
            }
        }).start();

        return emitter;
    }
}
