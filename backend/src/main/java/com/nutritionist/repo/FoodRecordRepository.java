package com.nutritionist.repo;

import com.nutritionist.entity.FoodRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDate;
import java.util.List;

public interface FoodRecordRepository extends JpaRepository<FoodRecord, Long> {

    List<FoodRecord> findByUserIdAndRecordDateOrderByCreatedAtDesc(Long userId, LocalDate date);

    List<FoodRecord> findByUserIdAndRecordDateAndMealTypeOrderByCreatedAtDesc(
            Long userId, LocalDate date, String mealType);

    List<FoodRecord> findByUserIdAndRecordDateBetweenOrderByRecordDate(
            Long userId, LocalDate start, LocalDate end);

    List<FoodRecord> findByUserIdAndVisibilityOrderByCreatedAtDesc(Long userId, String visibility);

    /** 广场：仅公开记录，支持餐次筛选，按时间或点赞数排序 */
    @Query("SELECT r FROM FoodRecord r WHERE r.visibility = 'public' " +
            "AND (:mealType IS NULL OR r.mealType = :mealType) " +
            "AND (:recordId IS NULL OR r.id <> :recordId) " +
            "ORDER BY r.createdAt DESC")
    Page<FoodRecord> findSquare(@Param("mealType") String mealType,
                                @Param("recordId") Long recordId,
                                Pageable pageable);
}
