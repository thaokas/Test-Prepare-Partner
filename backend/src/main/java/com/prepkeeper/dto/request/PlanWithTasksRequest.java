package com.prepkeeper.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class PlanWithTasksRequest {

    @NotBlank(message = "考试名称不能为空")
    @Size(max = 100)
    private String examName;

    @NotBlank(message = "考试类型不能为空")
    @Size(max = 64)
    private String examType;

    @NotBlank(message = "考试日期不能为空")
    private String examDate;

    private Double dailyHours;

    private Integer foundationLevel;

    private List<String> weakSubjects;

    private Integer currentMode = 0;

    @NotNull(message = "任务列表不能为空")
    private List<Map<String, Object>> tasks;
}
