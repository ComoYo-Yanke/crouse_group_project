package com.nutritionist.controller;

import com.nutritionist.auth.UserContext;
import com.nutritionist.common.ApiResponse;
import com.nutritionist.dto.Dtos;
import com.nutritionist.service.RecordService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.time.LocalDate;

/**
 * 记录模块（api.md 三）
 */
@RestController
@RequestMapping("/api/record")
@RequiredArgsConstructor
public class RecordController {

    private final RecordService recordService;

    /** 新增记录（拍照/文字录入确认后） */
    @PostMapping
    public ApiResponse<Object> create(@RequestBody Dtos.RecordReq req) {
        return ApiResponse.ok(java.util.Collections.singletonMap("recordId",
                recordService.create(UserContext.require(), req)));
    }

    /** 查询记录：?date=2025-01-01&mealType=午餐 */
    @GetMapping
    public ApiResponse<Dtos.RecordListResp> list(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @RequestParam(required = false) String mealType) {
        return ApiResponse.ok(recordService.list(UserContext.require(), date, mealType));
    }

    /** 删除记录 */
    @DeleteMapping("/{recordId}")
    public ApiResponse<Void> delete(@PathVariable Long recordId) {
        recordService.delete(UserContext.require(), recordId);
        return ApiResponse.ok();
    }

    /** 修改可见性 */
    @PutMapping("/{recordId}/visibility")
    public ApiResponse<Object> visibility(@PathVariable Long recordId,
                                          @RequestBody Dtos.VisibilityReq req) {
        return ApiResponse.ok(recordService.updateVisibility(UserContext.require(), recordId, req.getVisibility()));
    }

    /** 手动修正 */
    @PutMapping("/{recordId}")
    public ApiResponse<Object> update(@PathVariable Long recordId,
                                      @RequestBody Dtos.RecordUpdateReq req) {
        return ApiResponse.ok(recordService.update(UserContext.require(), recordId, req));
    }
}
