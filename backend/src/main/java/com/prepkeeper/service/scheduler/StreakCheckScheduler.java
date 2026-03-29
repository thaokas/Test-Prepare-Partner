package com.prepkeeper.service.scheduler;

import com.prepkeeper.entity.User;
import com.prepkeeper.repository.CheckinRepository;
import com.prepkeeper.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

/**
 * 连续打卡检查定时任务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class StreakCheckScheduler {

    private final UserRepository userRepository;
    private final CheckinRepository checkinRepository;

    /**
     * 每天00:05检查昨日打卡情况
     */
    @Scheduled(cron = "0 5 0 * * ?")
    @Transactional
    public void checkStreak() {
        log.info("开始检查连续打卡情况...");

        LocalDate yesterday = LocalDate.now().minusDays(1);

        // 获取所有有打卡记录的用户
        List<User> users = userRepository.findAll();

        int resetCount = 0;
        for (User user : users) {
            // 检查昨日是否打卡
            boolean checkedYesterday = checkinRepository.checkedYesterday(user.getUserId(), yesterday);

            if (!checkedYesterday && user.getCurrentStreak() > 0) {
                // 昨日未打卡，重置连续天数
                user.setCurrentStreak(0);
                userRepository.save(user);
                resetCount++;
                log.info("重置连续打卡: userId={}, previousStreak={}", user.getUserId(), user.getCurrentStreak());
            }
        }

        log.info("连续打卡检查完成，重置{}个用户", resetCount);
    }
}