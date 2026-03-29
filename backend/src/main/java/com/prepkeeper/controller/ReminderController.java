package com.prepkeeper.controller;

import com.prepkeeper.dto.request.ReminderConfigRequest;
import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.dto.response.PlanResponse;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.ReminderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Tag(name = "提醒接口", description = "提醒设置管理")
@RestController
@RequestMapping("/api/reminders")
@RequiredArgsConstructor
public class ReminderController {

    private final ReminderService reminderService;

    @Operation(summary = "配置提醒设置")
    @PutMapping("/config")
    public ResponseEntity<ApiResponse<PlanResponse>> configReminder(
            @Valid @RequestBody ReminderConfigRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {

        PlanResponse response = reminderService.configReminder(principal.getUserId(), request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}