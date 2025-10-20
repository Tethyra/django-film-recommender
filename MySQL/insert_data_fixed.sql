-- MySQL数据插入脚本（修复版）- Django影视推荐系统

-- 使用数据库
USE film_recommender;

-- 1. 插入默认站点数据
INSERT IGNORE INTO django_site (domain, name) VALUES 
('example.com', 'example.com'),
('localhost:8000', 'localhost:8000');

-- 2. 插入内容类型数据（使用INSERT IGNORE避免重复）
INSERT IGNORE INTO django_content_type (app_label, model) VALUES
('admin', 'logentry'),
('auth', 'group'),
('auth', 'permission'),
('auth', 'user'),
('contenttypes', 'contenttype'),
('main', 'category'),
('main', 'favorite'),
('main', 'film'),
('main', 'review'),
('main', 'userprofile'),
('main', 'watchhistory'),
('sessions', 'session'),
('sites', 'site');

-- 3. 插入初始迁移记录
INSERT IGNORE INTO django_migrations (app, name, applied) VALUES
('contenttypes', '0001_initial', NOW()),
('auth', '0001_initial', NOW()),
('admin', '0001_initial', NOW()),
('admin', '0002_logentry_remove_auto_add', NOW()),
('admin', '0003_logentry_add_action_flag_choices', NOW()),
('contenttypes', '0002_remove_content_type_name', NOW()),
('auth', '0002_alter_permission_name_max_length', NOW()),
('auth', '0003_alter_user_email_max_length', NOW()),
('auth', '0004_alter_user_username_opts', NOW()),
('auth', '0005_alter_user_last_login_null', NOW()),
('auth', '0006_require_contenttypes_0002', NOW()),
('auth', '0007_alter_validators_add_error_messages', NOW()),
('auth', '0008_alter_user_username_max_length', NOW()),
('auth', '0009_alter_user_last_name_max_length', NOW()),
('auth', '0010_alter_group_name_max_length', NOW()),
('auth', '0011_update_proxy_permissions', NOW()),
('auth', '0012_alter_user_first_name_max_length', NOW()),
('sessions', '0001_initial', NOW()),
('sites', '0001_initial', NOW()),
('sites', '0002_alter_domain_unique', NOW());

-- 4. 插入影视分类数据
INSERT IGNORE INTO main_category (name, description) VALUES
('电影', '电影作品'),
('电视剧', '电视剧作品'),
('动画', '动画作品'),
('纪录片', '纪录片作品'),
('综艺', '综艺节目'),
('短片', '短片作品'),
('动作片', '动作类电影'),
('喜剧片', '喜剧类电影'),
('爱情片', '爱情类电影'),
('科幻片', '科幻类电影'),
('恐怖片', '恐怖类电影'),
('悬疑片', '悬疑类电影'),
('文艺片', '文艺类电影'),
('国产剧', '中国大陆电视剧'),
('美剧', '美国电视剧'),
('英剧', '英国电视剧'),
('日剧', '日本电视剧'),
('韩剧', '韩国电视剧'),
('古装剧', '古代服装电视剧'),
('现代剧', '现代背景电视剧'),
('悬疑剧', '悬疑类电视剧'),
('日本动画', '日本制作的动画'),
('美国动画', '美国制作的动画'),
('国产动画', '中国大陆制作的动画'),
('剧场版', '动画电影'),
('TV版', '电视动画'),
('真人秀', '真人参与的综艺节目'),
('访谈节目', '访谈类节目'),
('音乐节目', '音乐类节目'),
('游戏节目', '游戏类节目'),
('经典片', '经典影视作品'),
('新片', '最新上映作品');

