package com.prepkeeper.controller;

import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.dto.response.UserResponse;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户接口", description = "用户信息管理")
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "获取用户信息")
    @GetMapping("/{userId}")
    public ResponseEntity<ApiResponse<UserResponse>> getUser(
            @PathVariable String userId,
            @AuthenticationPrincipal UserPrincipal principal) {

        // 只能查看自己的信息
        if (!principal.getUserId().equals(userId)) {
            return ResponseEntity.status(403).build();
        }

        UserResponse response = userService.getUserById(userId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "更新用户信息")
    @PutMapping("/{userId}")
    public ResponseEntity<ApiResponse<UserResponse>> updateUser(
            @PathVariable String userId,
            @RequestParam(required = false) String nickname,
            @RequestParam(required = false) String avatarUrl,
            @AuthenticationPrincipal UserPrincipal principal) {

        if (!principal.getUserId().equals(userId)) {
            return ResponseEntity.status(403).build();
        }

        UserResponse response = userService.updateUser(userId, nickname, avatarUrl);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取用户统计")
    @GetMapping("/{userId}/stats")
    public ResponseEntity<ApiResponse<UserResponse>> getUserStats(
            @PathVariable String userId,
            @AuthenticationPrincipal UserPrincipal principal) {

        if (!principal.getUserId().equals(userId)) {
            return ResponseEntity.status(403).build();
        }

        UserResponse response = userService.getUserById(userId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}