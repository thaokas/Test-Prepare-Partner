package com.prepkeeper.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import java.util.List;

@Data
public class CheckinRequest {

    @NotBlank(message = "计划ID不能为空")
    private String planId;

    /**
     * 今日完成的计划内容描述（完成内容）
     */
    private String content;

    /**
     * 打卡截图/图片URL，传入则先由多模态模型总结
     */
    private String imageUrl;

    /**
     * 打卡方式: 1-文字 2-图片
     */
    @Min(value = 1, message = "打卡方式值为1或2")
    @Max(value = 2, message = "打卡方式值为1或2")
    private Integer checkinType = 1;

    /**
     * 指定完成的任务ID列表(可选，不填则标记今日所有任务完成)
     */
    private List<String> taskIds;
}