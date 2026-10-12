package com.nutritionist.entity;

import lombok.Data;

import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * 用户表（sql.md 2.1）
 */
@Data
@Entity
@Table(name = "`user`", indexes = @Index(name = "idx_username", columnList = "username"))
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, length = 100)
    private String password;

    /** 身高 cm */
    private Double height;

    /** 体重 kg */
    private Double weight;

    private Integer age;

    /** 男/女 */
    @Column(length = 10)
    private String gender;

    /** 减脂/增肌/控糖/维持 */
    @Column(length = 20)
    private String goal;

    /** 忌口 */
    @Column(length = 200)
    private String avoid;

    /** 过敏原 */
    @Column(length = 200)
    private String allergy;

    @Column(length = 255)
    private String avatar;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    @PreUpdate
    public void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
