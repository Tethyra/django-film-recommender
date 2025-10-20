-- MySQL数据库管理脚本 - Django影视推荐系统

-- 使用数据库
USE film_recommender;

-- =============================================
-- 数据库管理功能集合
-- =============================================

-- 1. 数据统计功能
DELIMITER //
CREATE PROCEDURE GetDatabaseStats()
BEGIN
    SELECT '数据库统计信息' AS '=== 统计报告 ===';
    
    -- 基础统计
    SELECT 
        (SELECT COUNT(*) FROM auth_user) AS '用户总数',
        (SELECT COUNT(*) FROM main_film) AS '影视作品总数',
        (SELECT COUNT(*) FROM main_category) AS '分类总数',
        (SELECT COUNT(*) FROM main_review) AS '评论总数',
        (SELECT COUNT(*) FROM main_favorite) AS '收藏总数',
        (SELECT COUNT(*) FROM main_watchhistory) AS '观看记录总数';
    
    -- 按分类统计作品数量
    SELECT '按分类统计' AS '=== 分类统计 ===';
    SELECT c.name AS '分类名称', COUNT(fc.film_id) AS '作品数量'
    FROM main_category c
    LEFT JOIN main_film_categories fc ON c.id = fc.category_id
    GROUP BY c.name
    ORDER BY COUNT(fc.film_id) DESC;
    
    -- 评分统计
    SELECT '评分分布' AS '=== 评分统计 ===';
    SELECT 
        CASE 
            WHEN rating >= 9.5 THEN '9.5-10.0 (经典)'
            WHEN rating >= 9.0 THEN '9.0-9.4 (优秀)'
            WHEN rating >= 8.0 THEN '8.0-8.9 (良好)'
            WHEN rating >= 7.0 THEN '7.0-7.9 (一般)'
            ELSE '7.0以下 (较差)'
        END AS '评分区间',
        COUNT(*) AS '作品数量'
    FROM main_film
    GROUP BY 
        CASE 
            WHEN rating >= 9.5 THEN '9.5-10.0 (经典)'
            WHEN rating >= 9.0 THEN '9.0-9.4 (优秀)'
            WHEN rating >= 8.0 THEN '8.0-8.9 (良好)'
            WHEN rating >= 7.0 THEN '7.0-7.9 (一般)'
            ELSE '7.0以下 (较差)'
        END
    ORDER BY COUNT(*) DESC;
    
    -- 用户活跃度统计
    SELECT '用户活跃度' AS '=== 用户统计 ===';
    SELECT u.username AS '用户名',
           COUNT(DISTINCT r.id) AS '评论数',
           COUNT(DISTINCT fav.id) AS '收藏数',
           COUNT(DISTINCT wh.id) AS '观看数',
           (COUNT(DISTINCT r.id) + COUNT(DISTINCT fav.id) + COUNT(DISTINCT wh.id)) AS '总活跃度'
    FROM auth_user u
    LEFT JOIN main_review r ON u.id = r.user_id
    LEFT JOIN main_favorite fav ON u.id = fav.user_id
    LEFT JOIN main_watchhistory wh ON u.id = wh.user_id
    GROUP BY u.id
    ORDER BY (COUNT(DISTINCT r.id) + COUNT(DISTINCT fav.id) + COUNT(DISTINCT wh.id)) DESC;
    
END //
DELIMITER ;

-- 2. 用户管理功能
DELIMITER //
CREATE PROCEDURE CreateUser(
    IN p_username VARCHAR(150),
    IN p_email VARCHAR(254),
    IN p_password VARCHAR(128),
    IN p_bio TEXT,
    IN p_birth_date DATE,
    IN p_favorite_categories VARCHAR(200)
)
BEGIN
    DECLARE user_id INT;
    
    -- 创建用户
    INSERT INTO auth_user (
        username, email, password, first_name, last_name, 
        is_active, is_staff, is_superuser, date_joined
    ) VALUES (
        p_username, p_email, p_password, '', '', 
        1, 0, 0, NOW()
    );
    
    SET user_id = LAST_INSERT_ID();
    
    -- 创建用户资料
    INSERT INTO main_userprofile (
        user_id, bio, birth_date, favorite_categories
    ) VALUES (
        user_id, p_bio, p_birth_date, p_favorite_categories
    );
    
    SELECT '用户创建成功' AS message, user_id AS user_id;
    
END //
DELIMITER ;

