package com.example.backend_java.controller;

import com.example.backend_java.dto.LoginRequest;
import com.example.backend_java.dto.RegisterRequest;
import com.example.backend_java.dto.UserDto;
import com.example.backend_java.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        Optional<UserDto> user = authService.login(request);
        if (user.isPresent()) {
            UserDto u = user.get();
            // Don't send back password
            u.setPassword(null);
            return ResponseEntity.ok(u);
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid credentials"));
        }
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest request) {
        Optional<UserDto> user = authService.register(request);
        if (user.isPresent()) {
            UserDto u = user.get();
            u.setPassword(null);
            return ResponseEntity.ok(u);
        } else {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", "Email already exists"));
        }
    }
}
