package com.nutritionist.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;
import java.util.Map;

/**
 * 请求/响应 DTO 聚合（对应 doc/api.md）
 */
public class Dtos {

    /* ================= 用户模块 ================= */

    @Data
    public static class RegisterReq {
        @NotBlank(message = "用户名不能为空")
        private String username;
        @NotBlank(message = "密码不能为空")
        private String password;
        private Double height;
        private Double weight;
        private Integer age;
        private String gender;
        private String goal;
        private String avoid;
        private String allergy;
    }

    @Data
    public static class LoginReq {
        @NotBlank(message = "用户名不能为空")
        private String username;
        @NotBlank(message = "密码不能为空")
        private String password;
    }

    @Data
    public static class ProfileReq {
        private Double height;
        private Double weight;
        private Integer age;
        private String gender;
        private String goal;
        private String avoid;
        private String allergy;
    }

    @Data
    public static class ProfileResp {
        private Long userId;
        private String username;
        private Double height;
        private Double weight;
        private Integer age;
        private String gender;
        private String goal;
        private String avoid;
        private String allergy;
        /** 基础代谢 */
        private Long bmr;
        /** 目标摄入 kcal */
        private Long targetCalories;
    }

    @Data
    public static class UserHomeResp {
        private Long userId;
        private String username;
        private List<Map<String, Object>> publicRecords;
        private long totalLikes;
        private long totalComments;
    }

    /* ================= 记录模块 ================= */

    @Data
    public static class NutritionDto {
        private Double calories;
        private Double protein;
        private Double fat;
        private Double carbs;
        private Double fiber;
        private Double sodium;
    }

    @Data
    public static class RecordReq {
        private String foodName;
        private String portion;
        private String mealType;
        private String imageUrl;
        private NutritionDto nutrition;
        private String visibility;
        private Double confidence;
    }

    @Data
    public static class RecordUpdateReq {
        private String foodName;
        private String portion;
        private NutritionDto nutrition;
    }

    @Data
    public static class VisibilityReq {
        private String visibility;
    }

    @Data
    public static class RecordListResp {
        private List<Map<String, Object>> records;
        private Map<String, Object> total;
    }

    /* ================= 报告模块 ================= */

    @Data
    public static class DailyReportResp {
        private String date;
        private Map<String, Object> total;
        private Map<String, Object> target;
        private Map<String, Object> gap;
    }

    @Data
    public static class WeeklyReportResp {
        private List<Map<String, Object>> days;
        private Map<String, List<Object>> trend;
    }

    /* ================= 社交模块 ================= */

    @Data
    public static class SquareResp {
        private long total;
        private int page;
        private int size;
        private List<Map<String, Object>> records;
    }

    @Data
    public static class CommentReq {
        private Long recordId;
        @NotBlank(message = "评论内容不能为空")
        private String content;
        /** 为空=一级评论；指向一级评论=二级回复 */
        private Long parentId;
    }

    @Data
    public static class CommentResp {
        private List<Map<String, Object>> comments;
    }
}
