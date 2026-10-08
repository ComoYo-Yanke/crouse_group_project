package com.nutritionist.auth;

/**
 * 当前登录用户上下文（线程级）
 */
public class UserContext {

    private static final ThreadLocal<Long> CURRENT = new ThreadLocal<>();

    public static void set(Long userId) {
        CURRENT.set(userId);
    }

    public static Long get() {
        return CURRENT.get();
    }

    public static Long require() {
        Long userId = CURRENT.get();
        if (userId == null) {
            throw new com.nutritionist.common.BusinessException(401, "未登录");
        }
        return userId;
    }

    public static void clear() {
        CURRENT.remove();
    }
}
