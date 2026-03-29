package com.prepkeeper.exception;

import lombok.Getter;

@Getter
public enum ErrorCode {

    // 用户相关 1xxx
    USER_NOT_FOUND(1001, "用户不存在"),
    PASSWORD_ERROR(1002, "密码错误"),
    USER_EXISTS(1003, "用户已存在"),
    EMAIL_EXISTS(1004, "邮箱已被注册"),
    NICKNAME_EXISTS(1005, "昵称已被使用"),

    // 计划相关 2xxx
    PLAN_NOT_FOUND(2001, "计划不存在"),
    TASK_NOT_FOUND(2002, "任务不存在"),
    PLAN_NOT_ACTIVE(2003, "计划未激活"),
    TASK_ALREADY_COMPLETED(2004, "任务已完成"),

    // 认证相关 3xxx
    TOKEN_INVALID(3001, "Token无效"),
    TOKEN_EXPIRED(3002, "Token已过期"),
    UNAUTHORIZED(3003, "未授权"),
    FORBIDDEN(3004, "无权限访问"),

    // Agent服务相关 5xxx
    AGENT_SERVICE_ERROR(5001, "Agent服务异常"),
    AGENT_TIMEOUT(5002, "Agent服务超时"),

    // 系统相关 9xxx
    SYSTEM_ERROR(9999, "系统异常"),
    PARAM_ERROR(9998, "参数错误");

    private final int code;
    private final String message;

    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
}