-- 3. 影视管理功能
DELIMITER //
CREATE PROCEDURE AddFilm(
    IN p_title VARCHAR(200),
    IN p_director VARCHAR(200),
    IN p_actors VARCHAR(500),
    IN p_release_date DATE,
    IN p_description TEXT,
    IN p_rating FLOAT,
    IN p_rating_count INT,
    IN p_category_names VARCHAR(500)
)
BEGIN
    DECLARE film_id INT;
    DECLARE category_id INT;
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR 
        SELECT id FROM main_category 
        WHERE FIND_IN_SET(name, REPLACE(p_category_names, ', ', ','));
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- 创建电影
    INSERT INTO main_film (
        title, director, actors, release_date, 
        description, rating, rating_count
    ) VALUES (
        p_title, p_director, p_actors, p_release_date,
        p_description, p_rating, p_rating_count
    );
    
    SET film_id = LAST_INSERT_ID();
    
    -- 分配分类
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO category_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        INSERT INTO main_film_categories (film_id, category_id)
        VALUES (film_id, category_id);
        
    END LOOP;
    
    CLOSE cur;
    
    SELECT '电影添加成功' AS message, film_id AS film_id;
    
END //
DELIMITER ;

-- 4. 互动功能
DELIMITER //
CREATE PROCEDURE AddReview(
    IN p_user_id INT,
    IN p_film_id INT,
    IN p_rating INT,
    IN p_content TEXT
)
BEGIN
    DECLARE avg_rating FLOAT;
    DECLARE total_reviews INT;
    
    -- 检查用户和电影是否存在
    IF NOT EXISTS (SELECT id FROM auth_user WHERE id = p_user_id) THEN
        SELECT '用户不存在' AS error;
        LEAVE;
    END IF;
    
    IF NOT EXISTS (SELECT id FROM main_film WHERE id = p_film_id) THEN
        SELECT '电影不存在' AS error;
        LEAVE;
    END IF;
    
    -- 检查是否已评论过
    IF EXISTS (SELECT id FROM main_review WHERE user_id = p_user_id AND film_id = p_film_id) THEN
        SELECT '您已经评论过这部电影' AS error;
        LEAVE;
    END IF;
    
    -- 添加评论
    INSERT INTO main_review (user_id, film_id, rating, content)
    VALUES (p_user_id, p_film_id, p_rating, p_content);
    
    -- 更新电影评分
    SELECT AVG(rating) INTO avg_rating FROM main_review WHERE film_id = p_film_id;
    SELECT COUNT(*) INTO total_reviews FROM main_review WHERE film_id = p_film_id;
    
    UPDATE main_film
    SET rating = avg_rating, rating_count = total_reviews
    WHERE id = p_film_id;
    
    SELECT '评论添加成功' AS message;
    
END //
DELIMITER ;

-- 5. 收藏功能
DELIMITER //
CREATE PROCEDURE ToggleFavorite(
    IN p_user_id INT,
    IN p_film_id INT
)
BEGIN
    -- 检查用户和电影是否存在
    IF NOT EXISTS (SELECT id FROM auth_user WHERE id = p_user_id) THEN
        SELECT '用户不存在' AS error;
        LEAVE;
    END IF;
    
    IF NOT EXISTS (SELECT id FROM main_film WHERE id = p_film_id) THEN
        SELECT '电影不存在' AS error;
        LEAVE;
    END IF;
    
    -- 检查是否已收藏
    IF EXISTS (SELECT id FROM main_favorite WHERE user_id = p_user_id AND film_id = p_film_id) THEN
        -- 取消收藏
        DELETE FROM main_favorite WHERE user_id = p_user_id AND film_id = p_film_id;
        SELECT '取消收藏成功' AS message, 'removed' AS status;
    ELSE
        -- 添加收藏
        INSERT INTO main_favorite (user_id, film_id)
        VALUES (p_user_id, p_film_id);
        SELECT '收藏成功' AS message, 'added' AS status;
    END IF;
    
END //
DELIMITER ;

-- 6. 观看历史功能
DELIMITER //
CREATE PROCEDURE AddWatchHistory(
    IN p_user_id INT,
    IN p_film_id INT,
    IN p_watch_time DATETIME
)
BEGIN
    -- 检查用户和电影是否存在
    IF NOT EXISTS (SELECT id FROM auth_user WHERE id = p_user_id) THEN
        SELECT '用户不存在' AS error;
        LEAVE;
    END IF;
    
    IF NOT EXISTS (SELECT id FROM main_film WHERE id = p_film_id) THEN
        SELECT '电影不存在' AS error;
        LEAVE;
    END IF;
    
    -- 添加观看记录
    INSERT INTO main_watchhistory (user_id, film_id, watch_time)
    VALUES (p_user_id, p_film_id, p_watch_time);
    
    SELECT '观看记录添加成功' AS message;
    
