package com.prepkeeper.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "reminder_settings")
public class ReminderSettings {

    @Id
    @Column(name = "user_id", length = 64)
    private String userId;

    /** 监督模式: 0-静默 1-温柔 2-强化 3-唐僧 */
    @Column(name = "mode")
    private Integer mode = 1;

    /** 自定义提醒时间，JSON数组 ["09:00","14:00","20:00"] */
    @Column(name = "custom_times", length = 500)
    private String customTimes;

    /** 唐僧模式间隔(分钟)，5-120 */
    @Column(name = "monking_interval")
    private Integer monkingInterval = 30;

    @Column(name = "is_active")
    private Boolean isActive = true;

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
