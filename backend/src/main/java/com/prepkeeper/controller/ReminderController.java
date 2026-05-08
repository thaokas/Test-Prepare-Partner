package com.prepkeeper.controller;

import com.prepkeeper.dto.request.ReminderConfigRequest;
import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.dto.response.PlanResponse;
import com.prepkeeper.dto.response.ReminderSettingsResponse;
import com.prepkeeper.entity.Reminder;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.ReminderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "提醒接口", description = "提醒设置管理")
@RestController
@RequestMapping("/api/reminders")
@RequiredArgsConstructor
public class ReminderController {

    private final ReminderService reminderService;

    @Operation(summary = "获取提醒列表")
    @GetMapping
    public ResponseEntity<ApiResponse<List<Reminder>>> getReminders(
            @AuthenticationPrincipal UserPrincipal principal) {
        List<Reminder> reminders = reminderService.getReminderList(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(reminders));
    }

    @Operation(summary = "获取提醒设置")
    @GetMapping("/settings")
    public ResponseEntity<ApiResponse<ReminderSettingsResponse>> getSettings(
            @AuthenticationPrincipal UserPrincipal principal) {
        ReminderSettingsResponse settings = reminderService.getSettings(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(settings));
    }

    @Operation(summary = "配置提醒设置")
    @PutMapping("/config")
    public ResponseEntity<ApiResponse<PlanResponse>> configReminder(
            @Valid @RequestBody ReminderConfigRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {
        PlanResponse response = reminderService.configReminder(principal.getUserId(), request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取提醒历史")
    @GetMapping("/history")
    public ResponseEntity<ApiResponse<List<Reminder>>> getReminderHistory(
            @AuthenticationPrincipal UserPrincipal principal) {
        List<Reminder> history = reminderService.getReminderHistory(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(history));
    }
}