-- 5. 插入影视作品数据
INSERT IGNORE INTO main_film (title, director, actors, release_date, description, rating, rating_count) VALUES
-- 经典电影
('肖申克的救赎', '弗兰克·德拉邦特', '蒂姆·罗宾斯,摩根·弗里曼', '1994-09-10', '银行家安迪被冤枉杀害妻子入狱，在肖申克监狱中寻找自由的故事。', 9.7, 10000),
('霸王别姬', '陈凯歌', '张国荣,张丰毅,巩俐', '1993-01-01', '两位京剧演员半个世纪的悲欢离合，见证了时代的变迁。', 9.6, 8000),
('阿甘正传', '罗伯特·泽米吉斯', '汤姆·汉克斯,罗宾·怀特', '1994-07-06', '智商不高的阿甘通过努力成为人生赢家的励志故事。', 9.5, 9000),
('泰坦尼克号', '詹姆斯·卡梅隆', '莱昂纳多·迪卡普里奥,凯特·温丝莱特', '1997-12-19', '穷画家杰克和贵族小姐露丝在泰坦尼克号上的爱情故事。', 9.4, 12000),
('复仇者联盟4：终局之战', '安东尼·罗素,乔·罗素', '小罗伯特·唐尼,克里斯·埃文斯,马克·鲁弗洛', '2019-04-24', '复仇者联盟为了拯救宇宙与灭霸的最终决战。', 9.2, 14000),
('盗梦空间', '克里斯托弗·诺兰', '莱昂纳多·迪卡普里奥,约瑟夫·高登-莱维特,艾伦·佩吉', '2010-07-16', '通过梦境窃取和植入信息的科幻动作片。', 9.3, 11000),
('星际穿越', '克里斯托弗·诺兰', '马修·麦康纳,安妮·海瑟薇,杰西卡·查斯坦', '2014-11-07', '宇航员穿越虫洞寻找人类新家园的故事。', 9.3, 10000),
('楚门的世界', '彼得·威尔', '金·凯瑞,劳拉·琳妮,艾德·哈里斯', '1998-06-05', '楚门发现自己生活在一个被控制的虚假世界中。', 9.3, 8000),
('黑客帝国', '莉莉·沃卓斯基,拉娜·沃卓斯基', '基努·里维斯,劳伦斯·菲什伯恩,凯莉·安·摩丝', '1999-03-31', '尼奥发现世界是由机器控制的虚拟现实。', 9.2, 12000),
('当幸福来敲门', '加布里尔·穆奇诺', '威尔·史密斯,贾登·史密斯,桑迪·牛顿', '2006-12-15', '推销员克里斯·加德纳为了儿子努力奋斗的真实故事。', 9.1, 9000),
('指环王：王者归来', '彼得·杰克逊', '伊利亚·伍德,西恩·奥斯汀,维果·莫腾森', '2003-12-17', '弗罗多完成销毁魔戒使命的最终章。', 9.3, 10000),
('阿凡达', '詹姆斯·卡梅隆', '萨姆·沃辛顿,佐伊·索尔达娜,西格妮·韦弗', '2009-12-18', '人类在潘多拉星球与纳美人的冲突故事。', 9.1, 13000),

-- 热门电视剧
('权力的游戏', '戴维·贝尼奥夫,D·B·威斯', '基特·哈灵顿,艾米莉亚·克拉克,彼特·丁拉基', '2011-04-17', '九个家族争夺铁王座的史诗奇幻故事。', 9.5, 15000),
('绝命毒师', '文斯·吉利甘', '布莱恩·克兰斯顿,亚伦·保尔', '2008-01-20', '高中化学老师变成毒品制造商的犯罪故事。', 9.5, 11000),
('老友记', '大卫·克拉尼,玛尔塔·考夫曼', '詹妮弗·安妮斯顿,柯特妮·考克斯,丽莎·库卓', '1994-09-22', '六个好朋友在纽约的生活故事。', 9.4, 13000),
('黑镜', '查理·布鲁克', '托比·凯贝尔,汤姆·库伦,杰西卡·布朗·芬德利', '2011-12-04', '探讨科技对人类社会影响的科幻剧集。', 9.3, 8000),

-- 动画作品
('千与千寻', '宫崎骏', '柊瑠美,入野自由,夏木真理', '2001-07-20', '少女千寻在神灵世界的奇妙冒险。', 9.4, 12000),
('疯狂动物城', '拜伦·霍华德,瑞奇·摩尔', '金妮弗·古德温,杰森·贝特曼', '2016-03-04', '兔子朱迪成为动物城第一个兔子警察的故事。', 9.2, 8000),
('你的名字。', '新海诚', '神木隆之介,上白石萌音', '2016-08-26', '两个陌生人在梦中交换身体的奇幻爱情故事。', 9.1, 10000),
('进击的巨人', '荒木哲郎,小林靖子', '梶裕贵,石川由依,井上麻里奈', '2013-04-07', '人类对抗巨人的生存战斗故事。', 9.2, 9000);

