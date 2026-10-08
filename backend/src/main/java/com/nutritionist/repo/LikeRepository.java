package com.nutritionist.repo;

import com.nutritionist.entity.LikeRecord;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface LikeRepository extends JpaRepository<LikeRecord, Long> {

    Optional<LikeRecord> findByUserIdAndRecordId(Long userId, Long recordId);

    long countByRecordId(Long recordId);

    List<LikeRecord> findByUserIdAndRecordIdIn(Long userId, List<Long> recordIds);

    List<LikeRecord> findByRecordIdIn(List<Long> recordIds);

    void deleteByRecordId(Long recordId);
}
