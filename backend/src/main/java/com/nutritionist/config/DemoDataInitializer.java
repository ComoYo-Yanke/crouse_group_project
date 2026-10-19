package com.nutritionist.config;

import com.nutritionist.entity.Comment;
import com.nutritionist.entity.FoodRecord;
import com.nutritionist.entity.LikeRecord;
import com.nutritionist.entity.User;
import com.nutritionist.repo.CommentRepository;
import com.nutritionist.repo.FoodRecordRepository;
import com.nutritionist.repo.LikeRepository;
import com.nutritionist.repo.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDate;

/**
 * 演示数据：两个用户 + 若干公开记录 + 点赞评论
 * 账号：demo / 123456，xiaoming / 123456
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DemoDataInitializer implements CommandLineRunner {

    private final UserRepository userRepo;
    private final FoodRecordRepository recordRepo;
    private final LikeRepository likeRepo;
    private final CommentRepository commentRepo;

    @Override
    public void run(String... args) {
        if (userRepo.count() > 0) {
            return; // 已有数据则跳过
        }

        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

        User demo = new User();
        demo.setUsername("demo");
        demo.setPassword(encoder.encode("123456"));
        demo.setHeight(175.0);
        demo.setWeight(70.0);
        demo.setAge(22);
        demo.setGender("男");
        demo.setGoal("减脂");
        demo.setAvoid("香菜");
        demo.setAllergy("花生");
        userRepo.save(demo);

        User xiaoming = new User();
        xiaoming.setUsername("xiaoming");
        xiaoming.setPassword(encoder.encode("123456"));
        xiaoming.setHeight(165.0);
        xiaoming.setWeight(55.0);
        xiaoming.setAge(21);
        xiaoming.setGender("女");
        xiaoming.setGoal("增肌");
        userRepo.save(xiaoming);

        LocalDate today = LocalDate.now();
        LocalDate yesterday = today.minusDays(1);

        FoodRecord r1 = saveRecord(demo.getId(), "鸡胸肉沙拉", "1 份", "午餐", 350.0, 38.0, 8.0, 25.0, 6.0, 400.0, "public", today);
        FoodRecord r2 = saveRecord(demo.getId(), "燕麦牛奶", "1 碗", "早餐", 280.0, 12.0, 6.0, 45.0, 5.0, 120.0, "public", today);
        saveRecord(demo.getId(), "薯条汉堡", "1 份", "晚餐", 780.0, 22.0, 38.0, 85.0, 4.0, 900.0, "private", yesterday);
        FoodRecord r4 = saveRecord(xiaoming.getId(), "番茄牛肉面", "1 碗", "午餐", 520.0, 26.0, 12.0, 78.0, 4.0, 850.0, "public", today);
        saveRecord(xiaoming.getId(), "水煮蛋 + 全麦面包", "2 个 + 2 片", "早餐", 320.0, 18.0, 10.0, 40.0, 6.0, 350.0, "public", yesterday);

        // 点赞
        saveLike(xiaoming.getId(), r1.getId());
        saveLike(xiaoming.getId(), r2.getId());

        // 评论（分楼）
        Comment c1 = saveComment(r1.getId(), xiaoming.getId(), null, "看着好健康！蛋白质拉满了 💪");
        saveComment(r1.getId(), demo.getId(), c1.getId(), "谢谢！减脂期的经典搭配");
        saveComment(r1.getId(), xiaoming.getId(), c1.getId(), "求沙拉酱配方～");
        saveComment(r4.getId(), demo.getId(), null, "碳水有点高哦，注意搭配蔬菜");

        log.info("演示数据已初始化：demo/123456, xiaoming/123456");
    }

    private FoodRecord saveRecord(Long userId, String foodName, String portion, String mealType,
                                  Double cal, Double protein, Double fat, Double carbs, Double fiber,
                                  Double sodium, String visibility, LocalDate date) {
        FoodRecord r = new FoodRecord();
        r.setUserId(userId);
        r.setFoodName(foodName);
        r.setPortion(portion);
        r.setMealType(mealType);
        r.setCalories(cal);
        r.setProtein(protein);
        r.setFat(fat);
        r.setCarbs(carbs);
        r.setFiber(fiber);
        r.setSodium(sodium);
        r.setVisibility(visibility);
        r.setRecordDate(date);
        r.setConfidence(0.92);
        return recordRepo.save(r);
    }

    private void saveLike(Long userId, Long recordId) {
        LikeRecord like = new LikeRecord();
        like.setUserId(userId);
        like.setRecordId(recordId);
        likeRepo.save(like);
    }

    private Comment saveComment(Long recordId, Long userId, Long parentId, String content) {
        Comment c = new Comment();
        c.setRecordId(recordId);
        c.setUserId(userId);
        c.setParentId(parentId);
        c.setContent(content);
        return commentRepo.save(c);
    }
}
