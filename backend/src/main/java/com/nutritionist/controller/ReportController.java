package com.nutritionist.controller;

import com.nutritionist.auth.UserContext;
import com.nutritionist.common.ApiResponse;
import com.nutritionist.dto.Dtos;
import com.nutritionist.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

/**
 * 报告模块（api.md 四）
 */
@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    /** 每日报告 */
    @GetMapping("/daily")
    public ApiResponse<Dtos.DailyReportResp> daily(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ApiResponse.ok(reportService.daily(UserContext.require(), date));
    }

    /** 一周报告 */
    @GetMapping("/weekly")
    public ApiResponse<Dtos.WeeklyReportResp> weekly(
            @RequestParam(name = "start", required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate start) {
        return ApiResponse.ok(reportService.weekly(UserContext.require(), start));
    }
}
