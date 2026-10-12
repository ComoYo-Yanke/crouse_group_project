package com.nutritionist.service;

import com.nutritionist.auth.UserContext;
import com.nutritionist.dto.Dtos;
import com.nutritionist.entity.FoodRecord;
import com.nutritionist.entity.User;
import com.nutritionist.repo.FoodRecordRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 报告模块：每日聚合、缺口分析、一周趋势（need.md 3.5）
 */
@Service
@RequiredArgsConstructor
public class ReportService {

    private final FoodRecordRepository recordRepo;
    private final RecordService recordService;
    private final UserService userService;

    /**
     * 每日报告：total + target + gap
     * 目标按热量比例拆分：蛋白 15%、脂肪 25%、碳水 60%
     * 蛋白/碳水 4 kcal/g，脂肪 9 kcal/g
     */
    public Dtos.DailyReportResp daily(Long userId, LocalDate date) {
        if (date == null) date = LocalDate.now();
        List<FoodRecord> records =
                recordRepo.findByUserIdAndRecordDateOrderByCreatedAtDesc(userId, date);
        Map<String, Object> total = recordService.sumNutrition(records);

        User user = userService.getUser(userId);
        long targetCalories = userService.calcTargetCalories(user);

        Map<String, Object> target = new LinkedHashMap<>();
        target.put("calories", targetCalories);
        target.put("protein", Math.round(targetCalories * 0.15 / 4));
        target.put("fat", Math.round(targetCalories * 0.25 / 9));
        target.put("carbs", Math.round(targetCalories * 0.60 / 4));

        Map<String, Object> gap = new LinkedHashMap<>();
        for (String k : Arrays.asList("calories", "protein", "fat", "carbs")) {
            double t = ((Number) target.get(k)).doubleValue();
            double actual = ((Number) total.getOrDefault(k, 0)).doubleValue();
            gap.put(k, Math.round((t - actual) * 10) / 10.0); // 正=还差，负=超出
        }

        Dtos.DailyReportResp resp = new Dtos.DailyReportResp();
        resp.setDate(date.toString());
        resp.setTotal(total);
        resp.setTarget(target);
        resp.setGap(gap);
        return resp;
    }

    /** 一周报告：7 天逐日 + 趋势 */
    public Dtos.WeeklyReportResp weekly(Long userId, LocalDate start) {
        if (start == null) {
            start = LocalDate.now().minusDays(6);
        }
        List<FoodRecord> records =
                recordRepo.findByUserIdAndRecordDateBetweenOrderByRecordDate(userId, start, start.plusDays(6));

        // 按日期分组汇总
        Map<LocalDate, List<FoodRecord>> byDate = records.stream()
                .collect(Collectors.groupingBy(FoodRecord::getRecordDate));

        List<Map<String, Object>> days = new ArrayList<>();
        for (int i = 0; i < 7; i++) {
            LocalDate d = start.plusDays(i);
            Map<String, Object> total =
                    recordService.sumNutrition(byDate.getOrDefault(d, Collections.emptyList()));
            Map<String, Object> day = new LinkedHashMap<>();
            day.put("date", d.toString());
            day.put("calories", total.get("calories"));
            day.put("protein", total.get("protein"));
            day.put("fat", total.get("fat"));
            day.put("carbs", total.get("carbs"));
            days.add(day);
        }

        Map<String, List<Object>> trend = new LinkedHashMap<>();
        for (String k : Arrays.asList("calories", "protein", "fat", "carbs")) {
            trend.put(k, days.stream().map(d -> d.get(k)).collect(Collectors.toList()));
        }

        Dtos.WeeklyReportResp resp = new Dtos.WeeklyReportResp();
        resp.setDays(days);
        resp.setTrend(trend);
        return resp;
    }
}
