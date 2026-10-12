package com.nutritionist.controller;

import com.nutritionist.auth.UserContext;
import com.nutritionist.common.ApiResponse;
import com.nutritionist.dto.Dtos;
import com.nutritionist.service.SocialService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * 社交模块（api.md 五）
 */
@RestController
@RequiredArgsConstructor
public class SocialController {

    private final SocialService socialService;

    /** 公开广场：?page=1&size=10&sort=time&mealType=午餐 */
    @GetMapping("/api/square")
    public ApiResponse<Dtos.SquareResp> square(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "time") String sort,
            @RequestParam(required = false) String mealType) {
        return ApiResponse.ok(socialService.square(page, size, sort, mealType));
    }

    /** 点赞/取消 */
    @PostMapping("/api/like/{recordId}")
    public ApiResponse<Object> like(@PathVariable Long recordId) {
        return ApiResponse.ok(socialService.toggleLike(UserContext.require(), recordId));
    }

    /** 评论列表（分楼） */
    @GetMapping("/api/comment/{recordId}")
    public ApiResponse<Dtos.CommentResp> comments(@PathVariable Long recordId) {
        return ApiResponse.ok(socialService.comments(recordId));
    }

    /** 发表评论 */
    @PostMapping("/api/comment")
    public ApiResponse<Object> addComment(@Valid @RequestBody Dtos.CommentReq req) {
        return ApiResponse.ok(socialService.addComment(UserContext.require(), req));
    }

    /** 删除评论 */
    @DeleteMapping("/api/comment/{commentId}")
    public ApiResponse<Void> deleteComment(@PathVariable Long commentId) {
        socialService.deleteComment(UserContext.require(), commentId);
        return ApiResponse.ok();
    }
}
