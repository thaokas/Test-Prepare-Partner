package com.prepkeeper.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import java.util.List;

@Data
public class ReminderConfigRequest {

    @NotBlank(message = "计划ID不能为空")
    private String planId;

    /**
     * 监督模式: 0-静默 1-温柔 2-强化 3-唐僧
     */
    @Min(value = 0, message = "监督模式值为0-3")
    @Max(value = 3, message = "监督模式值为0-3")
    private Integer mode;

    /** 自定义提醒时间列表 ["09:00","14:00","20:00"] */
    private List<String> customTimes;

    /** 唐僧模式间隔（分钟，5-120） */
    @Min(value = 5, message = "唐僧模式间隔最少5分钟")
    @Max(value = 120, message = "唐僧模式间隔最多120分钟")
    private Integer monkingInterval = 30;
}