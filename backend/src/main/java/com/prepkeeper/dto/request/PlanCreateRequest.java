package com.prepkeeper.dto.request;

import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Data
public class PlanCreateRequest {

    @NotBlank(message = "考试名称不能为空")
    @Size(max = 100, message = "考试名称最长100字符")
    private String examName;

    @NotBlank(message = "考试类型不能为空")
    @Size(max = 64, message = "考试类型最长64字符")
    private String examType;

    @NotNull(message = "考试日期不能为空")
    @Future(message = "考试日期必须是未来日期")
    private LocalDate examDate;

    @NotNull(message = "每日学习时长不能为空")
    @DecimalMin(value = "0.5", message = "每日学习时长至少0.5小时")
    @DecimalMax(value = "12.0", message = "每日学习时长最多12小时")
    private BigDecimal dailyHours;

    /**
     * 基础水平: 0-零基础 1-有一定基础 2-已复习一轮
     */
    @Min(value = 0, message = "基础水平值为0-2")
    @Max(value = 2, message = "基础水平值为0-2")
    private Integer foundationLevel = 1;

    /**
     * 薄弱科目列表
     */
    private List<String> weakSubjects;

    /**
     * 监督模式: 0-静默 1-温柔 2-强化 3-唐僧
     */
    @Min(value = 0, message = "监督模式值为0-3")
    @Max(value = 3, message = "监督模式值为0-3")
    private Integer currentMode = 1;
}