package com.prepkeeper.service.scheduler;

import com.prepkeeper.entity.StudyPlan;
import com.prepkeeper.entity.Task;
import com.prepkeeper.repository.StudyPlanRepository;
import com.prepkeeper.repository.TaskRepository;
import com.prepkeeper.service.AgentClientService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.TemporalAdjusters;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 周报生成定时任务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class WeeklyReportScheduler {

    private final StudyPlanRepository planRepository;
    private final TaskRepository taskRepository;
    private final AgentClientService agentClient;

    /**
     * 每周日22:00生成周报
     */
    @Scheduled(cron = "0 0 22 ? * SUN")
    public void generateWeeklyReports() {
        log.info("开始生成周报...");

        LocalDate today = LocalDate.now();
        LocalDate weekStart = today.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
        LocalDate weekEnd = today.with(TemporalAdjusters.nextOrSame(DayOfWeek.SUNDAY));

        List<StudyPlan> activePlans = planRepository.findAllActivePlans();

        for (StudyPlan plan : activePlans) {
            try {
                // 查询本周任务
                List<Task> weekTasks = taskRepository.findByPlanIdAndTaskDateBetween(
                        plan.getPlanId(), weekStart, weekEnd);

                // 本周全部计划任务
                List<Map<String, Object>> totalPlan = weekTasks.stream()
                        .map(this::toTaskMap)
                        .toList();

                // 本周已完成任务
                List<Map<String, Object>> weeklyCompleted = weekTasks.stream()
                        .filter(t -> t.getStatus() == 2)
                        .map(this::toTaskMap)
                        .toList();

                agentClient.generateWeeklyReport(
                        plan.getUserId(),
                        weekStart.toString(),
                        weekEnd.toString(),
                        totalPlan,
                        weeklyCompleted);
                log.info("周报生成成功: userId={}, planId={}", plan.getUserId(), plan.getPlanId());
            } catch (Exception e) {
                log.error("周报生成失败: userId={}, planId={}, error={}",
                        plan.getUserId(), plan.getPlanId(), e.getMessage());
            }
        }

        log.info("周报生成任务完成，处理{}个计划", activePlans.size());
    }

    private Map<String, Object> toTaskMap(Task task) {
        Map<String, Object> map = new HashMap<>();
        map.put("task_date", task.getTaskDate() != null ? task.getTaskDate().toString() : null);
        map.put("subject", task.getSubject());
        map.put("estimated_minutes", task.getEstimatedMinutes());
        return map;
    }
}
