package com.nutritionist.controller;

import com.nutritionist.auth.UserContext;
import com.nutritionist.common.ApiResponse;
import com.nutritionist.dto.Dtos;
import com.nutritionist.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * 用户模块（api.md 二）
 */
@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    /** 注册 */
    @PostMapping("/register")
    public ApiResponse<Object> register(@Valid @RequestBody Dtos.RegisterReq req) {
        return ApiResponse.ok(userService.register(req));
    }

    /** 登录 */
    @PostMapping("/login")
    public ApiResponse<Object> login(@Valid @RequestBody Dtos.LoginReq req) {
        return ApiResponse.ok(userService.login(req));
    }

    /** 获取画像 */
    @GetMapping("/profile")
    public ApiResponse<Dtos.ProfileResp> profile() {
        return ApiResponse.ok(userService.getProfile(UserContext.require()));
    }

    /** 更新画像 */
    @PutMapping("/profile")
    public ApiResponse<Dtos.ProfileResp> updateProfile(@RequestBody Dtos.ProfileReq req) {
        return ApiResponse.ok(userService.updateProfile(UserContext.require(), req));
    }

    /** 个人主页 */
    @GetMapping("/{userId}/home")
    public ApiResponse<Dtos.UserHomeResp> home(@PathVariable Long userId) {
        return ApiResponse.ok(userService.getUserHome(userId));
    }
}
