package com.prepkeeper.service.scheduler;

import com.prepkeeper.entity.StudyPlan;
import com.prepkeeper.repository.StudyPlanRepository;
import com.prepkeeper.service.ReminderService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 每日提醒定时任务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DailyReminderScheduler {

    private final StudyPlanRepository planRepository;
    private final ReminderService reminderService;

    /**
     * 温柔模式提醒 - 每天22:00
     */
    @Scheduled(cron = "0 0 22 * * ?")
    public void gentleReminder() {
        log.info("开始执行温柔模式提醒任务...");

        List<StudyPlan> plans = planRepository.findAllActivePlansWithReminder().stream()
                .filter(p -> p.getCurrentMode() == 1)
                .toList();

        for (StudyPlan plan : plans) {
            try {
                String content = reminderService.generateAndSendReminder(
                        plan.getUserId(), plan.getPlanId(), plan.getCurrentMode());
                if (content != null) {
                    log.info("温柔提醒已发送: userId={}, planId={}", plan.getUserId(), plan.getPlanId());
                }
            } catch (Exception e) {
                log.error("温柔提醒发送失败: planId={}, error={}", plan.getPlanId(), e.getMessage());
            }
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
            try {
                String content = reminderService.generateAndSendReminder(
                        plan.getUserId(), plan.getPlanId(), plan.getCurrentMode());
                if (content != null) {
                    log.info("强化提醒已发送: userId={}, planId={}", plan.getUserId(), plan.getPlanId());
                }
            } catch (Exception e) {
                log.error("强化提醒发送失败: planId={}, error={}", plan.getPlanId(), e.getMessage());
            }
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
            try {
                String content = reminderService.generateAndSendReminder(
                        plan.getUserId(), plan.getPlanId(), plan.getCurrentMode());
                if (content != null) {
                    log.info("唐僧提醒已发送: userId={}, planId={}", plan.getUserId(), plan.getPlanId());
                }
            } catch (Exception e) {
                log.error("唐僧提醒发送失败: planId={}, error={}", plan.getPlanId(), e.getMessage());
            }
        }

        log.info("唐僧模式提醒任务完成，处理{}个计划", plans.size());
    }
}
