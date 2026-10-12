package com.nutritionist.entity;

import lombok.Data;

import javax.persistence.*;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 饮食记录表（sql.md 2.2）
 */
@Data
@Entity
@Table(name = "food_record", indexes = {
        @Index(name = "idx_user_date", columnList = "user_id, record_date"),
        @Index(name = "idx_visibility", columnList = "visibility, created_at")
})
public class FoodRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "food_name", nullable = false, length = 100)
    private String foodName;

    @Column(length = 50)
    private String portion;

    /** 早餐/午餐/晚餐/加餐 */
    @Column(name = "meal_type", length = 20)
    private String mealType;

    private Double calories;
    private Double protein;
    private Double fat;
    private Double carbs;
    private Double fiber;
    private Double sodium;

    @Column(name = "image_url", length = 255)
    private String imageUrl;

    /** 识别置信度 0-1 */
    private Double confidence;

    @Column(name = "is_corrected")
    private Boolean isCorrected = false;

    /** public / private */
    @Column(length = 10)
    private String visibility = "private";

    @Column(name = "record_date", nullable = false)
    private LocalDate recordDate;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
