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

import java.util.List;
import java.util.Map;

@Tag(name = "Agent代理接口", description = "与AI Agent服务交互")
@RestController
@RequestMapping("/api/agent")
@RequiredArgsConstructor
public class AgentProxyController {

    private final AgentClientService agentClient;

    @Operation(summary = "对话式计划生成代理")
    @PostMapping("/plan/chat")
    public ResponseEntity<ApiResponse<Map<String, Object>>> planChat(
            @RequestBody Map<String, Object> request,
            @AuthenticationPrincipal UserPrincipal principal) {

        String message = (String) request.get("message");
        String threadId = (String) request.get("threadId");

        @SuppressWarnings("unchecked")
        List<String> urls = (List<String>) request.get("urls");
        @SuppressWarnings("unchecked")
        List<String> pdfUrls = (List<String>) request.get("pdfUrls");
        @SuppressWarnings("unchecked")
        List<String> imageUrls = (List<String>) request.get("imageUrls");

        Map<String, Object> response = agentClient.planChat(
                principal.getUserId(), message, threadId, urls, pdfUrls, imageUrls);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "生成周报代理")
    @PostMapping("/report/weekly")
    public ResponseEntity<ApiResponse<Map<String, Object>>> generateWeeklyReport(
            @RequestBody Map<String, Object> request,
            @AuthenticationPrincipal UserPrincipal principal) {

        String weekStart = (String) request.get("weekStart");
        String weekEnd = (String) request.get("weekEnd");

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> totalPlan = (List<Map<String, Object>>) request.get("totalPlan");
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> weeklyCompleted = (List<Map<String, Object>>) request.get("weeklyCompleted");

        Map<String, Object> response = agentClient.generateWeeklyReport(
                principal.getUserId(), weekStart, weekEnd, totalPlan, weeklyCompleted);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
