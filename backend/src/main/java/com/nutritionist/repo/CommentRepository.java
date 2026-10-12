package com.nutritionist.repo;

import com.nutritionist.entity.Comment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CommentRepository extends JpaRepository<Comment, Long> {

    /** 一级评论（按时间倒序，需求 3.8.4） */
    List<Comment> findByRecordIdAndParentIdNullOrderByCreatedAtDesc(Long recordId);

    /** 某记录的所有评论（统计用） */
    long countByRecordId(Long recordId);

    /** 一级评论下的回复（按时间正序） */
    List<Comment> findByParentIdOrderByCreatedAtAsc(Long parentId);

    void deleteByParentId(Long parentId);

    void deleteByRecordId(Long recordId);
}
