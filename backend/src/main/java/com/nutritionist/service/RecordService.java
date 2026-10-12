package com.nutritionist.service;

import com.nutritionist.common.BusinessException;
import com.nutritionist.dto.Dtos;
import com.nutritionist.entity.Comment;
import com.nutritionist.entity.FoodRecord;
import com.nutritionist.entity.LikeRecord;
import com.nutritionist.repo.CommentRepository;
import com.nutritionist.repo.FoodRecordRepository;
import com.nutritionist.repo.LikeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 记录模块：录入、查询、删除、可见性、手动修正
 */
@Service
@RequiredArgsConstructor
public class RecordService {

    private final FoodRecordRepository recordRepo;
    private final LikeRepository likeRepo;
    private final CommentRepository commentRepo;

    /** 新增记录（need.md 3.3.1/3.3.2） */
    public Long create(Long userId, Dtos.RecordReq req) {
        if (req.getFoodName() == null || req.getFoodName().trim().isEmpty()) {
            throw new BusinessException(400, "食物名不能为空");
        }
        FoodRecord r = new FoodRecord();
        r.setUserId(userId);
        r.setFoodName(req.getFoodName());
        r.setPortion(req.getPortion());
        r.setMealType(req.getMealType() == null ? "加餐" : req.getMealType());
        r.setImageUrl(req.getImageUrl());
        r.setConfidence(req.getConfidence());
        r.setVisibility("public".equals(req.getVisibility()) ? "public" : "private");
        r.setRecordDate(LocalDate.now());
        if (req.getNutrition() != null) {
            r.setCalories(req.getNutrition().getCalories());
            r.setProtein(req.getNutrition().getProtein());
            r.setFat(req.getNutrition().getFat());
            r.setCarbs(req.getNutrition().getCarbs());
            r.setFiber(req.getNutrition().getFiber());
            r.setSodium(req.getNutrition().getSodium());
        }
        return recordRepo.save(r).getId();
    }

    /** 查询记录（need.md 3.3.4）：按日期+餐次，附当日汇总 */
    public Dtos.RecordListResp list(Long userId, LocalDate date, String mealType) {
        List<FoodRecord> records;
        if (date == null) {
            date = LocalDate.now();
        }
        if (mealType != null && !mealType.isEmpty()) {
            records = recordRepo.findByUserIdAndRecordDateAndMealTypeOrderByCreatedAtDesc(userId, date, mealType);
        } else {
            records = recordRepo.findByUserIdAndRecordDateOrderByCreatedAtDesc(userId, date);
        }

        Dtos.RecordListResp resp = new Dtos.RecordListResp();
        resp.setRecords(records.stream().map(this::toMap).collect(Collectors.toList()));
        resp.setTotal(sumNutrition(records));
        return resp;
    }

    /** 删除记录：仅本人 */
    @Transactional
    public void delete(Long userId, Long recordId) {
        FoodRecord r = getOwned(userId, recordId);
        likeRepo.deleteByRecordId(recordId);
        commentRepo.deleteByRecordId(recordId);
        recordRepo.delete(r);
    }

    /** 修改可见性（need.md 3.3.5） */
    public Map<String, Object> updateVisibility(Long userId, Long recordId, String visibility) {
        if (!"public".equals(visibility) && !"private".equals(visibility)) {
            throw new BusinessException(400, "visibility 只能为 public/private");
        }
        FoodRecord r = getOwned(userId, recordId);
        r.setVisibility(visibility);
        recordRepo.save(r);
        Map<String, Object> m = new HashMap<>();
        m.put("recordId", recordId);
        m.put("visibility", visibility);
        return m;
    }

    /** 手动修正（need.md 3.3.3）：标记 is_corrected */
    public Map<String, Object> update(Long userId, Long recordId, Dtos.RecordUpdateReq req) {
        FoodRecord r = getOwned(userId, recordId);
        if (req.getFoodName() != null) r.setFoodName(req.getFoodName());
        if (req.getPortion() != null) r.setPortion(req.getPortion());
        if (req.getNutrition() != null) {
            Dtos.NutritionDto n = req.getNutrition();
            if (n.getCalories() != null) r.setCalories(n.getCalories());
            if (n.getProtein() != null) r.setProtein(n.getProtein());
            if (n.getFat() != null) r.setFat(n.getFat());
            if (n.getCarbs() != null) r.setCarbs(n.getCarbs());
            if (n.getFiber() != null) r.setFiber(n.getFiber());
            if (n.getSodium() != null) r.setSodium(n.getSodium());
        }
        r.setIsCorrected(true);
        recordRepo.save(r);
        return toMap(r);
    }

    public FoodRecord get(Long recordId) {
        return recordRepo.findById(recordId)
                .orElseThrow(() -> new BusinessException(404, "记录不存在"));
    }

    public FoodRecord getOwned(Long userId, Long recordId) {
        FoodRecord r = get(recordId);
        if (!r.getUserId().equals(userId)) {
            throw new BusinessException(403, "只能操作自己的记录");
        }
        return r;
    }

    /** 校验记录公开才可点赞/评论 */
    public FoodRecord getPublic(Long recordId) {
        FoodRecord r = get(recordId);
        if (!"public".equals(r.getVisibility())) {
            throw new BusinessException(400, "私密记录不可点赞/评论");
        }
        return r;
    }

    public Map<String, Object> toMap(FoodRecord r) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("recordId", r.getId());
        m.put("foodName", r.getFoodName());
        m.put("portion", r.getPortion());
        m.put("mealType", r.getMealType());
        m.put("imageUrl", r.getImageUrl());
        Map<String, Object> n = new LinkedHashMap<>();
        n.put("calories", r.getCalories());
        n.put("protein", r.getProtein());
        n.put("fat", r.getFat());
        n.put("carbs", r.getCarbs());
        n.put("fiber", r.getFiber());
        n.put("sodium", r.getSodium());
        m.put("nutrition", n);
        m.put("visibility", r.getVisibility());
        m.put("isCorrected", r.getIsCorrected());
        m.put("createdAt", r.getCreatedAt().toString());
        return m;
    }

    /** 汇总营养 */
    public Map<String, Object> sumNutrition(List<FoodRecord> records) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("calories", round(records.stream().mapToDouble(r -> nz(r.getCalories())).sum()));
        m.put("protein", round(records.stream().mapToDouble(r -> nz(r.getProtein())).sum()));
        m.put("fat", round(records.stream().mapToDouble(r -> nz(r.getFat())).sum()));
        m.put("carbs", round(records.stream().mapToDouble(r -> nz(r.getCarbs())).sum()));
        m.put("fiber", round(records.stream().mapToDouble(r -> nz(r.getFiber())).sum()));
        m.put("sodium", round(records.stream().mapToDouble(r -> nz(r.getSodium())).sum()));
        return m;
    }

    private double nz(Double d) {
        return d == null ? 0 : d;
    }

    private double round(double v) {
        return Math.round(v * 10) / 10.0;
    }
}
