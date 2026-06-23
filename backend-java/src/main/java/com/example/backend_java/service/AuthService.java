package com.example.backend_java.service;

import com.example.backend_java.dto.LoginRequest;
import com.example.backend_java.dto.RegisterRequest;
import com.example.backend_java.dto.UserDto;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class AuthService {

    private final String ACCOUNTS_FILE = new File("accounts.json").getAbsolutePath();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public AuthService() {
        File file = new File(ACCOUNTS_FILE);
        if (!file.exists()) {
            try {
                objectMapper.writeValue(file, new ArrayList<UserDto>());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private List<UserDto> getUsers() {
        try {
            return objectMapper.readValue(new File(ACCOUNTS_FILE), new TypeReference<List<UserDto>>() {});
        } catch (IOException e) {
            return new ArrayList<>();
        }
    }

    private void saveUsers(List<UserDto> users) {
        try {
            objectMapper.writeValue(new File(ACCOUNTS_FILE), users);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public Optional<UserDto> login(LoginRequest request) {
        return getUsers().stream()
                .filter(u -> u.getEmail().equalsIgnoreCase(request.getEmail()) && u.getPassword().equals(request.getPassword()))
                .findFirst();
    }

    public Optional<UserDto> register(RegisterRequest request) {
        List<UserDto> users = getUsers();
        if (users.stream().anyMatch(u -> u.getEmail().equalsIgnoreCase(request.getEmail()))) {
            return Optional.empty(); // User exists
        }

        UserDto newUser = new UserDto(
                UUID.randomUUID().toString(),
                request.getEmail(),
                request.getPassword(),
                request.getName()
        );
        
        users.add(newUser);
        saveUsers(users);
        
        // Ensure user directories are created
        new File("users", newUser.getId() + "/courses").mkdirs();
        new File("users", newUser.getId() + "/storage").mkdirs();
        
        return Optional.of(newUser);
    }
}
