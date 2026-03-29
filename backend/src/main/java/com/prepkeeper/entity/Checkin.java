package com.prepkeeper.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 打卡记录实体
 */
@Data
@Entity
@Table(name = "checkins")
public class Checkin {

    @Id
    @Column(name = "checkin_id", length = 64)
    private String checkinId;

    @Column(name = "user_id", length = 64, nullable = false)
    private String userId;

    @Column(name = "plan_id", length = 64, nullable = false)
    private String planId;

    @Column(name = "checkin_date", nullable = false)
    private LocalDate checkinDate;

    @Column(name = "completed_tasks")
    private Integer completedTasks = 0;

    @Column(name = "total_tasks")
    private Integer totalTasks = 0;

    @Column(name = "completion_rate", precision = 5, scale = 2)
    private BigDecimal completionRate = BigDecimal.ZERO;

    /**
     * 是否为补卡: 0-否 1-是
     */
    @Column(name = "is_makeup")
    private Integer isMakeup = 0;

    /**
     * 是否中断连续: 0-否 1-是
     */
    @Column(name = "streak_broken")
    private Integer streakBroken = 0;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}