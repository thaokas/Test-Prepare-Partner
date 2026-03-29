package com.prepkeeper.service;

import com.prepkeeper.dto.request.CheckinRequest;
import com.prepkeeper.dto.response.CheckinResponse;
import com.prepkeeper.dto.response.EasterEggResponse;
import com.prepkeeper.entity.Checkin;
import com.prepkeeper.entity.StudyPlan;
import com.prepkeeper.exception.BusinessException;
import com.prepkeeper.exception.ErrorCode;
import com.prepkeeper.repository.CheckinRepository;
import com.prepkeeper.repository.StudyPlanRepository;
import com.prepkeeper.repository.TaskRepository;
import com.prepkeeper.util.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class CheckinService {

    private final CheckinRepository checkinRepository;
    private final StudyPlanRepository planRepository;
    private final TaskRepository taskRepository;
    private final UserService userService;
    private final AgentClientService agentClient;

    @Transactional
    public CheckinResponse checkin(String userId, CheckinRequest request) {
        // 验证计划
        StudyPlan plan = planRepository.findByPlanIdAndUserId(request.getPlanId(), userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PLAN_NOT_FOUND));

        LocalDate today = LocalDate.now();

        // 检查今日是否已打卡
        if (checkinRepository.existsByUserIdAndPlanIdAndCheckinDate(userId, request.getPlanId(), today)) {
            throw new BusinessException(4001, "今日已打卡");
        }

        // 获取今日任务
        long totalTasks = taskRepository.countTodayTotal(request.getPlanId(), today);
        long completedTasks;

        // 更新任务状态
        if (request.getTaskIds() != null && !request.getTaskIds().isEmpty()) {
            // 完成指定任务
            taskRepository.updateStatusByIds(request.getTaskIds(), 2);
            completedTasks = request.getTaskIds().size();
        } else {
            // 完成所有今日任务
            List<com.prepkeeper.entity.Task> todayTasks = taskRepository.findTodayTasks(request.getPlanId(), today);
            List<String> allTaskIds = todayTasks.stream()
                    .map(com.prepkeeper.entity.Task::getTaskId)
                    .toList();
            if (!allTaskIds.isEmpty()) {
                taskRepository.updateStatusByIds(allTaskIds, 2);
            }
            completedTasks = totalTasks;
        }

        // 计算完成率
        BigDecimal completionRate = totalTasks > 0
                ? BigDecimal.valueOf(completedTasks)
                        .divide(BigDecimal.valueOf(totalTasks), 4, RoundingMode.HALF_UP)
                        .multiply(BigDecimal.valueOf(100))
                : BigDecimal.ZERO;

        // 检查昨日是否打卡
        boolean checkedYesterday = checkinRepository.checkedYesterday(userId, today.minusDays(1));

        // 创建打卡记录
        Checkin checkin = new Checkin();
        checkin.setCheckinId(IdGenerator.generateCheckinId());
        checkin.setUserId(userId);
        checkin.setPlanId(request.getPlanId());
        checkin.setCheckinDate(today);
        checkin.setCompletedTasks((int) completedTasks);
        checkin.setTotalTasks((int) totalTasks);
        checkin.setCompletionRate(completionRate);
        checkin.setIsMakeup(0);
        checkin.setStreakBroken(checkedYesterday ? 0 : 1);

        checkinRepository.save(checkin);

        // 更新用户连续打卡
        userService.updateStreak(userId, checkedYesterday);

        // 获取当前连续打卡天数
        int currentStreak = userService.getUserById(userId).getCurrentStreak();

        // 调用Agent获取鼓励话术
        String encouragement = null;
        EasterEggResponse easterEgg = null;

        try {
            var agentResponse = agentClient.processCheckin(userId, request.getPlanId(), request.getContent(), completionRate);
            if (agentResponse != null) {
                encouragement = agentResponse.getEncouragement();
                if (agentResponse.getEasterEgg() != null) {
                    easterEgg = agentResponse.getEasterEgg();
                }
            }
        } catch (Exception e) {
            log.warn("Agent处理打卡失败: {}", e.getMessage());
            // 使用默认鼓励话术
            encouragement = getDefaultEncouragement(completionRate);
        }

        return CheckinResponse.builder()
                .checkinId(checkin.getCheckinId())
                .planId(checkin.getPlanId())
                .checkinDate(checkin.getCheckinDate())
                .completedTasks(checkin.getCompletedTasks())
                .totalTasks(checkin.getTotalTasks())
                .completionRate(checkin.getCompletionRate())
                .currentStreak(currentStreak)
                .encouragement(encouragement)
                .easterEgg(easterEgg)
                .build();
    }

    @Transactional(readOnly = true)
    public List<CheckinResponse> getCheckinHistory(String userId, LocalDate startDate, LocalDate endDate) {
        List<Checkin> checkins = checkinRepository.findByUserIdAndDateRange(userId, startDate, endDate);
        return checkins.stream()
                .map(c -> CheckinResponse.builder()
                        .checkinId(c.getCheckinId())
                        .planId(c.getPlanId())
                        .checkinDate(c.getCheckinDate())
                        .completedTasks(c.getCompletedTasks())
                        .totalTasks(c.getTotalTasks())
                        .completionRate(c.getCompletionRate())
                        .build())
                .toList();
    }

    private String getDefaultEncouragement(BigDecimal completionRate) {
        int rate = completionRate.intValue();
        if (rate == 100) {
            return "恭喜完成今日所有任务！继续保持！";
        } else if (rate >= 75) {
            return "太棒了！已经完成了大部分任务，再接再厉！";
        } else if (rate >= 50) {
            return "很好，已经完成了一半，继续加油！";
        } else if (rate >= 25) {
            return "迈出第一步就是胜利，明天继续！";
        } else {
            return "每一次努力都值得肯定，坚持下去！";
        }
    }
}