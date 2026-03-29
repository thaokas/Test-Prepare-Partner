package com.prepkeeper.controller;

import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.AgentClientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Tag(name = "Agent代理接口", description = "与AI Agent服务交互")
@RestController
@RequestMapping("/api/agent")
@RequiredArgsConstructor
public class AgentProxyController {

    private final AgentClientService agentClient;

    @Operation(summary = "对话代理")
    @PostMapping("/chat")
    public ResponseEntity<ApiResponse<Map<String, Object>>> chat(
            @RequestBody Map<String, String> request,
            @AuthenticationPrincipal UserPrincipal principal) {

        String message = request.get("message");
        Map<String, Object> response = agentClient.chat(principal.getUserId(), message);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取周报")
    @GetMapping("/report/weekly")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getWeeklyReport(
            @AuthenticationPrincipal UserPrincipal principal) {

        Map<String, Object> response = agentClient.generateWeeklyReport(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}