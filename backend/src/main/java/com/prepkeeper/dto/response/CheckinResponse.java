package com.prepkeeper.dto.response;

import lombok.Builder;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Data
@Builder
public class CheckinResponse {

    private String checkinId;
    private String planId;
    private LocalDate checkinDate;
    private Integer completedTasks;
    private Integer totalTasks;
    private BigDecimal completionRate;
    private Integer currentStreak;

    /**
     * 鼓励话术(由Agent生成)
     */
    private String encouragement;

    /**
     * 彩蛋信息(如果触发)
     */
    private EasterEggResponse easterEgg;
}