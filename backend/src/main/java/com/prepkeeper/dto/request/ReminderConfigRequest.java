package com.prepkeeper.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ReminderConfigRequest {

    @NotBlank(message = "计划ID不能为空")
    private String planId;

    /**
     * 监督模式: 0-静默 1-温柔 2-强化 3-唐僧
     */
    @Min(value = 0, message = "监督模式值为0-3")
    @Max(value = 3, message = "监督模式值为0-3")
    private Integer currentMode;
}