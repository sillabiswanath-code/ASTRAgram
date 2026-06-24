package com.example.backend_java.controller;

import com.example.backend_java.dto.BuildRequest;
import com.example.backend_java.service.VideoProcessingService;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.io.File;
import java.util.Map;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/course")
@CrossOrigin(origins = "*")
public class CourseController {

    private final String STORAGE_DIR = new File("storage").getAbsolutePath();
    private final VideoProcessingService videoProcessingService;

    public CourseController(VideoProcessingService videoProcessingService) {
        this.videoProcessingService = videoProcessingService;
        new File(STORAGE_DIR).mkdirs();
    }

    @PostMapping("/build-from-youtube")
    public ResponseEntity<?> buildCourse(@RequestBody BuildRequest request) {
        try {
            if (request.getUserId() == null || request.getUserId().isEmpty()) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "UserId required"));
            }
            String jsonOutput = videoProcessingService.processVideo(request.getYoutube_url(), request.getFormat(), request.isFastMode(), request.getUserId());
            
            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .body(jsonOutput);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping(value = "/stream-build", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamBuildCourse(@RequestParam String url, @RequestParam String format, @RequestParam boolean fastMode, @RequestParam String userId) {
        return videoProcessingService.streamProcessVideo(url, format, fastMode, userId);
    }

    @PostMapping("/upload-video")
    public ResponseEntity<?> uploadVideo(@RequestParam("file") MultipartFile file) {
        try {
            File tempDir = new File(STORAGE_DIR, "temp_uploads");
            tempDir.mkdirs();
            File tempFile = new File(tempDir, System.currentTimeMillis() + "_" + file.getOriginalFilename());
            file.transferTo(tempFile);
            return ResponseEntity.ok(Map.of("tempFilePath", tempFile.getAbsolutePath()));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/ollama-status")
    public ResponseEntity<Map<String, String>> getOllamaStatus() {
        return ResponseEntity.ok(Map.of("status", videoProcessingService.getOllamaStatus()));
    }

    @GetMapping("/download/{userId}/{videoId}/{fileName}")
    public ResponseEntity<Resource> downloadFile(@PathVariable String userId, @PathVariable String videoId, @PathVariable String fileName) {
        try {
            Path filePath = Paths.get("users").resolve(userId).resolve("storage").resolve(videoId).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists()) {
                String contentType = "application/octet-stream";
                if (fileName.endsWith(".mp4")) contentType = "video/mp4";
                else if (fileName.endsWith(".pdf")) contentType = "application/pdf";
                else if (fileName.endsWith(".jpg") || fileName.endsWith(".jpeg")) contentType = "image/jpeg";
                
                return ResponseEntity.ok()
                        .contentType(MediaType.parseMediaType(contentType))
                        .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + resource.getFilename() + "\"")
                        .body(resource);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception ex) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/list")
    public ResponseEntity<?> listCourses(@RequestParam String userId) {
        try {
            File coursesDir = new File("users/" + userId + "/courses");
            java.util.List<Map<String, Object>> courses = new java.util.ArrayList<>();
            if (coursesDir.exists() && coursesDir.isDirectory()) {
                com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
                for (File courseFolder : coursesDir.listFiles()) {
                    if (courseFolder.isDirectory()) {
                        File meta = new File(courseFolder, "metadata.json");
                        if (meta.exists()) {
                            try {
                                Map<String, Object> metaData = mapper.readValue(meta, new com.fasterxml.jackson.core.type.TypeReference<Map<String, Object>>(){});
                                courses.add(metaData);
                            } catch (Exception ignored) {}
                        }
                    }
                }
            }
            return ResponseEntity.ok(courses);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @DeleteMapping("/delete")
    public ResponseEntity<?> deleteCourse(@RequestParam String userId, @RequestParam String courseId) {
        try {
            Path coursePath = Paths.get("users").resolve(userId).resolve("courses").resolve(courseId).normalize();
            Path storagePath = Paths.get("users").resolve(userId).resolve("storage").resolve(courseId).normalize();
            
            if (Files.exists(coursePath)) {
                org.springframework.util.FileSystemUtils.deleteRecursively(coursePath);
            }
            if (Files.exists(storagePath)) {
                org.springframework.util.FileSystemUtils.deleteRecursively(storagePath);
            }
            
            return ResponseEntity.ok(Map.of("success", true, "message", "Course deleted successfully."));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/report-quiz-question")
    public ResponseEntity<?> reportQuizQuestion(@RequestBody Map<String, Object> payload) {
        try {
            String userId = (String) payload.get("userId");
            String courseId = (String) payload.get("courseId");
            String segmentId = String.valueOf(payload.get("segmentId"));
            String questionIndex = String.valueOf(payload.get("questionIndex"));

            File baseDir = new File("processor.py").getAbsoluteFile().getParentFile();
            if (baseDir == null || !new File(baseDir, "processor.py").exists()) {
                baseDir = new File(System.getProperty("user.dir")).getAbsoluteFile();
            }

            File venvPython = new File(baseDir, "venv/Scripts/python.exe");
            String pythonExe = venvPython.exists() ? venvPython.getAbsolutePath() : "python";
            File scriptFile = new File(baseDir, "report_quiz_question.py");

            ProcessBuilder pb = new ProcessBuilder(
                pythonExe,
                scriptFile.getAbsolutePath(),
                userId,
                courseId,
                segmentId,
                questionIndex
            );
            pb.directory(baseDir);
            pb.redirectErrorStream(false);
            Process process = pb.start();
            
            // Asynchronously drain stderr to prevent OS pipe deadlocks
            new Thread(() -> {
                try {
                    java.io.BufferedReader r = new java.io.BufferedReader(new java.io.InputStreamReader(process.getErrorStream()));
                    while (r.readLine() != null) {}
                } catch (Exception ignored) {}
            }).start();
            
            java.io.BufferedReader stdoutReader = new java.io.BufferedReader(new java.io.InputStreamReader(process.getInputStream()));
            StringBuilder stdout = new StringBuilder();
            String line;
            while ((line = stdoutReader.readLine()) != null) {
                stdout.append(line).append("\n");
            }
            process.waitFor();

            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .body(stdout.toString());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/restart-ollama")
    public ResponseEntity<?> restartOllama() {
        try {
            videoProcessingService.checkAndRestartOllama();
            return ResponseEntity.ok(Map.of("success", true, "message", "Ollama restart triggered."));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }
}
