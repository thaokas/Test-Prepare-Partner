package com.prepkeeper.repository;

import com.prepkeeper.entity.EasterEgg;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDate;
import java.util.List;

@Repository
public interface EasterEggRepository extends JpaRepository<EasterEgg, String> {

    List<EasterEgg> findByUserId(String userId);

    /**
     * 检查今日是否已触发某类型彩蛋
     */
    boolean existsByUserIdAndEggTypeAndTriggerDate(String userId, String eggType, LocalDate triggerDate);

    /**
     * 查询用户已触发的彩蛋
     */
    @Query("SELECT e FROM EasterEgg e WHERE e.userId = :userId AND e.isTriggered = 1 ORDER BY e.triggerDate DESC")
    List<EasterEgg> findTriggeredByUserId(@Param("userId") String userId);
}