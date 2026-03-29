package com.prepkeeper.controller;

import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.dto.response.TaskResponse;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.TaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "任务接口", description = "每日任务管理")
@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
public class TaskController {

    private final TaskService taskService;

    @Operation(summary = "获取今日任务")
    @GetMapping("/today")
    public ResponseEntity<ApiResponse<List<TaskResponse>>> getTodayTasks(
            @RequestParam String planId,
            @AuthenticationPrincipal UserPrincipal principal) {

        List<TaskResponse> response = taskService.getTodayTasks(planId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取计划下所有任务")
    @GetMapping("/plan/{planId}")
    public ResponseEntity<ApiResponse<List<TaskResponse>>> getTasksByPlan(
            @PathVariable String planId,
            @AuthenticationPrincipal UserPrincipal principal) {

        List<TaskResponse> response = taskService.getTasksByPlan(planId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "更新任务状态")
    @PutMapping("/{taskId}/status")
    public ResponseEntity<ApiResponse<TaskResponse>> updateTaskStatus(
            @PathVariable String taskId,
            @RequestParam Integer status,
            @AuthenticationPrincipal UserPrincipal principal) {

        TaskResponse response = taskService.updateTaskStatus(taskId, status);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "完成单个任务")
    @PostMapping("/{taskId}/complete")
    public ResponseEntity<ApiResponse<TaskResponse>> completeTask(
            @PathVariable String taskId,
            @AuthenticationPrincipal UserPrincipal principal) {

        TaskResponse response = taskService.completeTask(taskId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}