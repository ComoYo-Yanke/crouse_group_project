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

    /**
     * 食物名：前端保存餐食时会把多个食物名用「、」拼接，
     * 长度不定，用 CLOB 避免 Value too long（曾为 length=100）。
     */
    @Lob
    @Column(name = "food_name", nullable = false, columnDefinition = "CLOB")
    private String foodName;

    /** 份量：前端为多个「食物名+份量」的分号拼接，同上用 CLOB（曾为 length=50）。 */
    @Lob
    @Column(columnDefinition = "CLOB")
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

    /**
     * 图片（前端以 base64 data URL 形式提交，长度可达数十 KB）
     * 必须用 CLOB 存储：原定义为 length=255，远超长会抛
     * Hibernate DataException: Value too long for column "IMAGE_URL"。
     */
    @Lob
    @Column(name = "image_url", columnDefinition = "CLOB")
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
