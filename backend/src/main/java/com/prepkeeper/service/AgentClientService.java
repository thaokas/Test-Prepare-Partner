package com.prepkeeper.service;

import com.prepkeeper.dto.request.PlanCreateRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class AgentClientService {

    @Value("${agent.service.url}")
    private String agentUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * 调用Agent处理打卡 — POST /api/checkin/
     */
    public Map<String, Object> processCheckin(String completedContent, BigDecimal overallCompletionRate, String imageUrl) {
        String url = agentUrl + "/api/checkin/";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("completed_content", completedContent);
        requestBody.put("overall_completion_rate", overallCompletionRate);
        requestBody.put("image_url", imageUrl);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent处理打卡失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 调用Agent生成计划(一次性) — POST /api/plan/generate
     */
    public Map<String, Object> generatePlan(String userId, PlanCreateRequest request) {
        String url = agentUrl + "/api/plan/generate";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("exam_name", request.getExamName());
        requestBody.put("exam_type", request.getExamType());
        requestBody.put("exam_date", request.getExamDate().toString());
        requestBody.put("daily_hours", request.getDailyHours());
        requestBody.put("foundation_level", request.getFoundationLevel());
        requestBody.put("weak_subjects", request.getWeakSubjects());

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent生成计划失败: {}", e.getMessage());
            throw new RuntimeException("Agent服务异常: " + e.getMessage());
        }
    }

    /**
     * 对话式计划生成 — POST /api/plan/chat
     */
    public Map<String, Object> planChat(String userId, String message, String threadId,
                                         List<String> urls, List<String> pdfUrls, List<String> imageUrls) {
        String url = agentUrl + "/api/plan/chat";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("message", message);
        requestBody.put("thread_id", threadId);
        requestBody.put("urls", urls != null ? urls : List.of());
        requestBody.put("pdf_urls", pdfUrls != null ? pdfUrls : List.of());
        requestBody.put("image_urls", imageUrls != null ? imageUrls : List.of());

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent对话计划失败: {}", e.getMessage());
            throw new RuntimeException("Agent服务异常: " + e.getMessage());
        }
    }

    /**
     * 调用Agent生成提醒文案 — POST /api/reminder/generate
     */
    public Map<String, Object> generateReminder(List<Map<String, Object>> todayTotalTasks,
                                                 List<Map<String, Object>> todayIncompleteTasks,
                                                 List<Map<String, Object>> examTotalTasks,
                                                 List<Map<String, Object>> examCompletedTasks,
                                                 double elapsedStudyDays,
                                                 double totalStudyDays,
                                                 String strictnessMode) {
        String url = agentUrl + "/api/reminder/generate";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("today_total_tasks", todayTotalTasks);
        requestBody.put("today_incomplete_tasks", todayIncompleteTasks);
        requestBody.put("exam_total_tasks", examTotalTasks);
        requestBody.put("exam_completed_tasks", examCompletedTasks);
        requestBody.put("elapsed_study_days", elapsedStudyDays);
        requestBody.put("total_study_days", totalStudyDays);
        requestBody.put("strictness_mode", strictnessMode);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent生成提醒失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 调用Agent生成周报 — POST /api/report/weekly
     */
    public Map<String, Object> generateWeeklyReport(String userId, String weekStart, String weekEnd,
                                                     List<Map<String, Object>> totalPlan,
                                                     List<Map<String, Object>> weeklyCompleted) {
        String url = agentUrl + "/api/report/weekly";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("week_start", weekStart);
        requestBody.put("week_end", weekEnd);
        requestBody.put("total_plan", totalPlan != null ? totalPlan : List.of());
        requestBody.put("weekly_completed", weeklyCompleted != null ? weeklyCompleted : List.of());

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent生成周报失败: {}", e.getMessage());
            throw new RuntimeException("Agent服务异常: " + e.getMessage());
        }
    }

    /**
     * 获取Agent端提醒设置 — GET /api/reminder/settings/{userId}
     */
    public Map<String, Object> getReminderSettingsFromAgent(String userId) {
        String url = agentUrl + "/api/reminder/settings/" + userId;

        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            return response;
        } catch (Exception e) {
            log.error("获取Agent提醒设置失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 更新Agent端提醒设置 — PUT /api/reminder/settings/{userId}
     */
    public Map<String, Object> updateReminderSettingsInAgent(String userId, int mode,
                                                              List<String> customTimes, int monkingInterval) {
        String url = agentUrl + "/api/reminder/settings/" + userId;

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("mode", mode);
        requestBody.put("custom_times", customTimes != null ? customTimes : List.of());
        requestBody.put("monking_interval", monkingInterval);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.exchange(url, HttpMethod.PUT, entity,
                    new ParameterizedTypeReference<Map<String, Object>>() {}).getBody();
            return response;
        } catch (Exception e) {
            log.error("更新Agent提醒设置失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * LLM代理 — POST /api/plan/llm/chat
     */
    public Map<String, Object> llmChat(List<Map<String, String>> messages, String systemPrompt) {
        String url = agentUrl + "/api/plan/llm/chat";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("messages", messages != null ? messages : List.of());
        requestBody.put("system_prompt", systemPrompt != null ? systemPrompt : "");

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("LLM代理调用失败: {}", e.getMessage());
            throw new RuntimeException("Agent服务异常: " + e.getMessage());
        }
    }

    /**
     * 网络搜索代理 — POST /api/plan/search
     */
    public Map<String, Object> search(String query) {
        String url = agentUrl + "/api/plan/search";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("query", query);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("搜索代理调用失败: {}", e.getMessage());
            return Map.of("results", List.of(), "error", e.getMessage());
        }
    }

    /**
     * strictness_mode映射: 后端整数模式 → Agent字符串模式
     */
    public static String modeToStrictness(int mode) {
        return switch (mode) {
            case 0 -> "silent";
            case 1 -> "gentle";
            case 2 -> "intensive";
            case 3 -> "tangseng";
            default -> "gentle";
        };
    }
}
