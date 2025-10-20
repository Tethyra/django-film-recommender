-- MySQL数据库脚本（修复版）- Django影视推荐系统

-- 创建数据库
CREATE DATABASE IF NOT EXISTS film_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE film_recommender;

-- 1. 用户表 (Django内置用户表)
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. 用户扩展资料表
CREATE TABLE IF NOT EXISTS main_userprofile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    avatar VARCHAR(100) NULL,
    bio TEXT NULL,
    birth_date DATE NULL,
    favorite_categories VARCHAR(200) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    user_id INT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- 3. 影视分类表
CREATE TABLE IF NOT EXISTS main_category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. 影视作品表
CREATE TABLE IF NOT EXISTS main_film (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    director VARCHAR(200) NOT NULL DEFAULT '',
    actors VARCHAR(500) NOT NULL DEFAULT '',
    release_date DATE NULL,
    description TEXT NULL,
    poster VARCHAR(100) NULL,
    rating FLOAT NOT NULL DEFAULT 0,
    rating_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_title (title)
);

-- 5. 影视-分类关联表 (多对多)
CREATE TABLE IF NOT EXISTS main_film_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES main_category(id) ON DELETE CASCADE,
    UNIQUE KEY unique_film_category (film_id, category_id)
);

-- 6. 观看历史表
CREATE TABLE IF NOT EXISTS main_watchhistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    watch_time DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    film_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_film_time (user_id, film_id, watch_time)
);

-- 7. 收藏记录表
CREATE TABLE IF NOT EXISTS main_favorite (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    film_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_film (user_id, film_id)
);

-- 8. 评论评分表
CREATE TABLE IF NOT EXISTS main_review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    film_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_film_review (user_id, film_id)
);

-- 9. Django迁移记录表
CREATE TABLE IF NOT EXISTS django_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
);

-- 10. Django内容类型表
CREATE TABLE IF NOT EXISTS django_content_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE KEY unique_content_type (app_label, model)
);

-- 11. Django权限表
CREATE TABLE IF NOT EXISTS auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE,
    UNIQUE KEY unique_permission (content_type_id, codename)
);

-- 12. Django用户组表
CREATE TABLE IF NOT EXISTS auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- 13. 用户-组关联表
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_group (user_id, group_id)
);

-- 14. 用户-权限关联表
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_permission (user_id, permission_id)
);

-- 15. Django会话表
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME NOT NULL,
    INDEX idx_session_expire (expire_date)
);

-- 16. Django站点表
CREATE TABLE IF NOT EXISTS django_site (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(100) NOT NULL,
    name VARCHAR(50) NOT NULL
);

-- 创建索引以提高性能
CREATE INDEX idx_film_title ON main_film(title);
CREATE INDEX idx_film_director ON main_film(director);
CREATE INDEX idx_film_actors ON main_film(actors);
CREATE INDEX idx_review_user_id ON main_review(user_id);
CREATE INDEX idx_review_film_id ON main_review(film_id);
CREATE INDEX idx_favorite_user_id ON main_favorite(user_id);
CREATE INDEX idx_watchhistory_user_id ON main_watchhistory(user_id);

-- 打印创建成功信息
SELECT '数据库表结构创建完成！' AS message;