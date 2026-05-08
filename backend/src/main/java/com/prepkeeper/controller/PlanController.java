package com.prepkeeper.controller;

import com.prepkeeper.dto.request.PlanChatRequest;
import com.prepkeeper.dto.request.PlanCreateRequest;
import com.prepkeeper.dto.response.ApiResponse;
import com.prepkeeper.dto.response.PlanChatResponse;
import com.prepkeeper.dto.response.PlanResponse;
import com.prepkeeper.security.UserPrincipal;
import com.prepkeeper.service.PlanService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Tag(name = "计划接口", description = "备考计划管理")
@RestController
@RequestMapping("/api/plans")
@RequiredArgsConstructor
public class PlanController {

    private final PlanService planService;

    @Operation(summary = "创建计划")
    @PostMapping
    public ResponseEntity<ApiResponse<PlanResponse>> createPlan(
            @Valid @RequestBody PlanCreateRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {

        PlanResponse response = planService.createPlan(principal.getUserId(), request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "对话式计划生成")
    @PostMapping("/chat")
    public ResponseEntity<ApiResponse<PlanChatResponse>> planChat(
            @Valid @RequestBody PlanChatRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {

        PlanChatResponse response = planService.planChat(principal.getUserId(), request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取计划详情")
    @GetMapping("/{planId}")
    public ResponseEntity<ApiResponse<PlanResponse>> getPlan(
            @PathVariable String planId,
            @AuthenticationPrincipal UserPrincipal principal) {

        PlanResponse response = planService.getPlanById(planId, principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取用户计划列表")
    @GetMapping("/user/{userId}")
    public ResponseEntity<ApiResponse<List<PlanResponse>>> getUserPlans(
            @PathVariable String userId,
            @AuthenticationPrincipal UserPrincipal principal) {

        if (!principal.getUserId().equals(userId)) {
            return ResponseEntity.status(403).build();
        }

        List<PlanResponse> response = planService.getUserPlans(userId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "更新计划")
    @PutMapping("/{planId}")
    public ResponseEntity<ApiResponse<PlanResponse>> updatePlan(
            @PathVariable String planId,
            @RequestBody PlanCreateRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {

        // 暂不支持直接更新，需要删除重建
        return ResponseEntity.badRequest().build();
    }

    @Operation(summary = "切换监督模式")
    @PutMapping("/{planId}/mode")
    public ResponseEntity<ApiResponse<PlanResponse>> updateMode(
            @PathVariable String planId,
            @RequestParam Integer mode,
            @AuthenticationPrincipal UserPrincipal principal) {

        PlanResponse response = planService.updateMode(planId, principal.getUserId(), mode);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "删除计划")
    @DeleteMapping("/{planId}")
    public ResponseEntity<ApiResponse<Void>> deletePlan(
            @PathVariable String planId,
            @AuthenticationPrincipal UserPrincipal principal) {

        planService.deletePlan(planId, principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(null));
    }
}