package com.prepkeeper.dto.response;

import lombok.Builder;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
public class PlanResponse {

    private String planId;
    private String userId;
    private String examName;
    private String examType;
    private LocalDate examDate;
    private BigDecimal dailyHours;
    private Integer foundationLevel;
    private List<String> weakSubjects;
    private Integer currentMode;
    private Integer planStatus;
    private Integer currentPhase;
    private LocalDateTime createdAt;

    /**
     * 总任务数
     */
    private Long totalTasks;

    /**
     * 已完成任务数
     */
    private Long completedTasks;

    /**
     * 完成率
     */
    private Double completionRate;
}