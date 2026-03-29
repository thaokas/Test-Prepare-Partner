package com.prepkeeper.controller;

import com.prepkeeper.dto.request.CheckinRequest;
import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.dto.response.CheckinResponse;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.CheckinService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@Tag(name = "打卡接口", description = "每日打卡管理")
@RestController
@RequestMapping("/api/checkins")
@RequiredArgsConstructor
public class CheckinController {

    private final CheckinService checkinService;

    @Operation(summary = "提交打卡")
    @PostMapping
    public ResponseEntity<ApiResponse<CheckinResponse>> checkin(
            @Valid @RequestBody CheckinRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {

        CheckinResponse response = checkinService.checkin(principal.getUserId(), request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取今日打卡记录")
    @GetMapping("/today")
    public ResponseEntity<ApiResponse<CheckinResponse>> getTodayCheckin(
            @RequestParam String planId,
            @AuthenticationPrincipal UserPrincipal principal) {

        // 查询今日打卡记录
        // 暂返回空
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @Operation(summary = "获取打卡历史")
    @GetMapping("/history")
    public ResponseEntity<ApiResponse<List<CheckinResponse>>> getCheckinHistory(
            @RequestParam(required = false) LocalDate startDate,
            @RequestParam(required = false) LocalDate endDate,
            @AuthenticationPrincipal UserPrincipal principal) {

        if (startDate == null) {
            startDate = LocalDate.now().minusDays(30);
        }
        if (endDate == null) {
            endDate = LocalDate.now();
        }

        List<CheckinResponse> response = checkinService.getCheckinHistory(principal.getUserId(), startDate, endDate);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取连续打卡天数")
    @GetMapping("/streak")
    public ResponseEntity<ApiResponse<Integer>> getStreak(
            @AuthenticationPrincipal UserPrincipal principal) {

        // 通过用户信息获取
        return ResponseEntity.ok(ApiResponse.success(0));
    }
}