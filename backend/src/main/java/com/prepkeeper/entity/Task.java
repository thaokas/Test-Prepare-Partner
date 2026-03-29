package com.prepkeeper.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 任务实体
 */
@Data
@Entity
@Table(name = "tasks")
public class Task {

    @Id
    @Column(name = "task_id", length = 64)
    private String taskId;

    @Column(name = "plan_id", length = 64, nullable = false)
    private String planId;

    @Column(name = "task_date", nullable = false)
    private LocalDate taskDate;

    @Column(name = "subject", length = 50, nullable = false)
    private String subject;

    @Column(name = "task_content", length = 500, nullable = false)
    private String taskContent;

    @Column(name = "estimated_minutes")
    private Integer estimatedMinutes;

    /**
     * 任务类型: 1-学习 2-复习 3-刷题 4-模考
     */
    @Column(name = "task_type")
    private Integer taskType = 1;

    /**
     * 所属阶段: 1-基础 2-强化 3-冲刺
     */
    @Column(name = "phase", nullable = false)
    private Integer phase;

    /**
     * 状态: 0-未开始 1-进行中 2-已完成 3-已跳过
     */
    @Column(name = "status")
    private Integer status = 0;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    /**
     * 打卡方式: 1-文字 2-图片
     */
    @Column(name = "checkin_type")
    private Integer checkinType;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}