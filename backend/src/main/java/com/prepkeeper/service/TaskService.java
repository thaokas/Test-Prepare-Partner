package com.prepkeeper.service;

import com.prepkeeper.dto.response.TaskResponse;
import com.prepkeeper.entity.Task;
import com.prepkeeper.exception.BusinessException;
import com.prepkeeper.exception.ErrorCode;
import com.prepkeeper.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class TaskService {

    private final TaskRepository taskRepository;

    @Transactional(readOnly = true)
    public List<TaskResponse> getTodayTasks(String planId) {
        List<Task> tasks = taskRepository.findTodayTasks(planId, LocalDate.now());
        return tasks.stream()
                .map(this::toTaskResponse)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<TaskResponse> getTasksByPlan(String planId) {
        List<Task> tasks = taskRepository.findByPlanId(planId);
        return tasks.stream()
                .map(this::toTaskResponse)
                .collect(Collectors.toList());
    }

    @Transactional
    public TaskResponse completeTask(String taskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new BusinessException(ErrorCode.TASK_NOT_FOUND));

        if (task.getStatus() == 2) {
            throw new BusinessException(ErrorCode.TASK_ALREADY_COMPLETED);
        }

        task.setStatus(2);
        task = taskRepository.save(task);

        return toTaskResponse(task);
    }

    @Transactional
    public int completeTasks(List<String> taskIds) {
        return taskRepository.updateStatusByIds(taskIds, 2);
    }

    @Transactional
    public TaskResponse updateTaskStatus(String taskId, Integer status) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new BusinessException(ErrorCode.TASK_NOT_FOUND));

        task.setStatus(status);
        if (status == 2) {
            task.setCompletedAt(java.time.LocalDateTime.now());
        }

        task = taskRepository.save(task);
        return toTaskResponse(task);
    }

    @Transactional(readOnly = true)
    public long countTodayCompleted(String planId) {
        return taskRepository.countTodayCompleted(planId, LocalDate.now());
    }

    @Transactional(readOnly = true)
    public long countTodayTotal(String planId) {
        return taskRepository.countTodayTotal(planId, LocalDate.now());
    }

    private TaskResponse toTaskResponse(Task task) {
        return TaskResponse.builder()
                .taskId(task.getTaskId())
                .planId(task.getPlanId())
                .taskDate(task.getTaskDate())
                .subject(task.getSubject())
                .taskContent(task.getTaskContent())
                .estimatedMinutes(task.getEstimatedMinutes())
                .taskType(task.getTaskType())
                .phase(task.getPhase())
                .status(task.getStatus())
                .completedAt(task.getCompletedAt())
                .checkinType(task.getCheckinType())
                .build();
    }
}