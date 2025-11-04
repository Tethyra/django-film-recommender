#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
影视推荐系统数据生成脚本
为排行榜和社区功能添加丰富的数据
"""

import os
import sys
import random
import datetime
from faker import Faker

# 先设置Django环境，然后再导入模型
def setup_django_env():
    """设置Django环境"""
    try:
        project_root = os.path.abspath(os.path.dirname(__file__))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_recommender.settings")
        
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        import django
        django.setup()
        print("✅ Django环境设置成功")
        return True
        
    except Exception as e:
        print(f"❌ Django环境设置失败: {e}")
        return False

# 先设置Django环境
if not setup_django_env():
    print("❌ 无法运行数据生成脚本")
    sys.exit(1)

# 现在可以导入Django模型了
from django.utils import timezone
from django.contrib.auth.models import User
from main.models import Film, Category, Review, Favorite, WatchHistory, UserProfile

class FilmDataGenerator:
    """影视数据生成器"""
    
    def __init__(self):
        self.fake = Faker('zh_CN')
        self.setup_data()
    
    def setup_data(self):
        """设置基础数据"""
        # 影视分类数据
        self.categories = [
            '电影', '电视剧', '动画', '纪录片', '综艺', '动作', '喜剧', '爱情', 
            '科幻', '悬疑', '惊悚', '恐怖', '冒险', '奇幻', '犯罪', '剧情',
            '家庭', '儿童', '音乐', '传记', '历史', '战争', '西部', '灾难',
            '运动', '青春', '励志', '古装', '武侠', '都市', '乡村', '其他'
        ]
        
        # 导演数据
        self.directors = [
            '张艺谋', '冯小刚', '陈凯歌', '李安', '王家卫', '周星驰', '徐克',
            '吴京', '沈腾', '黄渤', '邓超', '王宝强', '刘德华', '梁朝伟', '周润发',
            '克里斯托弗·诺兰', '詹姆斯·卡梅隆', '史蒂文·斯皮尔伯格', '马丁·斯科塞斯',
            '昆汀·塔伦蒂诺', '彼得·杰克逊', '大卫·芬奇'
        ]
        
        # 演员数据
        self.actors = [
            '章子怡', '巩俐', '周迅', '赵薇', '范冰冰', '李冰冰', '杨幂', '刘诗诗',
            '黄晓明', '陈坤', '胡歌', '彭于晏', '吴彦祖', '谢霆锋', '古天乐',
            '莱昂纳多·迪卡普里奥', '布拉德·皮特', '汤姆·克鲁斯', '约翰尼·德普',
            '安吉丽娜·朱莉', '斯嘉丽·约翰逊', '艾玛·沃特森', '詹妮弗·劳伦斯'
        ]
        
        # 电影标题数据
        self.movie_titles = [
            '星际穿越', '盗梦空间', '肖申克的救赎', '阿甘正传', '泰坦尼克号',
            '霸王别姬', '英雄', '卧虎藏龙', '功夫', '喜剧之王',
            '阿凡达', '复仇者联盟', '星球大战', '哈利波特', '指环王',
            '黑客帝国', '变形金刚', '蜘蛛侠', '蝙蝠侠', '超人',
            '速度与激情', '碟中谍', '007', '谍影重重', '古墓丽影',
            '侏罗纪公园', '金刚', '哥斯拉', '大白鲨', '异形',
            '终结者', '机器人总动员', '寻梦环游记', '飞屋环游记', '冰雪奇缘',
            '狮子王', '美女与野兽', '阿拉丁', '小美人鱼', '灰姑娘'
        ]
        
        # 电视剧标题数据
        self.tv_titles = [
            '权力的游戏', '老友记', '生活大爆炸', '绝命毒师', '纸牌屋',
            '越狱', '迷失', '行尸走肉', '吸血鬼日记', '绯闻女孩',
            '甄嬛传', '琅琊榜', '芈月传', '如懿传', '延禧攻略',
            '武林外传', '家有儿女', '爱情公寓', '欢乐颂', '都挺好',
            '庆余年', '长安十二时辰', '陈情令', '锦衣之下', '三生三世十里桃花'
        ]
        
        # 动画标题数据
        self.anime_titles = [
            '火影忍者', '海贼王', '死神', '龙珠', '柯南',
            '进击的巨人', '东京喰种', '刀剑神域', '我的英雄学院', '一拳超人',
            '千与千寻', '龙猫', '哈尔的移动城堡', '幽灵公主', '天空之城',
            '你的名字', '天气之子', '秒速五厘米', '言叶之庭', '声之形',
            '哪吒之魔童降世', '大圣归来', '白蛇：缘起', '姜子牙', '大鱼海棠'
        ]
        
        # 电影描述模板
        self.descriptions = [
            '这是一部{genre}类型的精彩{type}，讲述了{character}在{setting}的故事。影片由{director}执导，{actors}主演，{year}年上映后获得了广泛好评。',
            '{title}是{director}导演的经典作品，{plot}。该片在{year}年{event}，成为{milestone}。',
            '在{background}的时代背景下，{protagonist}面临着{conflict}的挑战。通过{journey}，最终{resolution}。',
            '这部{type}融合了{elements}等元素，以{style}的叙事手法展现了{theme}的深刻主题。',
            '{title}以{unique}的视角，探讨了{issues}等社会问题，引发观众的深思。'
        ]
    
    def generate_category(self):
        """生成分类数据"""
        print("📁 开始生成分类数据...")
        
        created_count = 0
        for name in self.categories:
            if not Category.objects.filter(name=name).exists():
                Category.objects.create(
                    name=name,
                    description=f'{name}类影视作品',
                    created_at=timezone.now()
                )
                created_count += 1
                print(f"   ✅ 创建分类: {name}")
            else:
                print(f"   ⏩ 分类已存在: {name}")
        
        print(f"📊 分类生成完成，新增{created_count}个分类")
    
    def generate_film(self, count=50):
        """生成电影数据"""
        print(f"\n🎬 开始生成电影数据 (目标: {count}部)...")
        
        all_categories = Category.objects.all()
        created_count = 0
        
        for i in range(count):
            # 随机选择影视类型
            media_type = random.choice(['电影', '电视剧', '动画'])
            
            # 根据类型选择标题
            if media_type == '电影':
                title = random.choice(self.movie_titles)
                # 避免重复标题
                if Film.objects.filter(title=title).exists():
                    title = f"{title} ({random.randint(2010, 2024)})"
            elif media_type == '电视剧':
                title = random.choice(self.tv_titles)
                if Film.objects.filter(title=title).exists():
                    title = f"{title} 第{random.randint(1, 10)}季"
            else:  # 动画
                title = random.choice(self.anime_titles)
                if Film.objects.filter(title=title).exists():
                    title = f"{title} 剧场版"
            
            # 检查是否已存在
            if Film.objects.filter(title=title).exists():
                print(f"   ⏩ 电影已存在: {title}")
                continue
            
            # 生成基本信息
            release_year = random.randint(1990, 2024)
            release_date = timezone.datetime(
                release_year, 
                random.randint(1, 12), 
                random.randint(1, 28)
            )
            
            # 选择导演和演员
            director = random.choice(self.directors)
            selected_actors = random.sample(self.actors, k=random.randint(2, 6))
            actors = ', '.join(selected_actors)
            
            # 选择分类（1-3个）
            selected_categories = random.sample(list(all_categories), k=random.randint(1, 3))
            
            # 确保包含主要类型分类
            main_category = Category.objects.filter(name=media_type).first()
            if main_category and main_category not in selected_categories:
                selected_categories.append(main_category)
            
            # 生成描述
            genre = ', '.join([cat.name for cat in selected_categories[:2]])
            description = random.choice(self.descriptions).format(
                genre=genre,
                type=media_type,
                character=self.fake.name(),
                setting=self.fake.city(),
                director=director,
                actors=', '.join(selected_actors[:2]),
                year=release_year,
                title=title,
                plot=self.fake.sentence(nb_words=15),
                event=random.choice(['获得奥斯卡奖', '票房大卖', '口碑爆棚', '成为经典']),
                milestone=random.choice(['影史经典', '票房冠军', '评分最高', '获奖无数']),
                background=self.fake.year(),
                protagonist=self.fake.name(),
                conflict=self.fake.sentence(nb_words=8),
                journey=self.fake.sentence(nb_words=10),
                resolution=random.choice(['实现梦想', '获得成功', '找到真爱', '拯救世界']),
                elements=random.choice(['动作、冒险', '爱情、喜剧', '科幻、悬疑', '恐怖、惊悚']),
                style=random.choice(['独特', '精彩', '感人', '震撼']),
                theme=random.choice(['爱情', '友情', '亲情', '梦想', '成长']),
                unique=random.choice(['独特', '新颖', '创新', '深刻']),
                issues=random.choice(['社会问题', '人性探讨', '价值观', '人生意义'])
            )
            
            # 生成评分和评分人数
            rating = round(random.uniform(6.0, 9.9), 1)
            rating_count = random.randint(100, 100000)
            
            # 创建电影
            film = Film.objects.create(
                title=title,
                director=director,
                actors=actors,
                release_date=release_date,
                description=description,
                rating=rating,
                rating_count=rating_count,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            
            # 添加分类
            film.categories.set(selected_categories)
            
            created_count += 1
            print(f"   ✅ 创建{media_type}: {title} ({rating}分)")
            
            # 进度显示
            if (i + 1) % 10 == 0:
                print(f"   📊 进度: {i + 1}/{count}")
        
        print(f"📊 电影生成完成，新增{created_count}部作品")
    
    def generate_users(self, count=20):
        """生成用户数据"""
        print(f"\n👥 开始生成用户数据 (目标: {count}个)...")
        
        created_count = 0
        
        for i in range(count):
            username = self.fake.user_name()
            email = self.fake.email()
            
            if not User.objects.filter(username=username).exists():
                # 创建用户
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    date_joined=timezone.now() - timezone.timedelta(
                        days=random.randint(1, 365)
                    )
                )
                
                # 创建用户资料
                UserProfile.objects.create(
                    user=user,
                    bio=self.fake.text(max_nb_chars=200),
                    birth_date=self.fake.date_of_birth(minimum_age=18, maximum_age=60),
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                
                created_count += 1
                print(f"   ✅ 创建用户: {username}")
            else:
                print(f"   ⏩ 用户已存在: {username}")
        
        print(f"📊 用户生成完成，新增{created_count}个用户")
    
    def generate_reviews(self, count=200):
        """生成评论数据"""
        print(f"\n💬 开始生成评论数据 (目标: {count}条)...")
        
        films = list(Film.objects.all())
        users = list(User.objects.all())
        
        if not films or not users:
            print("❌ 缺少电影或用户数据，无法生成评论")
            return
        
        created_count = 0
        
        for i in range(count):
            film = random.choice(films)
            user = random.choice(users)
            
            # 避免重复评论（同一用户对同一电影）
            if Review.objects.filter(user=user, film=film).exists():
                continue
            
            # 生成评论内容
            rating = random.randint(1, 5)
            comments = [
                f"这部{self.get_media_type(film)}真的很{random.choice(['好看', '精彩', '棒', '优秀'])}！",
                f"{film.title}是我看过的{random.choice(['最好的', '最棒的', '最精彩的'])}之一。",
                f"演员的表演很{random.choice(['出色', '精彩', '到位', '自然'])}，剧情也很{random.choice(['吸引人', '紧凑', '感人'])}。",
                f"推荐大家去看这部{self.get_media_type(film)}，绝对不会{random.choice(['失望', '后悔'])}的。",
                f"{random.choice(['很棒', '不错', '还行', '一般', '不太好'])}的一部{self.get_media_type(film)}，{random.choice(['值得一看', '可以看看', '不推荐'])}。",
                self.fake.sentence(nb_words=20),
                self.fake.paragraph(nb_sentences=2),
                f"给{rating}分，{random.choice(['推荐', '还可以', '一般般', '不推荐'])}"
            ]
            content = random.choice(comments)
            
            # 生成评论时间（最近一年内）
            created_at = timezone.now() - timezone.timedelta(
                days=random.randint(1, 365)
            )
            
            # 创建评论
            Review.objects.create(
                user=user,
                film=film,
                rating=rating,
                content=content,
                created_at=created_at,
                updated_at=created_at,
                likes=random.randint(0, 50)
            )
            
            created_count += 1
            
            # 更新电影评分
            self.update_film_rating(film)
            
            # 进度显示
            if (i + 1) % 50 == 0:
                print(f"   📊 进度: {i + 1}/{count}")
        
        print(f"📊 评论生成完成，新增{created_count}条评论")
    
    def generate_favorites(self, count=100):
        """生成收藏数据"""
        print(f"\n❤️ 开始生成收藏数据 (目标: {count}个)...")
        
        films = list(Film.objects.all())
        users = list(User.objects.all())
        
        if not films or not users:
            print("❌ 缺少电影或用户数据，无法生成收藏")
            return
        
        created_count = 0
        
        for i in range(count):
            film = random.choice(films)
            user = random.choice(users)
            
            if not Favorite.objects.filter(user=user, film=film).exists():
                Favorite.objects.create(
                    user=user,
                    film=film,
                    created_at=timezone.now() - timezone.timedelta(
                        days=random.randint(1, 365)
                    )
                )
                created_count += 1
                
                # 进度显示
                if (i + 1) % 20 == 0:
                    print(f"   📊 进度: {i + 1}/{count}")
        
        print(f"📊 收藏生成完成，新增{created_count}个收藏")
    
    def generate_watch_history(self, count=150):
        """生成观看历史数据"""
        print(f"\n📺 开始生成观看历史数据 (目标: {count}条)...")
        
        films = list(Film.objects.all())
        users = list(User.objects.all())
        
        if not films or not users:
            print("❌ 缺少电影或用户数据，无法生成观看历史")
            return
        
        created_count = 0
        max_attempts = 3  # 最大尝试次数
        
        while created_count < count and max_attempts > 0:
            film = random.choice(films)
            user = random.choice(users)
            
            # 检查是否已经存在该用户对该电影的观看历史
            if not WatchHistory.objects.filter(user=user, film=film).exists():
                # 创建观看历史
                WatchHistory.objects.create(
                    user=user,
                    film=film,
                    watch_time=timezone.now() - timezone.timedelta(
                        days=random.randint(1, 90)
                    ),
                    watch_duration=random.randint(300, 7200)  # 5分钟到2小时
                )
                
                created_count += 1
                
                # 进度显示
                if created_count % 30 == 0:
                    print(f"   📊 进度: {created_count}/{count}")
            else:
                # 如果已经存在，减少尝试次数
                max_attempts -= 1
        
        # 如果达到最大尝试次数但仍未生成足够的数据
        if created_count < count:
            print(f"   ⚠️  达到最大尝试次数，实际生成了{created_count}条观看历史记录")
            print(f"   💡 建议：增加电影或用户数量，或者修改WatchHistory模型的unique_together约束")
        
        print(f"📊 观看历史生成完成，新增{created_count}条记录")
    
    def get_media_type(self, film):
        """根据分类判断媒体类型"""
        categories = film.categories.all()
        if any(cat.name == '电视剧' for cat in categories):
            return '电视剧'
        elif any(cat.name == '动画' for cat in categories):
            return '动画'
        else:
            return '电影'
    
    def update_film_rating(self, film):
        """更新电影评分"""
        from django.db.models import Avg, Count
        
        result = Review.objects.filter(film=film).aggregate(
            avg_rating=Avg('rating'),
            review_count=Count('id')
        )
        
        if result['avg_rating']:
            film.rating = round(result['avg_rating'], 1)
            film.rating_count = result['review_count']
            film.save()

class RankingDataEnhancer:
    """排行榜数据增强器"""
    
    def __init__(self):
        pass
    
    def enhance_rankings(self):
        """增强排行榜数据"""
        from django.db.models import Avg, Count
        
        print("\n🏆 开始增强排行榜数据...")
        
        # 为每个分类生成排行榜数据
        categories = Category.objects.filter(name__in=['电影', '电视剧', '动画'])
        
        for category in categories:
            # 获取该分类下的电影
            films = Film.objects.filter(categories=category)
            
            if films.count() > 0:
                # 计算平均评分
                films = films.annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews')
                )
                
                # 更新电影评分
                for film in films:
                    if film.avg_rating:
                        film.rating = round(film.avg_rating, 1)
                        film.rating_count = film.review_count
                        film.save()
        
        print("📊 排行榜数据增强完成")

class CommunityDataEnhancer:
    """社区数据增强器"""
    
    def __init__(self):
        pass
    
    def enhance_community(self):
        """增强社区数据"""
        from django.db.models import Count
        
        print("\n🌐 开始增强社区数据...")
        
        # 识别活跃用户
        active_users = User.objects.annotate(
            review_count=Count('reviews')
        ).filter(
            review_count__gt=5
        ).order_by('-review_count')[:10]
        
        print(f"   ✅ 识别出{active_users.count()}个活跃用户")
        
        print("📊 社区数据增强完成")

def main():
    """主函数"""
    print("="*60)
    print("影视推荐系统数据生成器")
    print("为排行榜和社区功能添加丰富的数据")
    print("="*60)
    
    try:
        # 创建数据生成器
        generator = FilmDataGenerator()
        
        # 生成基础数据
        generator.generate_category()
        generator.generate_film(count=100)  # 生成100部电影
        generator.generate_users(count=30)   # 生成30个用户
        
        # 生成互动数据
        generator.generate_reviews(count=500)   # 生成500条评论
        generator.generate_favorites(count=200) # 生成200个收藏
        generator.generate_watch_history(count=300) # 生成300条观看历史
        
        # 增强排行榜数据
        ranking_enhancer = RankingDataEnhancer()
        ranking_enhancer.enhance_rankings()
        
        # 增强社区数据
        community_enhancer = CommunityDataEnhancer()
        community_enhancer.enhance_community()
        
        # 显示统计信息
        print("\n" + "="*60)
        print("数据生成完成统计")
        print("="*60)
        
        print(f"📁 分类数量: {Category.objects.count()}个")
        print(f"🎬 电影数量: {Film.objects.count()}部")
        print(f"👥 用户数量: {User.objects.count()}个")
        print(f"💬 评论数量: {Review.objects.count()}条")
        print(f"❤️ 收藏数量: {Favorite.objects.count()}个")
        print(f"📺 观看历史: {WatchHistory.objects.count()}条")
        
        print("\n🎉 数据生成脚本运行完成！")
        print("\n" + "="*60)
        print("排行榜和社区功能现在拥有丰富的数据：")
        print("="*60)
        print("🏆 排行榜功能：")
        print("   - 评分排行榜")
        print("   - 热门程度排行榜")
        print("   - 新片上映排行榜")
        print("   - 分类排行榜")
        print("\n🌐 社区功能：")
        print("   - 热门讨论")
        print("   - 活跃用户")
        print("   - 用户评论")
        print("   - 电影推荐")
        print("   - 互动功能")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()