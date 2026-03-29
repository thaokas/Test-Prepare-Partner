package com.prepkeeper.service.scheduler;

import com.prepkeeper.entity.StudyPlan;
import com.prepkeeper.repository.StudyPlanRepository;
import com.prepkeeper.service.AgentClientService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 周报生成定时任务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class WeeklyReportScheduler {

    private final StudyPlanRepository planRepository;
    private final AgentClientService agentClient;

    /**
     * 每周日22:00生成周报
     */
    @Scheduled(cron = "0 0 22 ? * SUN")
    public void generateWeeklyReports() {
        log.info("开始生成周报...");

        // 获取所有活跃计划
        List<StudyPlan> activePlans = planRepository.findActivePlansByUserId(null);

        for (StudyPlan plan : activePlans) {
            try {
                agentClient.generateWeeklyReport(plan.getUserId());
                log.info("周报生成成功: userId={}", plan.getUserId());
            } catch (Exception e) {
                log.error("周报生成失败: userId={}, error={}", plan.getUserId(), e.getMessage());
            }
        }

        log.info("周报生成任务完成");
    }
}