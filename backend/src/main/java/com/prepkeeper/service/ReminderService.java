package com.prepkeeper.service;

import com.prepkeeper.dto.request.ReminderConfigRequest;
import com.prepkeeper.dto.response.PlanResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ReminderService {

    private final PlanService planService;

    @Transactional
    public PlanResponse configReminder(String userId, ReminderConfigRequest request) {
        return planService.updateMode(request.getPlanId(), userId, request.getCurrentMode());
    }
}