package com.prepkeeper.repository;

import com.prepkeeper.entity.Reminder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ReminderRepository extends JpaRepository<Reminder, String> {

    List<Reminder> findByUserId(String userId);

    List<Reminder> findByUserIdAndIsSent(String userId, Integer isSent);

    /**
     * 查询待发送的提醒
     */
    @Query("SELECT r FROM Reminder r WHERE r.isSent = 0 AND r.triggerTime <= :now")
    List<Reminder> findPendingReminders(@Param("now") LocalDateTime now);

    /**
     * 标记提醒已发送
     */
    @Modifying
    @Query("UPDATE Reminder r SET r.isSent = 1, r.sentAt = CURRENT_TIMESTAMP WHERE r.reminderId = :reminderId")
    int markAsSent(@Param("reminderId") String reminderId);
}