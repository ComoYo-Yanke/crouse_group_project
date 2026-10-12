package com.nutritionist.entity;

import lombok.Data;

import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * 评论表，分楼（sql.md 2.5）
 * parent_id = null 一级评论；指向一级评论则为二级回复；最多两层
 */
@Data
@Entity
@Table(name = "comment", indexes = {
        @Index(name = "idx_comment_record", columnList = "record_id, created_at"),
        @Index(name = "idx_parent", columnList = "parent_id")
})
public class Comment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "record_id", nullable = false)
    private Long recordId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    /** 父评论ID，NULL = 一级评论 */
    @Column(name = "parent_id")
    private Long parentId;

    @Column(nullable = false, length = 500)
    private String content;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
