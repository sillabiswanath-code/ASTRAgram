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
            String jsonOutput = videoProcessingService.processVideo(request.getYoutube_url(), request.getFormat(), request.isFastMode());
            
            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .body(jsonOutput);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping(value = "/stream-build", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamBuildCourse(@RequestParam String url, @RequestParam String format, @RequestParam boolean fastMode) {
        return videoProcessingService.streamProcessVideo(url, format, fastMode);
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

    @GetMapping("/download/{videoId}/{fileName}")
    public ResponseEntity<Resource> downloadFile(@PathVariable String videoId, @PathVariable String fileName) {
        try {
            Path filePath = Paths.get(STORAGE_DIR).resolve(videoId).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists()) {
                String contentType = "application/octet-stream";
                if (fileName.endsWith(".mp4")) contentType = "video/mp4";
                else if (fileName.endsWith(".pdf")) contentType = "application/pdf";
                
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
}