END //
DELIMITER ;

-- 7. 搜索功能
DELIMITER //
CREATE PROCEDURE SearchFilms(
    IN p_query VARCHAR(255)
)
BEGIN
    SET @search_term = CONCAT('%', p_query, '%');
    
    -- 多字段搜索
    SELECT f.*, GROUP_CONCAT(c.name) AS categories
    FROM main_film f
    LEFT JOIN main_film_categories fc ON f.id = fc.film_id
    LEFT JOIN main_category c ON fc.category_id = c.id
    WHERE 
        f.title LIKE @search_term
        OR f.director LIKE @search_term
        OR f.actors LIKE @search_term
        OR f.description LIKE @search_term
        OR EXISTS (
            SELECT 1 FROM main_category c2 
            JOIN main_film_categories fc2 ON c2.id = fc2.category_id
            WHERE fc2.film_id = f.id AND c2.name LIKE @search_term
        )
    GROUP BY f.id
    ORDER BY f.rating DESC;
    
END //
DELIMITER ;

-- 8. 推荐功能
DELIMITER //
CREATE PROCEDURE GetRecommendations(
    IN p_user_id INT,
    IN p_limit INT
)
BEGIN
    -- 基于用户收藏的推荐
    SELECT '基于收藏的推荐' AS '=== 推荐结果 ===';
    SELECT f.*, COUNT(*) AS recommend_score
    FROM main_favorite fav
    JOIN main_film_categories fc ON fav.film_id = fc.film_id
    JOIN main_film_categories fc2 ON fc.category_id = fc2.category_id
    JOIN main_film f ON fc2.film_id = f.id
    WHERE fav.user_id = p_user_id
      AND f.id NOT IN (SELECT film_id FROM main_favorite WHERE user_id = p_user_id)
    GROUP BY f.id
    ORDER BY COUNT(*) DESC, f.rating DESC
    LIMIT p_limit;
    
    -- 热门推荐
    SELECT '热门推荐' AS '=== 热门推荐 ===';
    SELECT * FROM main_film
    WHERE rating_count >= 500
    ORDER BY rating DESC, rating_count DESC
    LIMIT p_limit;
    
    -- 最新推荐
    SELECT '最新推荐' AS '=== 最新推荐 ===';
    SELECT * FROM main_film
    ORDER BY release_date DESC
    LIMIT p_limit;
    
END //
DELIMITER ;

-- 9. 数据清理功能
DELIMITER //
CREATE PROCEDURE CleanupDatabase(
    IN p_keep_months INT
)
BEGIN
    DECLARE cutoff_date DATE;
    SET cutoff_date = DATE_SUB(NOW(), INTERVAL p_keep_months MONTH);
    
    -- 清理旧的观看记录
    DELETE FROM main_watchhistory WHERE watch_time < cutoff_date;
    
    -- 清理过期会话
    DELETE FROM django_session WHERE expire_date < NOW();
    
    -- 优化表
    OPTIMIZE TABLE main_watchhistory, django_session;
    
    SELECT CONCAT('数据清理完成，保留了最近 ', p_keep_months, ' 个月的数据') AS message;
    
END //
DELIMITER ;

-- 10. 备份功能 (生成备份SQL语句)
DELIMITER //
CREATE PROCEDURE GenerateBackupScript()
BEGIN
    SELECT '生成备份脚本建议：' AS message;
    SELECT CONCAT('mysqldump -u username -p film_recommender > backup_', DATE_FORMAT(NOW(), '%Y%m%d_%H%i%s'), '.sql') AS backup_command;
    SELECT '建议定期执行备份以防止数据丢失' AS note;
END //
DELIMITER ;

-- 打印创建成功信息
SELECT '数据库管理存储过程创建完成！' AS message;
SELECT '可用的存储过程：' AS '=== 存储过程列表 ===';
SELECT '1. GetDatabaseStats() - 数据库统计信息';
SELECT '2. CreateUser(...) - 创建用户';
SELECT '3. AddFilm(...) - 添加电影';
SELECT '4. AddReview(...) - 添加评论';
SELECT '5. ToggleFavorite(...) - 收藏/取消收藏';
SELECT '6. AddWatchHistory(...) - 添加观看记录';
SELECT '7. SearchFilms(...) - 搜索电影';
SELECT '8. GetRecommendations(...) - 获取推荐';
SELECT '9. CleanupDatabase(...) - 数据清理';
SELECT '10. GenerateBackupScript() - 生成备份脚本';