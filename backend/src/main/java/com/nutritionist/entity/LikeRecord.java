package com.nutritionist.entity;

import lombok.Data;

import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * 点赞表（sql.md 2.4）
 * 表名 like 是 SQL 关键字，故实体名 LikeRecord
 */
@Data
@Entity
@Table(name = "`like`", indexes = {
        @Index(name = "uk_user_record", columnList = "user_id, record_id", unique = true),
        @Index(name = "idx_record", columnList = "record_id")
})
public class LikeRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "record_id", nullable = false)
    private Long recordId;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
