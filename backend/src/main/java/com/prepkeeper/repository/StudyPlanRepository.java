package com.prepkeeper.repository;

import com.prepkeeper.entity.StudyPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface StudyPlanRepository extends JpaRepository<StudyPlan, String> {

    List<StudyPlan> findByUserId(String userId);

    List<StudyPlan> findByUserIdAndPlanStatus(String userId, Integer planStatus);

    Optional<StudyPlan> findByPlanIdAndUserId(String planId, String userId);

    /**
     * 查询用户活跃的计划(进行中)
     */
    @Query("SELECT sp FROM StudyPlan sp WHERE sp.userId = :userId AND sp.planStatus = 0")
    List<StudyPlan> findActivePlansByUserId(@Param("userId") String userId);

    /**
     * 查询所有非静默模式的活跃计划(用于定时提醒)
     */
    @Query("SELECT sp FROM StudyPlan sp WHERE sp.planStatus = 0 AND sp.currentMode > 0")
    List<StudyPlan> findAllActivePlansWithReminder();
}