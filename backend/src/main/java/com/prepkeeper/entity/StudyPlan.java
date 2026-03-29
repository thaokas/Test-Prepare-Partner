package com.prepkeeper.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 备考计划实体
 */
@Data
@Entity
@Table(name = "study_plans")
public class StudyPlan {

    @Id
    @Column(name = "plan_id", length = 64)
    private String planId;

    @Column(name = "user_id", length = 64, nullable = false)
    private String userId;

    @Column(name = "exam_name", length = 100, nullable = false)
    private String examName;

    @Column(name = "exam_type", length = 64, nullable = false)
    private String examType;

    @Column(name = "exam_date", nullable = false)
    private LocalDate examDate;

    @Column(name = "daily_hours", precision = 3, scale = 1)
    private BigDecimal dailyHours;

    @Column(name = "foundation_level")
    private Integer foundationLevel = 1;

    @Column(name = "weak_subjects", length = 500)
    private String weakSubjects;

    /**
     * 监督模式: 0-静默 1-温柔 2-强化 3-唐僧
     */
    @Column(name = "current_mode")
    private Integer currentMode = 1;

    /**
     * 计划状态: 0-进行中 1-已完成 2-已暂停
     */
    @Column(name = "plan_status")
    private Integer planStatus = 0;

    /**
     * 当前阶段: 1-基础 2-强化 3-冲刺
     */
    @Column(name = "current_phase")
    private Integer currentPhase = 1;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}