package com.prepkeeper.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 用户实体
 */
@Data
@Entity
@Table(name = "users")
public class User {

    @Id
    @Column(name = "user_id", length = 64)
    private String userId;

    @Column(name = "nickname", length = 50)
    private String nickname;

    @Column(name = "password", length = 256)
    private String password;

    @Column(name = "email", length = 100, unique = true)
    private String email;

    @Column(name = "avatar_url", length = 500)
    private String avatarUrl;

    @Column(name = "total_checkins")
    private Integer totalCheckins = 0;

    @Column(name = "current_streak")
    private Integer currentStreak = 0;

    @Column(name = "max_streak")
    private Integer maxStreak = 0;

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