package com.prepkeeper.dto.response;

import lombok.Builder;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
public class TaskResponse {

    private String taskId;
    private String planId;
    private LocalDate taskDate;
    private String subject;
    private String taskContent;
    private Integer estimatedMinutes;
    private Integer taskType;
    private Integer phase;
    private Integer status;
    private LocalDateTime completedAt;
    private Integer checkinType;
}