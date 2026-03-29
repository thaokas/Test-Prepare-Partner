package com.prepkeeper.util;

import cn.hutool.core.util.IdUtil;

public class IdGenerator {

    public static String generateUserId() {
        return "U" + IdUtil.getSnowflakeNextIdStr();
    }

    public static String generatePlanId() {
        return "P" + IdUtil.getSnowflakeNextIdStr();
    }

    public static String generateTaskId() {
        return "T" + IdUtil.getSnowflakeNextIdStr();
    }

    public static String generateCheckinId() {
        return "C" + IdUtil.getSnowflakeNextIdStr();
    }

    public static String generateReminderId() {
        return "R" + IdUtil.getSnowflakeNextIdStr();
    }

    public static String generateEasterEggId() {
        return "E" + IdUtil.getSnowflakeNextIdStr();
    }
}