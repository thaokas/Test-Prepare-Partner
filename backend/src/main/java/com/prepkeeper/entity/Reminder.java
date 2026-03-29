package com.prepkeeper.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 提醒记录实体
 */
@Data
@Entity
@Table(name = "reminders")
public class Reminder {

    @Id
    @Column(name = "reminder_id", length = 64)
    private String reminderId;

    @Column(name = "user_id", length = 64, nullable = false)
    private String userId;

    @Column(name = "plan_id", length = 64, nullable = false)
    private String planId;

    /**
     * 提醒类型: 1-每日提醒 2-催更提醒 3-周报提醒
     */
    @Column(name = "reminder_type", nullable = false)
    private Integer reminderType;

    @Column(name = "trigger_time", nullable = false)
    private LocalDateTime triggerTime;

    @Column(name = "content", length = 1000)
    private String content;

    /**
     * 是否已发送: 0-否 1-是
     */
    @Column(name = "is_sent")
    private Integer isSent = 0;

    @Column(name = "sent_at")
    private LocalDateTime sentAt;
}