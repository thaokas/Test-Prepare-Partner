package com.prepkeeper.service;

import com.prepkeeper.dto.request.PlanCreateRequest;
import com.prepkeeper.dto.response.CheckinResponse;
import com.prepkeeper.dto.response.EasterEggResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class AgentClientService {

    @Value("${agent.service.url}")
    private String agentUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * 调用Agent生成计划
     */
    public Map<String, Object> generatePlan(String userId, String planId, PlanCreateRequest request) {
        String url = agentUrl + "/api/plan/generate";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("plan_id", planId);
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
     * 调用Agent处理打卡
     */
    public CheckinAgentResponse processCheckin(String userId, String planId, String content, BigDecimal completionRate) {
        String url = agentUrl + "/api/checkin";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("plan_id", planId);
        requestBody.put("content", content);
        requestBody.put("completion_rate", completionRate);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);

            if (response != null) {
                CheckinAgentResponse result = new CheckinAgentResponse();
                result.setEncouragement((String) response.get("encouragement"));

                @SuppressWarnings("unchecked")
                Map<String, Object> eggData = (Map<String, Object>) response.get("easter_egg");
                if (eggData != null) {
                    EasterEggResponse egg = EasterEggResponse.builder()
                            .eggType((String) eggData.get("egg_type"))
                            .content((String) eggData.get("content"))
                            .triggerDate(null)
                            .build();
                    result.setEasterEgg(egg);
                }

                return result;
            }
            return null;
        } catch (Exception e) {
            log.error("调用Agent处理打卡失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 调用Agent生成周报
     */
    public Map<String, Object> generateWeeklyReport(String userId) {
        String url = agentUrl + "/api/report/weekly?user_id=" + userId;

        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent生成周报失败: {}", e.getMessage());
            throw new RuntimeException("Agent服务异常: " + e.getMessage());
        }
    }

    /**
     * 调用Agent进行对话
     */
    public Map<String, Object> chat(String userId, String message) {
        String url = agentUrl + "/api/chat";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("message", message);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent对话失败: {}", e.getMessage());
            throw new RuntimeException("Agent服务异常: " + e.getMessage());
        }
    }

    /**
     * 调用Agent发送提醒
     */
    public Map<String, Object> triggerReminder(String userId, String planId, Integer reminderType) {
        String url = agentUrl + "/api/reminder/trigger";

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("plan_id", planId);
        requestBody.put("reminder_type", reminderType);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, entity, Map.class);
            return response;
        } catch (Exception e) {
            log.error("调用Agent提醒失败: {}", e.getMessage());
            return null;
        }
    }

    @lombok.Data
    public static class CheckinAgentResponse {
        private String encouragement;
        private EasterEggResponse easterEgg;
    }
}