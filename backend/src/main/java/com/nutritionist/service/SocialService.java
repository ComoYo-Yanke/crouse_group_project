package com.nutritionist.service;

import com.nutritionist.auth.UserContext;
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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 社交模块：公开广场、点赞、评论分楼（need.md 3.8）
 */
@Service
@RequiredArgsConstructor
public class SocialService {

    private final FoodRecordRepository recordRepo;
    private final LikeRepository likeRepo;
    private final CommentRepository commentRepo;
    private final UserRepository userRepo;
    private final RecordService recordService;

    /**
     * 公开广场（need.md 3.8.1）
     * sort=time 按时间倒序；sort=likes 按点赞数倒序（内存排序，数据量小可接受）
     */
    public Dtos.SquareResp square(int page, int size, String sort, String mealType) {
        if (page < 1) page = 1;
        if (size < 1 || size > 50) size = 10;

        Page<FoodRecord> p = recordRepo.findSquare(
                (mealType == null || mealType.isEmpty()) ? null : mealType,
                null,
                PageRequest.of(page - 1, size, Sort.by(Sort.Direction.DESC, "createdAt")));

        List<FoodRecord> records = new ArrayList<>(p.getContent());

        // 按点赞数排序：取整页后重排（演示规模足够）
        if ("likes".equals(sort)) {
            Map<Long, Long> likeCount = likeMap(records);
            records.sort((a, b) -> Long.compare(
                    likeCount.getOrDefault(b.getId(), 0L),
                    likeCount.getOrDefault(a.getId(), 0L)));
        }

        Long currentUserId = UserContext.get();
        List<Long> recordIds = records.stream().map(FoodRecord::getId).collect(Collectors.toList());
        Map<Long, Long> likeCounts = likeMap(records);
        Map<Long, Long> commentCounts = new HashMap<>();
        Set<Long> likedByMe = new HashSet<>();
        for (Long rid : recordIds) {
            commentCounts.put(rid, commentRepo.countByRecordId(rid));
        }
        if (currentUserId != null && !recordIds.isEmpty()) {
            likedByMe = likeRepo.findByUserIdAndRecordIdIn(currentUserId, recordIds).stream()
                    .map(LikeRecord::getRecordId)
                    .collect(Collectors.toSet());
        }

        // 用户名映射
        Set<Long> userIds = records.stream().map(FoodRecord::getUserId).collect(Collectors.toSet());
        Map<Long, String> userNames = new HashMap<>();
        if (!userIds.isEmpty()) {
            userRepo.findAllById(userIds).forEach(u -> userNames.put(u.getId(), u.getUsername()));
        }

        Dtos.SquareResp resp = new Dtos.SquareResp();
        resp.setTotal(p.getTotalElements());
        resp.setPage(page);
        resp.setSize(size);
        resp.setRecords(records.stream().map(r -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("recordId", r.getId());
            m.put("userId", r.getUserId());
            m.put("username", userNames.getOrDefault(r.getUserId(), "未知用户"));
            m.put("foodName", r.getFoodName());
            m.put("mealType", r.getMealType());
            m.put("imageUrl", r.getImageUrl());
            m.put("calories", r.getCalories());
            m.put("likeCount", likeCounts.getOrDefault(r.getId(), 0L));
            m.put("commentCount", commentCounts.getOrDefault(r.getId(), 0L));
            m.put("liked", likedByMe.contains(r.getId()));
            m.put("createdAt", r.getCreatedAt().toString());
            return m;
        }).collect(Collectors.toList()));
        return resp;
    }

    /** 点赞/取消（need.md 3.8.2）：已赞则取消，未赞则新增 */
    @Transactional
    public Map<String, Object> toggleLike(Long userId, Long recordId) {
        FoodRecord record = recordService.getPublic(recordId); // 私密记录不可赞
        Optional<LikeRecord> existing = likeRepo.findByUserIdAndRecordId(userId, recordId);

        boolean liked;
        if (existing.isPresent()) {
            likeRepo.delete(existing.get());
            liked = false;
        } else {
            LikeRecord like = new LikeRecord();
            like.setUserId(userId);
            like.setRecordId(recordId);
            likeRepo.save(like);
            liked = true;
        }

        Map<String, Object> m = new HashMap<>();
        m.put("recordId", recordId);
        m.put("liked", liked);
        m.put("likeCount", likeRepo.countByRecordId(recordId));
        return m;
    }

    /** 评论列表（need.md 3.8.4）：一级倒序 + 回复正序 */
    public Dtos.CommentResp comments(Long recordId) {
        List<Comment> top = commentRepo.findByRecordIdAndParentIdNullOrderByCreatedAtDesc(recordId);

        Set<Long> userIds = new HashSet<>();
        for (Comment c : top) {
            userIds.add(c.getUserId());
            for (Comment r : commentRepo.findByParentIdOrderByCreatedAtAsc(c.getId())) {
                userIds.add(r.getUserId());
            }
        }
        Map<Long, String> userNames = new HashMap<>();
        if (!userIds.isEmpty()) {
            userRepo.findAllById(userIds).forEach(u -> userNames.put(u.getId(), u.getUsername()));
        }

        List<Map<String, Object>> comments = new ArrayList<>();
        for (Comment c : top) {
            Map<String, Object> m = toCommentMap(c, userNames);
            List<Map<String, Object>> replies = new ArrayList<>();
            for (Comment r : commentRepo.findByParentIdOrderByCreatedAtAsc(c.getId())) {
                Map<String, Object> rm = toCommentMap(r, userNames);
                rm.put("parentId", c.getId());
                replies.add(rm);
            }
            m.put("replies", replies);
            comments.add(m);
        }

        Dtos.CommentResp resp = new Dtos.CommentResp();
        resp.setComments(comments);
        return resp;
    }

    /** 发表评论（need.md 3.8.3）：分楼校验，最多两层 */
    public Map<String, Object> addComment(Long userId, Dtos.CommentReq req) {
        recordService.getPublic(req.getRecordId()); // 私密记录不可评

        if (req.getContent() == null || req.getContent().trim().isEmpty()) {
            throw new BusinessException(400, "评论内容不能为空");
        }

        Comment c = new Comment();
        c.setRecordId(req.getRecordId());
        c.setUserId(userId);
        c.setContent(req.getContent().trim());
        if (req.getParentId() != null) {
            Comment parent = commentRepo.findById(req.getParentId())
                    .orElseThrow(() -> new BusinessException(404, "父评论不存在"));
            if (parent.getParentId() != null) {
                throw new BusinessException(400, "最多两层评论，不能回复二级回复");
            }
            c.setParentId(parent.getId());
        }
        c = commentRepo.save(c);

        Map<String, Object> m = new HashMap<>();
        m.put("commentId", c.getId());
        m.put("content", c.getContent());
        m.put("createdAt", c.getCreatedAt().toString());
        return m;
    }

    /** 删除评论（need.md 3.8.5）：仅本人；删一级评论时回复一并删除 */
    @Transactional
    public void deleteComment(Long userId, Long commentId) {
        Comment c = commentRepo.findById(commentId)
                .orElseThrow(() -> new BusinessException(404, "评论不存在"));
        if (!c.getUserId().equals(userId)) {
            throw new BusinessException(403, "只能删除自己的评论");
        }
        if (c.getParentId() == null) {
            commentRepo.deleteByParentId(c.getId()); // 级联删回复
        }
        commentRepo.delete(c);
    }

    private Map<String, Object> toCommentMap(Comment c, Map<Long, String> userNames) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("commentId", c.getId());
        m.put("userId", c.getUserId());
        m.put("username", userNames.getOrDefault(c.getUserId(), "未知用户"));
        m.put("content", c.getContent());
        m.put("createdAt", c.getCreatedAt().toString());
        return m;
    }

    private Map<Long, Long> likeMap(List<FoodRecord> records) {
        List<Long> ids = records.stream().map(FoodRecord::getId).collect(Collectors.toList());
        if (ids.isEmpty()) return Collections.emptyMap();
        return likeRepo.findByRecordIdIn(ids).stream()
                .collect(Collectors.groupingBy(LikeRecord::getRecordId, Collectors.counting()));
    }
}
