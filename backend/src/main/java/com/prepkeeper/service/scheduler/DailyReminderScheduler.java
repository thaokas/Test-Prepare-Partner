package com.prepkeeper.service.scheduler;

import com.prepkeeper.entity.StudyPlan;
import com.prepkeeper.repository.StudyPlanRepository;
import com.prepkeeper.repository.TaskRepository;
import com.prepkeeper.service.AgentClientService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.List;

/**
 * 每日提醒定时任务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DailyReminderScheduler {

    private final StudyPlanRepository planRepository;
    private final TaskRepository taskRepository;
    private final AgentClientService agentClient;

    /**
     * 温柔模式提醒 - 每天22:00
     */
    @Scheduled(cron = "0 0 22 * * ?")
    public void gentleReminder() {
        log.info("开始执行温柔模式提醒任务...");

        // 查询温柔模式(1)的活跃计划
        List<StudyPlan> plans = planRepository.findAllActivePlansWithReminder().stream()
                .filter(p -> p.getCurrentMode() == 1)
                .toList();

        for (StudyPlan plan : plans) {
            sendReminderIfNeeded(plan, 1);
        }

        log.info("温柔模式提醒任务完成，处理{}个计划", plans.size());
    }

    /**
     * 强化模式提醒 - 每天21:00和22:00
     */
    @Scheduled(cron = "0 0 21,22 * * ?")
    public void enhancedReminder() {
        log.info("开始执行强化模式提醒任务...");

        List<StudyPlan> plans = planRepository.findAllActivePlansWithReminder().stream()
                .filter(p -> p.getCurrentMode() == 2)
                .toList();

        for (StudyPlan plan : plans) {
            sendReminderIfNeeded(plan, 2);
        }

        log.info("强化模式提醒任务完成，处理{}个计划", plans.size());
    }

    /**
     * 唐僧模式提醒 - 21:00起每30分钟
     */
    @Scheduled(cron = "0 0/30 21-23 * * ?")
    public void monkReminder() {
        log.info("开始执行唐僧模式提醒任务...");

        List<StudyPlan> plans = planRepository.findAllActivePlansWithReminder().stream()
                .filter(p -> p.getCurrentMode() == 3)
                .toList();

        for (StudyPlan plan : plans) {
            sendReminderIfNeeded(plan, 3);
        }

        log.info("唐僧模式提醒任务完成，处理{}个计划", plans.size());
    }

    /**
     * 发送提醒（如果今日任务未完成）
     */
    private void sendReminderIfNeeded(StudyPlan plan, Integer reminderType) {
        try {
            // 检查今日是否有未完成任务
            long totalToday = taskRepository.countTodayTotal(plan.getPlanId(), LocalDate.now());
            long completedToday = taskRepository.countTodayCompleted(plan.getPlanId(), LocalDate.now());

            if (completedToday < totalToday) {
                // 有未完成任务，发送提醒
                agentClient.triggerReminder(plan.getUserId(), plan.getPlanId(), reminderType);
                log.info("发送提醒: userId={}, planId={}, mode={}", plan.getUserId(), plan.getPlanId(), reminderType);
            }
        } catch (Exception e) {
            log.error("发送提醒失败: planId={}, error={}", plan.getPlanId(), e.getMessage());
        }
    }
}