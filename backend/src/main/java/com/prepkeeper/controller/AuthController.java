package com.prepkeeper.controller;

import com.prepkeeper.dto.request.LoginRequest;
import com.prepkeeper.dto.request.RegisterRequest;
import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.dto.response.AuthResponse;
import com.prepkeeper.dto.response.UserResponse;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Tag(name = "认证接口", description = "用户注册、登录、Token刷新")
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public ResponseEntity<ApiResponse<AuthResponse>> register(@Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.register(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "用户登录")
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody LoginRequest request) {
        AuthResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "刷新Token")
    @PostMapping("/refresh")
    public ResponseEntity<ApiResponse<AuthResponse>> refresh(@RequestBody String refreshToken) {
        AuthResponse response = authService.refreshToken(refreshToken);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取当前用户信息")
    @GetMapping("/me")
    public ResponseEntity<ApiResponse<UserResponse>> getCurrentUser(@AuthenticationPrincipal UserPrincipal principal) {
        // 通过UserService获取完整用户信息
        return ResponseEntity.ok(ApiResponse.success(
                UserResponse.builder()
                        .userId(principal.getUserId())
                        .email(principal.getEmail())
                        .nickname(principal.getNickname())
                        .build()
        ));
    }
}