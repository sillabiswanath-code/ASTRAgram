package com.example.backend_java.service;

import org.springframework.stereotype.Service;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.logging.Logger;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Service
public class VideoProcessingService {
    private static final Logger LOGGER = Logger.getLogger(VideoProcessingService.class.getName());

    // Resolve the backend-java directory from the running jar/class location
    private static final File BASE_DIR = resolveBaseDir();

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

    public String processVideo(String youtubeUrl, String format, boolean fastMode) throws Exception {
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
            fastMode ? "true" : "false"
        );
        // Set working directory explicitly so storage/ and venv/ paths resolve correctly
        pb.directory(BASE_DIR);
        // Capture stdout and stderr separately
        pb.redirectErrorStream(false);
        Process process = pb.start();

        // Read stdout (JSON output from Python)
        BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder stdout = new StringBuilder();
        String line;
        while ((line = stdoutReader.readLine()) != null) {
            stdout.append(line).append("\n");
        }

        // Read stderr (logs/warnings from Python)
        BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        StringBuilder stderr = new StringBuilder();
        while ((line = stderrReader.readLine()) != null) {
            stderr.append(line).append("\n");
        }

        int exitCode = process.waitFor();

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

    public SseEmitter streamProcessVideo(String youtubeUrl, String format, boolean fastMode) {
        // Set timeout to 0 for infinite timeout since processing can take minutes
        SseEmitter emitter = new SseEmitter(0L);

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
                    fastMode ? "true" : "false"
                );
                pb.directory(BASE_DIR);
                pb.redirectErrorStream(false);
                Process process = pb.start();

                BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                StringBuilder jsonOutput = new StringBuilder();
                String line;
                boolean inJson = false;

                while ((line = stdoutReader.readLine()) != null) {
                    if (line.startsWith("PROGRESS:")) {
                        // Send progress event
                        emitter.send(SseEmitter.event().name("progress").data(line.substring(9)));
                    } else if (line.trim().startsWith("{") || inJson) {
                        inJson = true;
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

                if (stderr.length() > 0) {
                    LOGGER.warning("Python stderr:\n" + stderr);
                }

                if (exitCode != 0) {
                    String errMsg = jsonOutput.toString().trim();
                    if (errMsg.isEmpty()) errMsg = stderr.toString().trim();
                    emitter.send(SseEmitter.event().name("result").data("{\"error\": \"Processing failed: " + errMsg.replace("\"", "\\\"").replace("\n", " ") + "\"}"));
                } else {
                    String result = jsonOutput.toString().trim();
                    if (result.isEmpty()) result = "{\"error\": \"No JSON output found\"}";
                    emitter.send(SseEmitter.event().name("result").data(result));
                }

                emitter.complete();
            } catch (Exception e) {
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
