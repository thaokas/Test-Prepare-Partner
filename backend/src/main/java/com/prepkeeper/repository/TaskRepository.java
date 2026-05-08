package com.prepkeeper.repository;

import com.prepkeeper.entity.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDate;
import java.util.List;

@Repository
public interface TaskRepository extends JpaRepository<Task, String> {

    List<Task> findByPlanId(String planId);

    List<Task> findByPlanIdAndTaskDate(String planId, LocalDate taskDate);

    List<Task> findByPlanIdAndTaskDateBetween(String planId, LocalDate startDate, LocalDate endDate);

    List<Task> findByPlanIdAndStatus(String planId, Integer status);

    /**
     * 查询今日任务
     */
    @Query("SELECT t FROM Task t WHERE t.planId = :planId AND t.taskDate = :date ORDER BY t.createdAt")
    List<Task> findTodayTasks(@Param("planId") String planId, @Param("date") LocalDate date);

    /**
     * 统计计划下任务总数
     */
    @Query("SELECT COUNT(t) FROM Task t WHERE t.planId = :planId")
    long countByPlanId(@Param("planId") String planId);

    /**
     * 统计计划下已完成任务数
     */
    @Query("SELECT COUNT(t) FROM Task t WHERE t.planId = :planId AND t.status = 2")
    long countCompletedByPlanId(@Param("planId") String planId);

    /**
     * 统计今日任务完成情况
     */
    @Query("SELECT COUNT(t) FROM Task t WHERE t.planId = :planId AND t.taskDate = :date AND t.status = 2")
    long countTodayCompleted(@Param("planId") String planId, @Param("date") LocalDate date);

    @Query("SELECT COUNT(t) FROM Task t WHERE t.planId = :planId AND t.taskDate = :date")
    long countTodayTotal(@Param("planId") String planId, @Param("date") LocalDate date);

    /**
     * 批量更新任务状态
     */
    @Modifying
    @Query("UPDATE Task t SET t.status = :status, t.completedAt = CURRENT_TIMESTAMP WHERE t.taskId IN :taskIds")
    int updateStatusByIds(@Param("taskIds") List<String> taskIds, @Param("status") Integer status);
}