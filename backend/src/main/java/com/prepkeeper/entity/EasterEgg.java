package com.prepkeeper.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDate;

/**
 * 彩蛋触发记录实体
 */
@Data
@Entity
@Table(name = "easter_eggs")
public class EasterEgg {

    @Id
    @Column(name = "record_id", length = 64)
    private String recordId;

    @Column(name = "user_id", length = 64, nullable = false)
    private String userId;

    /**
     * 彩蛋类型: late_night/weekend/early_bird/random
     */
    @Column(name = "egg_type", length = 50, nullable = false)
    private String eggType;

    @Column(name = "trigger_date", nullable = false)
    private LocalDate triggerDate;

    @Column(name = "content", length = 500)
    private String content;

    /**
     * 是否已触发: 0-否 1-是
     */
    @Column(name = "is_triggered")
    private Integer isTriggered = 0;
}