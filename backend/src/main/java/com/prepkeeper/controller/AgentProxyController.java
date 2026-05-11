package com.prepkeeper.controller;

import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.entity.Task;
import com.prepkeeper.repository.TaskRepository;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.AgentClientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Tag(name = "Agent代理接口", description = "与AI Agent服务交互")
@RestController
@RequestMapping("/agent")
@RequiredArgsConstructor
public class AgentProxyController {

    private final AgentClientService agentClient;
    private final TaskRepository taskRepository;

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

    @Operation(summary = "LLM对话代理")
    @PostMapping("/llm/chat")
    public ResponseEntity<ApiResponse<Map<String, Object>>> llmChat(
            @RequestBody Map<String, Object> request) {

        @SuppressWarnings("unchecked")
        List<Map<String, String>> messages = (List<Map<String, String>>) request.get("messages");
        String systemPrompt = (String) request.get("system_prompt");

        Map<String, Object> response = agentClient.llmChat(messages, systemPrompt);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "网络搜索代理")
    @PostMapping("/search")
    public ResponseEntity<ApiResponse<Map<String, Object>>> search(
            @RequestBody Map<String, Object> request) {

        String query = (String) request.get("query");
        Map<String, Object> response = agentClient.search(query);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "生成周报代理")
    @PostMapping("/report/weekly")
    public ResponseEntity<ApiResponse<Map<String, Object>>> generateWeeklyReport(
            @RequestBody Map<String, Object> request,
            @AuthenticationPrincipal UserPrincipal principal) {

        String weekStart = (String) request.get("weekStart");
        String weekEnd = (String) request.get("weekEnd");
        String userId = principal.getUserId();

        LocalDate startDate = LocalDate.parse(weekStart);
        LocalDate endDate = weekEnd != null ? LocalDate.parse(weekEnd) : startDate.plusDays(6);

        // 查询用户在日期范围内的所有任务（跨计划）
        List<Task> weekTasks = taskRepository.findByUserIdAndTaskDateBetween(userId, startDate, endDate);

        List<Map<String, Object>> totalPlan = weekTasks.stream()
                .map(this::toTaskMap)
                .toList();

        List<Map<String, Object>> weeklyCompleted = weekTasks.stream()
                .filter(t -> t.getStatus() == 2)
                .map(this::toTaskMap)
                .toList();

        Map<String, Object> agentResponse = agentClient.generateWeeklyReport(
                userId, weekStart, weekEnd != null ? weekEnd : endDate.toString(),
                totalPlan, weeklyCompleted);

        // 将 agent 返回的字段映射为前端期望的字段名
        Map<String, Object> response = new HashMap<>(agentResponse);
        response.put("weekStart", weekStart);
        response.put("weekEnd", weekEnd != null ? weekEnd : endDate.toString());
        if (agentResponse.containsKey("total_rate")) {
            response.put("completionRate", agentResponse.get("total_rate"));
        }
        if (agentResponse.containsKey("total_planned")) {
            response.put("totalTasks", agentResponse.get("total_planned"));
        }
        if (agentResponse.containsKey("total_completed")) {
            response.put("completedTasks", agentResponse.get("total_completed"));
        }
        if (agentResponse.containsKey("completed_hours")) {
            response.put("totalHours", agentResponse.get("completed_hours"));
        }
        if (agentResponse.containsKey("report_title")) {
            response.put("reportTitle", agentResponse.get("report_title"));
        }
        if (agentResponse.containsKey("grade")) {
            response.put("grade", agentResponse.get("grade"));
        }
        if (agentResponse.containsKey("streak_days")) {
            response.put("streakDays", agentResponse.get("streak_days"));
        }
        if (agentResponse.containsKey("daily_breakdown")) {
            response.put("dailyBreakdown", agentResponse.get("daily_breakdown"));
        }
        if (agentResponse.containsKey("subject_stats")) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> stats = (List<Map<String, Object>>) agentResponse.get("subject_stats");
            Map<String, Object> breakdown = new HashMap<>();
            if (stats != null) {
                for (Map<String, Object> s : stats) {
                    Object subject = s.get("subject");
                    Object hours = s.get("completed_minutes");
                    if (subject != null) {
                        double h = hours instanceof Number ? ((Number) hours).doubleValue() / 60.0 : 0.0;
                        breakdown.put(subject.toString(), Math.round(h * 10) / 10.0);
                    }
                }
            }
            response.put("subjectBreakdown", breakdown);
        }

        return ResponseEntity.ok(ApiResponse.success(response));
    }

    private Map<String, Object> toTaskMap(Task task) {
        Map<String, Object> map = new HashMap<>();
        map.put("task_date", task.getTaskDate() != null ? task.getTaskDate().toString() : null);
        map.put("subject", task.getSubject());
        map.put("task_content", task.getTaskContent() != null ? task.getTaskContent() : "");
        map.put("estimated_minutes", task.getEstimatedMinutes());
        map.put("task_type", task.getTaskType());
        return map;
    }
}
