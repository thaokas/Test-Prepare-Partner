package com.prepkeeper.dto.response;

import lombok.Builder;
import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
@Builder
public class PlanChatResponse {

    private String threadId;
    private String status;
    private String message;
    private String clarificationQuestion;
    private String planId;
    private List<Map<String, Object>> tasks;
}
