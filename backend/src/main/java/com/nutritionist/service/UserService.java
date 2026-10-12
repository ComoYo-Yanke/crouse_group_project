package com.nutritionist.service;

import com.nutritionist.auth.JwtUtil;
import com.nutritionist.common.BusinessException;
import com.nutritionist.dto.Dtos;
import com.nutritionist.entity.Comment;
import com.nutritionist.entity.FoodRecord;
import com.nutritionist.entity.LikeRecord;
import com.nutritionist.entity.User;
import com.nutritionist.repo.CommentRepository;
import com.nutritionist.repo.FoodRecordRepository;
import com.nutritionist.repo.LikeRepository;
import com.nutritionist.repo.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 用户模块：注册、登录、画像、个人主页
 * BMR 与目标摄入公式见 need.md 11.1 / 11.2
 */
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepo;
    private final FoodRecordRepository recordRepo;
    private final LikeRepository likeRepo;
    private final CommentRepository commentRepo;
    private final JwtUtil jwtUtil;

    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    /** 注册：用户名唯一 + 密码加密 */
    public Map<String, Object> register(Dtos.RegisterReq req) {
        if (userRepo.existsByUsername(req.getUsername())) {
            throw new BusinessException(400, "用户名已存在");
        }
        if (req.getPassword() == null || req.getPassword().length() < 6) {
            throw new BusinessException(400, "密码至少 6 位");
        }
        User user = new User();
        user.setUsername(req.getUsername());
        user.setPassword(encoder.encode(req.getPassword()));
        user.setHeight(req.getHeight());
        user.setWeight(req.getWeight());
        user.setAge(req.getAge());
        user.setGender(req.getGender());
        user.setGoal(req.getGoal() == null ? "维持" : req.getGoal());
        user.setAvoid(req.getAvoid());
        user.setAllergy(req.getAllergy());
        user = userRepo.save(user);

        Map<String, Object> data = new HashMap<>();
        data.put("userId", user.getId());
        data.put("token", jwtUtil.generate(user.getId()));
        return data;
    }

    /** 登录：校验密码，签发 JWT */
    public Map<String, Object> login(Dtos.LoginReq req) {
        User user = userRepo.findByUsername(req.getUsername())
                .orElseThrow(() -> new BusinessException(404, "用户名不存在"));
        if (!encoder.matches(req.getPassword(), user.getPassword())) {
            throw new BusinessException(400, "密码错误");
        }
        Map<String, Object> data = new HashMap<>();
        data.put("userId", user.getId());
        data.put("token", jwtUtil.generate(user.getId()));
        data.put("profile", toProfile(user));
        return data;
    }

    /** 获取画像 */
    public Dtos.ProfileResp getProfile(Long userId) {
        User user = getUser(userId);
        return toProfile(user);
    }

    /** 更新画像（need.md 3.2.3） */
    public Dtos.ProfileResp updateProfile(Long userId, Dtos.ProfileReq req) {
        User user = getUser(userId);
        if (req.getHeight() != null) user.setHeight(req.getHeight());
        if (req.getWeight() != null) user.setWeight(req.getWeight());
        if (req.getAge() != null) user.setAge(req.getAge());
        if (req.getGender() != null) user.setGender(req.getGender());
        if (req.getGoal() != null) user.setGoal(req.getGoal());
        if (req.getAvoid() != null) user.setAvoid(req.getAvoid());
        if (req.getAllergy() != null) user.setAllergy(req.getAllergy());
        userRepo.save(user);
        return toProfile(user);
    }

    /** 个人主页：仅公开记录 + 点赞/评论统计（need.md 3.2.4） */
    public Dtos.UserHomeResp getUserHome(Long userId) {
        User user = getUser(userId);
        List<FoodRecord> records = recordRepo.findByUserIdAndVisibilityOrderByCreatedAtDesc(userId, "public");

        List<Long> recordIds = records.stream().map(FoodRecord::getId).collect(Collectors.toList());
        Map<Long, Long> likeCountMap = recordIds.isEmpty() ? Collections.emptyMap()
                : likeRepo.findByRecordIdIn(recordIds).stream()
                .collect(Collectors.groupingBy(LikeRecord::getRecordId, Collectors.counting()));
        Map<Long, Long> commentCountMap = new HashMap<>();
        for (Long rid : recordIds) {
            commentCountMap.put(rid, commentRepo.countByRecordId(rid));
        }

        Dtos.UserHomeResp resp = new Dtos.UserHomeResp();
        resp.setUserId(user.getId());
        resp.setUsername(user.getUsername());
        resp.setPublicRecords(records.stream().map(r -> {
            Map<String, Object> m = new HashMap<>();
            m.put("recordId", r.getId());
            m.put("foodName", r.getFoodName());
            m.put("imageUrl", r.getImageUrl());
            m.put("calories", r.getCalories());
            m.put("likeCount", likeCountMap.getOrDefault(r.getId(), 0L));
            m.put("commentCount", commentCountMap.getOrDefault(r.getId(), 0L));
            m.put("createdAt", r.getCreatedAt().toString());
            return m;
        }).collect(Collectors.toList()));
        resp.setTotalLikes(likeCountMap.values().stream().mapToLong(Long::longValue).sum());
        resp.setTotalComments(commentCountMap.values().stream().mapToLong(Long::longValue).sum());
        return resp;
    }

    public User getUser(Long userId) {
        return userRepo.findById(userId)
                .orElseThrow(() -> new BusinessException(404, "用户不存在"));
    }

    /* ============ 营养计算（need.md 11.1/11.2） ============ */

    /** 基础代谢 BMR：男 10W+6.25H-5A+5；女 10W+6.25H-5A-161 */
    public long calcBmr(User user) {
        if (user.getWeight() == null || user.getHeight() == null || user.getAge() == null) {
            return 1500; // 信息不全时的默认值
        }
        double bmr = 10 * user.getWeight() + 6.25 * user.getHeight() - 5 * user.getAge();
        boolean male = !"女".equals(user.getGender());
        return Math.round(male ? bmr + 5 : bmr - 161);
    }

    /** 目标摄入：减脂 BMR*1.2-500；增肌 BMR*1.5+300；维持/控糖 BMR*1.3 */
    public long calcTargetCalories(User user) {
        long bmr = calcBmr(user);
        String goal = user.getGoal() == null ? "维持" : user.getGoal();
        switch (goal) {
            case "减脂": return Math.round(bmr * 1.2 - 500);
            case "增肌": return Math.round(bmr * 1.5 + 300);
            default:     return Math.round(bmr * 1.3);
        }
    }

    private Dtos.ProfileResp toProfile(User user) {
        Dtos.ProfileResp p = new Dtos.ProfileResp();
        p.setUserId(user.getId());
        p.setUsername(user.getUsername());
        p.setHeight(user.getHeight());
        p.setWeight(user.getWeight());
        p.setAge(user.getAge());
        p.setGender(user.getGender());
        p.setGoal(user.getGoal());
        p.setAvoid(user.getAvoid());
        p.setAllergy(user.getAllergy());
        p.setBmr(calcBmr(user));
        p.setTargetCalories(calcTargetCalories(user));
        return p;
    }
}