-- 6. 为影视作品分配分类（使用存储过程方式更安全）
DELIMITER //
CREATE PROCEDURE AssignCategories()
BEGIN
    -- 肖申克的救赎 - 电影,剧情片,经典片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '肖申克的救赎' AND c.name IN ('电影', '文艺片', '经典片');
    
    -- 霸王别姬 - 电影,文艺片,经典片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '霸王别姬' AND c.name IN ('电影', '文艺片', '经典片');
    
    -- 阿甘正传 - 电影,文艺片,经典片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '阿甘正传' AND c.name IN ('电影', '文艺片', '经典片');
    
    -- 泰坦尼克号 - 电影,爱情片,经典片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '泰坦尼克号' AND c.name IN ('电影', '爱情片', '经典片');
    
    -- 复仇者联盟4 - 电影,科幻片,动作片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '复仇者联盟4：终局之战' AND c.name IN ('电影', '科幻片', '动作片');
    
    -- 盗梦空间 - 电影,科幻片,动作片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '盗梦空间' AND c.name IN ('电影', '科幻片', '动作片');
    
    -- 星际穿越 - 电影,科幻片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '星际穿越' AND c.name IN ('电影', '科幻片');
    
    -- 楚门的世界 - 电影,文艺片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '楚门的世界' AND c.name IN ('电影', '文艺片');
    
    -- 黑客帝国 - 电影,科幻片,动作片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '黑客帝国' AND c.name IN ('电影', '科幻片', '动作片');
    
    -- 当幸福来敲门 - 电影,文艺片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '当幸福来敲门' AND c.name IN ('电影', '文艺片');
    
    -- 指环王 - 电影,科幻片,动作片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '指环王：王者归来' AND c.name IN ('电影', '科幻片', '动作片');
    
    -- 阿凡达 - 电影,科幻片,动作片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '阿凡达' AND c.name IN ('电影', '科幻片', '动作片');
    
    -- 权力的游戏 - 电视剧,美剧,悬疑剧
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '权力的游戏' AND c.name IN ('电视剧', '美剧', '悬疑剧');
    
    -- 绝命毒师 - 电视剧,美剧,悬疑剧
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '绝命毒师' AND c.name IN ('电视剧', '美剧', '悬疑剧');
    
    -- 老友记 - 电视剧,美剧
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '老友记' AND c.name IN ('电视剧', '美剧');
    
    -- 黑镜 - 电视剧,英剧,科幻片
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '黑镜' AND c.name IN ('电视剧', '英剧', '科幻片');
    
    -- 千与千寻 - 动画,日本动画,剧场版
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '千与千寻' AND c.name IN ('动画', '日本动画', '剧场版');
    
    -- 疯狂动物城 - 动画,美国动画,剧场版
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '疯狂动物城' AND c.name IN ('动画', '美国动画', '剧场版');
    
    -- 你的名字。 - 动画,日本动画,剧场版
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '你的名字。' AND c.name IN ('动画', '日本动画', '剧场版');
    
    -- 进击的巨人 - 动画,日本动画,TV版
    INSERT IGNORE INTO main_film_categories (film_id, category_id)
    SELECT f.id, c.id FROM main_film f, main_category c
    WHERE f.title = '进击的巨人' AND c.name IN ('动画', '日本动画', 'TV版');
    
    SELECT '分类分配完成' AS message;
END //
DELIMITER ;

-- 执行分类分配
CALL AssignCategories();

-- 删除临时存储过程
DROP PROCEDURE IF EXISTS AssignCategories;

-- 打印插入成功信息
SELECT '示例数据插入完成！' AS message;
SELECT 
    (SELECT COUNT(*) FROM main_category) AS category_count,
    (SELECT COUNT(*) FROM main_film) AS film_count,
    (SELECT COUNT(*) FROM main_film_categories) AS film_category_count;