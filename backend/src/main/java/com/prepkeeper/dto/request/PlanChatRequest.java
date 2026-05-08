package com.prepkeeper.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import java.util.List;

@Data
public class PlanChatRequest {

    @NotBlank(message = "消息不能为空")
    private String message;

    /** 续聊时传入已有thread_id，新对话传null */
    private String threadId;

    /** 参考资料网页URL */
    private List<String> urls;

    /** PDF资料URL */
    private List<String> pdfUrls;

    /** 图片资料URL */
    private List<String> imageUrls;
}
