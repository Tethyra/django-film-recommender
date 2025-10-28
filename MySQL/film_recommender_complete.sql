-- MySQL数据库导入文件 - film_recommender.sql
-- 适用于Navicat导入

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

-- 1. 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS film_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE film_recommender;

-- 2. 用户表（Django内置）
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
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 影视分类表
CREATE TABLE IF NOT EXISTS main_category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    created_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 影视作品表
CREATE TABLE IF NOT EXISTS main_film (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    director VARCHAR(100) NULL,
    actors VARCHAR(500) NULL,
    release_date DATE NULL,
    description TEXT NULL,
    poster_path VARCHAR(255) NULL,
    rating FLOAT NOT NULL DEFAULT 0,
    rating_count INT NOT NULL DEFAULT 0,
    tmdb_id INT NULL,
    tmdb_rating FLOAT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 电影分类关联表
CREATE TABLE IF NOT EXISTS main_film_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES main_category(id) ON DELETE CASCADE,
    UNIQUE KEY film_category_unique (film_id, category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 用户资料表
CREATE TABLE IF NOT EXISTS main_userprofile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    avatar VARCHAR(100) NULL,
    bio TEXT NULL,
    birth_date DATE NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 用户喜好分类关联表
CREATE TABLE IF NOT EXISTS main_userprofile_favorite_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userprofile_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (userprofile_id) REFERENCES main_userprofile(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES main_category(id) ON DELETE CASCADE,
    UNIQUE KEY user_category_unique (userprofile_id, category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 观看历史表
CREATE TABLE IF NOT EXISTS main_watchhistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    film_id INT NOT NULL,
    watch_time DATETIME NOT NULL,
    watch_duration INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE,
    UNIQUE KEY user_film_unique (user_id, film_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 收藏表
CREATE TABLE IF NOT EXISTS main_favorite (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    film_id INT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE,
    UNIQUE KEY user_film_unique (user_id, film_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 评论表
CREATE TABLE IF NOT EXISTS main_review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    film_id INT NOT NULL,
    rating INT NOT NULL DEFAULT 5,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    likes INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES main_film(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Django会话表
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Django迁移记录表
CREATE TABLE IF NOT EXISTS django_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认数据
INSERT INTO main_category (name, description, created_at) VALUES
('电影', '精彩的电影作品', NOW()),
('电视剧', '热门电视剧集', NOW()),
('动画', '动画电影和剧集', NOW()),
('纪录片', '真实记录的影片', NOW()),
('动作', '动作片', NOW()),
('喜剧', '喜剧片', NOW()),
('爱情', '爱情片', NOW()),
('科幻', '科幻片', NOW()),
('悬疑', '悬疑片', NOW()),
('惊悚', '惊悚片', NOW());

-- 插入测试电影数据
INSERT INTO main_film (title, director, actors, release_date, description, rating, rating_count, created_at, updated_at) VALUES
('星际穿越', '克里斯托弗·诺兰', '马修·麦康纳, 安妮·海瑟薇, 杰西卡·查斯坦', '2014-11-07', '在不久的将来，地球面临着严重的环境危机，粮食短缺威胁着人类的生存。前NASA宇航员库珀（马修·麦康纳饰）被神秘的重力异常现象引导，发现了一个秘密的NASA基地，并加入了一个拯救人类的计划。', 9.3, 10000, NOW(), NOW()),
('盗梦空间', '克里斯托弗·诺兰', '莱昂纳多·迪卡普里奥, 约瑟夫·高登-莱维特, 艾伦·佩吉', '2010-07-16', '多姆·科布（莱昂纳多·迪卡普里奥饰）是一位经验丰富的窃贼，他在人们精神最为脆弱的梦境中活动，窃取潜意识中有价值的信息。', 9.2, 9500, NOW(), NOW()),
('肖申克的救赎', '弗兰克·德拉邦特', '蒂姆·罗宾斯, 摩根·弗里曼', '1994-09-23', '银行家安迪（蒂姆·罗宾斯饰）被冤枉杀害了他的妻子及其情人，被判处无期徒刑，关在肖申克监狱里。在狱中，他结识了“瑞德”（摩根·弗里曼饰），并在监狱中度过了长达19年的时光。', 9.7, 15000, NOW(), NOW()),
('阿甘正传', '罗伯特·泽米吉斯', '汤姆·汉克斯, 罗宾·怀特, 加里·西尼斯', '1994-07-06', '阿甘（汤姆·汉克斯饰）是一个智商只有75的低能儿，但他的母亲总是鼓励他“傻人有傻福”，要他自强不息。阿甘像普通孩子一样上学，并且认识了一生的朋友和至爱珍妮。', 9.5, 12000, NOW(), NOW()),
('泰坦尼克号', '詹姆斯·卡梅隆', '莱昂纳多·迪卡普里奥, 凯特·温丝莱特', '1997-12-19', '1912年4月10日，号称“世界工业史上的奇迹”的豪华客轮泰坦尼克号开始了自己的处女航，从英国的南安普顿出发驶往美国纽约。富家少女露丝（凯特·温丝莱特饰）与母亲及未婚夫卡尔坐上了头等舱。', 9.4, 11000, NOW(), NOW());

-- 关联电影和分类
INSERT INTO main_film_categories (film_id, category_id) VALUES
(1, 1), (1, 8),  -- 星际穿越 - 电影、科幻
(2, 1), (2, 9),  -- 盗梦空间 - 电影、悬疑
(3, 1), (3, 7),  -- 肖申克的救赎 - 电影、爱情
(4, 1), (4, 6),  -- 阿甘正传 - 电影、喜剧
(5, 1), (5, 7);  -- 泰坦尼克号 - 电影、爱情

-- 创建管理员用户（密码：admin123456）
INSERT INTO auth_user (username, email, password, first_name, last_name, is_active, is_staff, is_superuser, date_joined) VALUES
('admin', 'admin@example.com', 'pbkdf2_sha256$390000$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx$yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy=', 'Admin', 'User', 1, 1, 1, NOW());

-- 创建管理员资料
INSERT INTO main_userprofile (user_id, created_at, updated_at) VALUES
(1, NOW(), NOW());

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;

-- 导入完成提示
SELECT '数据库导入完成！' AS message;
SELECT '管理员账号：admin' AS admin_username;
SELECT '管理员密码：admin123456' AS admin_password;
SELECT '请登录后立即修改密码！' AS security_note;