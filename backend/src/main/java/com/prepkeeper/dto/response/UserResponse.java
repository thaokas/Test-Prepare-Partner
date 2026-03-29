package com.prepkeeper.dto.response;

import lombok.Builder;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Builder
public class UserResponse {

    private String userId;
    private String nickname;
    private String email;
    private String avatarUrl;
    private Integer totalCheckins;
    private Integer currentStreak;
    private Integer maxStreak;
    private LocalDateTime createdAt;
}