package com.prepkeeper.repository;

import com.prepkeeper.entity.Checkin;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface CheckinRepository extends JpaRepository<Checkin, String> {

    List<Checkin> findByUserId(String userId);

    List<Checkin> findByUserIdOrderByCheckinDateDesc(String userId);

    Optional<Checkin> findByUserIdAndPlanIdAndCheckinDate(String userId, String planId, LocalDate checkinDate);

    /**
     * 检查今日是否已打卡
     */
    boolean existsByUserIdAndPlanIdAndCheckinDate(String userId, String planId, LocalDate checkinDate);

    /**
     * 查询用户某时间范围内的打卡记录
     */
    @Query("SELECT c FROM Checkin c WHERE c.userId = :userId AND c.checkinDate BETWEEN :startDate AND :endDate ORDER BY c.checkinDate DESC")
    List<Checkin> findByUserIdAndDateRange(@Param("userId") String userId, @Param("startDate") LocalDate startDate, @Param("endDate") LocalDate endDate);

    /**
     * 统计用户累计打卡天数
     */
    @Query("SELECT COUNT(DISTINCT c.checkinDate) FROM Checkin c WHERE c.userId = :userId")
    long countDistinctCheckinDates(@Param("userId") String userId);

    /**
     * 查询昨日是否打卡
     */
    @Query("SELECT CASE WHEN COUNT(c) > 0 THEN true ELSE false END FROM Checkin c WHERE c.userId = :userId AND c.checkinDate = :yesterday")
    boolean checkedYesterday(@Param("userId") String userId, @Param("yesterday") LocalDate yesterday);
}