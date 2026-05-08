package com.prepkeeper.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.prepkeeper.dto.request.ReminderConfigRequest;
import com.prepkeeper.dto.response.PlanResponse;
import com.prepkeeper.dto.response.ReminderSettingsResponse;
import com.prepkeeper.entity.Reminder;
import com.prepkeeper.entity.ReminderSettings;
import com.prepkeeper.entity.StudyPlan;
import com.prepkeeper.entity.Task;
import com.prepkeeper.exception.BusinessException;
import com.prepkeeper.exception.ErrorCode;
import com.prepkeeper.repository.ReminderRepository;
import com.prepkeeper.repository.ReminderSettingsRepository;
import com.prepkeeper.repository.StudyPlanRepository;
import com.prepkeeper.repository.TaskRepository;
import com.prepkeeper.util.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ReminderService {

    private final ReminderSettingsRepository settingsRepository;
    private final ReminderRepository reminderRepository;
    private final StudyPlanRepository planRepository;
    private final TaskRepository taskRepository;
    private final AgentClientService agentClient;
    private final ObjectMapper objectMapper;

    @Transactional
    public PlanResponse configReminder(String userId, ReminderConfigRequest request) {
        StudyPlan plan = planRepository.findByPlanIdAndUserId(request.getPlanId(), userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PLAN_NOT_FOUND));

        plan.setCurrentMode(request.getMode());
        planRepository.save(plan);

        // 保存提醒设置
        ReminderSettings settings = settingsRepository.findById(userId)
                .orElseGet(() -> {
                    ReminderSettings s = new ReminderSettings();
                    s.setUserId(userId);
                    return s;
                });

        settings.setMode(request.getMode());
        if (request.getCustomTimes() != null) {
            settings.setCustomTimes(toJsonString(request.getCustomTimes()));
        }
        if (request.getMonkingInterval() != null) {
            settings.setMonkingInterval(request.getMonkingInterval());
        }
        settingsRepository.save(settings);

        long totalTasks = taskRepository.countByPlanId(plan.getPlanId());
        long completedTasks = taskRepository.countCompletedByPlanId(plan.getPlanId());

        return toPlanResponse(plan, totalTasks, completedTasks);
    }

    @Transactional(readOnly = true)
    public ReminderSettingsResponse getSettings(String userId) {
        ReminderSettings settings = settingsRepository.findById(userId)
                .orElse(null);

        if (settings == null) {
            return ReminderSettingsResponse.builder()
                    .mode(1)
                    .customTimes(List.of())
                    .monkingInterval(30)
                    .isActive(true)
                    .build();
        }

        return ReminderSettingsResponse.builder()
                .mode(settings.getMode())
                .customTimes(parseJsonToList(settings.getCustomTimes()))
                .monkingInterval(settings.getMonkingInterval())
                .isActive(settings.getIsActive())
                .build();
    }

    @Transactional(readOnly = true)
    public List<Reminder> getReminderList(String userId) {
        return reminderRepository.findByUserId(userId);
    }

    @Transactional(readOnly = true)
    public List<Reminder> getReminderHistory(String userId) {
        return reminderRepository.findByUserIdOrderByTriggerTimeDesc(userId);
    }

    /**
     * 生成并发送提醒 — 从DB查询任务数据，调用Agent生成文案，保存提醒记录
     */
    @Transactional
    public String generateAndSendReminder(String userId, String planId, Integer mode) {
        StudyPlan plan = planRepository.findById(planId).orElse(null);
        if (plan == null) {
            log.warn("计划不存在: planId={}", planId);
            return null;
        }

        LocalDate today = LocalDate.now();

        // 今日任务
        List<Task> todayTasks = taskRepository.findTodayTasks(planId, today);
        List<Map<String, Object>> todayTotalTasks = toTaskMaps(todayTasks);
        List<Map<String, Object>> todayIncompleteTasks = todayTasks.stream()
                .filter(t -> t.getStatus() != 2)
                .map(this::toTaskMap)
                .toList();

        // 全部任务
        List<Task> allTasks = taskRepository.findByPlanId(planId);
        List<Map<String, Object>> examTotalTasks = toTaskMaps(allTasks);
        List<Map<String, Object>> examCompletedTasks = allTasks.stream()
                .filter(t -> t.getStatus() == 2)
                .map(this::toTaskMap)
                .toList();

        // 计算学习天数
        long totalStudyDays = ChronoUnit.DAYS.between(plan.getExamDate(), today);
        if (totalStudyDays < 1) totalStudyDays = 1;
        long elapsedStudyDays = ChronoUnit.DAYS.between(plan.getCreatedAt().toLocalDate(), today);
        if (elapsedStudyDays < 0) elapsedStudyDays = 0;

        String strictnessMode = AgentClientService.modeToStrictness(mode);

        try {
            Map<String, Object> agentResponse = agentClient.generateReminder(
                    todayTotalTasks, todayIncompleteTasks,
                    examTotalTasks, examCompletedTasks,
                    elapsedStudyDays, totalStudyDays,
                    strictnessMode);

            String content = agentResponse != null ? (String) agentResponse.get("content") : null;

            // 保存提醒记录
            Reminder reminder = new Reminder();
            reminder.setReminderId(IdGenerator.generateReminderId());
            reminder.setUserId(userId);
            reminder.setPlanId(planId);
            reminder.setReminderType(1);
            reminder.setTriggerTime(LocalDateTime.now());
            reminder.setContent(content);
            reminder.setIsSent(content != null ? 1 : 0);
            if (content != null) {
                reminder.setSentAt(LocalDateTime.now());
            }
            reminderRepository.save(reminder);

            return content;
        } catch (Exception e) {
            log.error("生成提醒失败: userId={}, planId={}, error={}", userId, planId, e.getMessage());
            return null;
        }
    }

    private Map<String, Object> toTaskMap(Task task) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", task.getTaskId());
        map.put("subject", task.getSubject());
        map.put("name", task.getTaskContent());
        map.put("estimated_minutes", task.getEstimatedMinutes());
        map.put("task_date", task.getTaskDate() != null ? task.getTaskDate().toString() : null);
        return map;
    }

    private List<Map<String, Object>> toTaskMaps(List<Task> tasks) {
        return tasks.stream().map(this::toTaskMap).toList();
    }

    private PlanResponse toPlanResponse(StudyPlan plan, long totalTasks, long completedTasks) {
        double completionRate = totalTasks > 0 ? (double) completedTasks / totalTasks * 100 : 0;

        return PlanResponse.builder()
                .planId(plan.getPlanId())
                .userId(plan.getUserId())
                .examName(plan.getExamName())
                .examType(plan.getExamType())
                .examDate(plan.getExamDate())
                .dailyHours(plan.getDailyHours())
                .foundationLevel(plan.getFoundationLevel())
                .currentMode(plan.getCurrentMode())
                .planStatus(plan.getPlanStatus())
                .currentPhase(plan.getCurrentPhase())
                .createdAt(plan.getCreatedAt())
                .totalTasks(totalTasks)
                .completedTasks(completedTasks)
                .completionRate(completionRate)
                .build();
    }

    private String toJsonString(List<String> list) {
        if (list == null || list.isEmpty()) return "[]";
        try {
            return objectMapper.writeValueAsString(list);
        } catch (JsonProcessingException e) {
            return "[]";
        }
    }

    @SuppressWarnings("unchecked")
    private List<String> parseJsonToList(String json) {
        if (json == null || json.isEmpty()) return new ArrayList<>();
        try {
            return objectMapper.readValue(json, List.class);
        } catch (JsonProcessingException e) {
            return new ArrayList<>();
        }
    }
}
