package com.prepkeeper.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.prepkeeper.dto.request.PlanCreateRequest;
import com.prepkeeper.dto.response.PlanResponse;
import com.prepkeeper.entity.StudyPlan;
import com.prepkeeper.exception.BusinessException;
import com.prepkeeper.exception.ErrorCode;
import com.prepkeeper.repository.StudyPlanRepository;
import com.prepkeeper.repository.TaskRepository;
import com.prepkeeper.util.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class PlanService {

    private final StudyPlanRepository planRepository;
    private final TaskRepository taskRepository;
    private final AgentClientService agentClient;
    private final ObjectMapper objectMapper;

    @Transactional
    public PlanResponse createPlan(String userId, PlanCreateRequest request) {
        // 计算阶段
        int phase = calculatePhase(request.getExamDate());

        // 创建计划
        StudyPlan plan = new StudyPlan();
        plan.setPlanId(IdGenerator.generatePlanId());
        plan.setUserId(userId);
        plan.setExamName(request.getExamName());
        plan.setExamType(request.getExamType());
        plan.setExamDate(request.getExamDate());
        plan.setDailyHours(request.getDailyHours());
        plan.setFoundationLevel(request.getFoundationLevel());
        plan.setWeakSubjects(toJsonString(request.getWeakSubjects()));
        plan.setCurrentMode(request.getCurrentMode());
        plan.setCurrentPhase(phase);
        plan.setPlanStatus(0);

        plan = planRepository.save(plan);

        // 调用Agent生成任务
        try {
            agentClient.generatePlan(userId, plan.getPlanId(), request);
        } catch (Exception e) {
            log.warn("Agent生成任务失败，计划已创建: {}", e.getMessage());
        }

        return toPlanResponse(plan, 0L, 0L);
    }

    @Transactional(readOnly = true)
    public PlanResponse getPlanById(String planId, String userId) {
        StudyPlan plan = planRepository.findByPlanIdAndUserId(planId, userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PLAN_NOT_FOUND));

        long totalTasks = taskRepository.countByPlanId(planId);
        long completedTasks = taskRepository.countCompletedByPlanId(planId);

        return toPlanResponse(plan, totalTasks, completedTasks);
    }

    @Transactional(readOnly = true)
    public List<PlanResponse> getUserPlans(String userId) {
        List<StudyPlan> plans = planRepository.findByUserId(userId);
        return plans.stream()
                .map(plan -> {
                    long total = taskRepository.countByPlanId(plan.getPlanId());
                    long completed = taskRepository.countCompletedByPlanId(plan.getPlanId());
                    return toPlanResponse(plan, total, completed);
                })
                .collect(Collectors.toList());
    }

    @Transactional
    public PlanResponse updateMode(String planId, String userId, Integer mode) {
        StudyPlan plan = planRepository.findByPlanIdAndUserId(planId, userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PLAN_NOT_FOUND));

        plan.setCurrentMode(mode);
        plan = planRepository.save(plan);

        long totalTasks = taskRepository.countByPlanId(planId);
        long completedTasks = taskRepository.countCompletedByPlanId(planId);

        return toPlanResponse(plan, totalTasks, completedTasks);
    }

    @Transactional
    public void deletePlan(String planId, String userId) {
        StudyPlan plan = planRepository.findByPlanIdAndUserId(planId, userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PLAN_NOT_FOUND));

        plan.setPlanStatus(2); // 标记为暂停
        planRepository.save(plan);
    }

    private int calculatePhase(LocalDate examDate) {
        long daysRemaining = ChronoUnit.DAYS.between(LocalDate.now(), examDate);
        if (daysRemaining > 90) {
            return 1; // 基础阶段
        } else if (daysRemaining >= 45) {
            return 2; // 强化阶段
        } else {
            return 3; // 冲刺阶段
        }
    }

    private String toJsonString(List<String> list) {
        if (list == null || list.isEmpty()) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(list);
        } catch (JsonProcessingException e) {
            return null;
        }
    }

    private PlanResponse toPlanResponse(StudyPlan plan, long totalTasks, long completedTasks) {
        double completionRate = totalTasks > 0 ? (double) completedTasks / totalTasks * 100 : 0;
        List<String> weakSubjects = parseJsonToList(plan.getWeakSubjects());

        return PlanResponse.builder()
                .planId(plan.getPlanId())
                .userId(plan.getUserId())
                .examName(plan.getExamName())
                .examType(plan.getExamType())
                .examDate(plan.getExamDate())
                .dailyHours(plan.getDailyHours())
                .foundationLevel(plan.getFoundationLevel())
                .weakSubjects(weakSubjects)
                .currentMode(plan.getCurrentMode())
                .planStatus(plan.getPlanStatus())
                .currentPhase(plan.getCurrentPhase())
                .createdAt(plan.getCreatedAt())
                .totalTasks(totalTasks)
                .completedTasks(completedTasks)
                .completionRate(completionRate)
                .build();
    }

    private List<String> parseJsonToList(String json) {
        if (json == null || json.isEmpty()) {
            return null;
        }
        try {
            return objectMapper.readValue(json, List.class);
        } catch (JsonProcessingException e) {
            return null;
        }
    }
}