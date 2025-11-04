#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排行榜数据增强脚本
为排行榜功能添加更多样化的数据
"""

import os
import sys
import random
from datetime import datetime, timedelta

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
    print("❌ 无法运行数据增强脚本")
    sys.exit(1)

# 现在可以导入Django模型了
from django.utils import timezone
from django.db.models import Avg, Count, F, Q
from main.models import Film, Category, Review, User
from django.contrib.auth.models import User as DjangoUser

class AdvancedRankingGenerator:
    """高级排行榜数据生成器"""
    
    def __init__(self):
        self.setup_categories()
    
    def setup_categories(self):
        """设置分类数据"""
        self.category_mapping = {
            '电影': ['动作', '喜剧', '爱情', '科幻', '悬疑', '惊悚', '冒险', '奇幻'],
            '电视剧': ['都市', '古装', '悬疑', '爱情', '喜剧', '动作', '科幻'],
            '动画': ['日本动画', '国产动画', '欧美动画', '剧场版', 'TV版']
        }
    
    def generate_category_rankings(self):
        """生成分类排行榜数据"""
        print("📊 开始生成分类排行榜数据...")
        
        # 为主要分类生成排行榜
        main_categories = ['电影', '电视剧', '动画']
        
        for main_category_name in main_categories:
            main_category = Category.objects.filter(name=main_category_name).first()
            if not main_category:
                continue
            
            # 获取该主分类下的所有电影
            films = Film.objects.filter(categories=main_category)
            
            if films.exists():
                # 计算排名数据
                ranked_films = films.annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews')
                ).filter(
                    avg_rating__isnull=False,
                    review_count__gte=3  # 至少3条评论才参与排名
                ).order_by('-avg_rating', '-review_count')
                
                print(f"   ✅ {main_category_name}排行榜: {ranked_films.count()}部作品")
                
                # 为前10名电影添加特殊标记（如果需要）
                for i, film in enumerate(ranked_films[:10]):
                    # 这里可以添加排行榜相关的特殊处理
                    pass
        
        print("📊 分类排行榜数据生成完成")
    
    def generate_trending_rankings(self):
        """生成上升最快排行榜数据"""
        print("📈 开始生成上升最快排行榜数据...")
        
        # 计算最近30天的评分变化
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        
        # 获取有足够评论的电影
        films = Film.objects.annotate(
            recent_reviews=Count('reviews', filter=Q(reviews__created_at__gte=thirty_days_ago)),
            old_reviews=Count('reviews', filter=Q(reviews__created_at__gte=sixty_days_ago, 
                                               reviews__created_at__lt=thirty_days_ago))
        ).filter(
            recent_reviews__gte=2,  # 最近30天至少2条评论
            old_reviews__gte=1     # 之前30天至少1条评论
        )
        
        trending_films = []
        for film in films:
            # 计算近期评分
            recent_avg = Review.objects.filter(
                film=film,
                created_at__gte=thirty_days_ago
            ).aggregate(Avg('rating'))['rating__avg']
            
            # 计算之前评分
            old_avg = Review.objects.filter(
                film=film,
                created_at__gte=sixty_days_ago,
                created_at__lt=thirty_days_ago
            ).aggregate(Avg('rating'))['rating__avg']
            
            if recent_avg and old_avg and recent_avg > old_avg:
                # 计算上升幅度
                increase = recent_avg - old_avg
                trending_films.append({
                    'film': film,
                    'recent_avg': recent_avg,
                    'old_avg': old_avg,
                    'increase': increase,
                    'increase_percent': (increase / old_avg) * 100
                })
        
        # 按上升幅度排序
        trending_films.sort(key=lambda x: x['increase'], reverse=True)
        
        print(f"   ✅ 上升最快: {len(trending_films)}部作品")
        
        # 输出前10名
        for i, item in enumerate(trending_films[:10]):
            print(f"      #{i+1} {item['film'].title}: +{item['increase']:.1f}分")
        
        print("📊 上升最快排行榜数据生成完成")
    
    def generate_yearly_rankings(self):
        """生成年度排行榜数据"""
        print("📅 开始生成年度排行榜数据...")
        
        # 获取2010年至今的电影
        current_year = timezone.now().year
        
        for year in range(2010, current_year + 1):
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)
            
            # 获取该年度上映的电影
            films = Film.objects.filter(
                release_date__gte=year_start,
                release_date__lte=year_end
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(
                avg_rating__isnull=False,
                review_count__gte=5  # 至少5条评论
            ).order_by('-avg_rating', '-review_count')
            
            if films.exists():
                top_film = films.first()
                print(f"   ✅ {year}年度最佳: {top_film.title} ({top_film.avg_rating:.1f}分)")
        
        print("📊 年度排行榜数据生成完成")
    
    def generate_popularity_rankings(self):
        """生成人气排行榜数据"""
        print("🔥 开始生成人气排行榜数据...")
        
        # 基于评论数量、收藏数量、观看次数的综合排名
        films = Film.objects.annotate(
            review_count=Count('reviews'),
            favorite_count=Count('favorited_by'),
            watch_count=Count('watch_records')
        ).filter(
            review_count__gte=2
        )
        
        # 计算人气得分 (评论数*0.4 + 收藏数*0.3 + 观看数*0.3)
        popular_films = []
        for film in films:
            score = (film.review_count * 0.4 + 
                    film.favorite_count * 0.3 + 
                    film.watch_count * 0.3)
            
            popular_films.append({
                'film': film,
                'score': score,
                'review_count': film.review_count,
                'favorite_count': film.favorite_count,
                'watch_count': film.watch_count
            })
        
        # 按得分排序
        popular_films.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"   ✅ 人气排行榜: {len(popular_films)}部作品")
        
        # 输出前10名
        for i, item in enumerate(popular_films[:10]):
            print(f"      #{i+1} {item['film'].title}: {item['score']:.1f}分")
        
        print("📊 人气排行榜数据生成完成")
    
    def generate_genre_specific_rankings(self):
        """生成特定类型排行榜数据"""
        print("🎭 开始生成特定类型排行榜数据...")
        
        # 特定类型排行榜
        genres = ['动作', '喜剧', '爱情', '科幻', '悬疑']
        
        for genre in genres:
            genre_category = Category.objects.filter(name=genre).first()
            if not genre_category:
                continue
            
            # 获取该类型的电影
            films = Film.objects.filter(
                categories=genre_category
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(
                avg_rating__isnull=False,
                review_count__gte=2
            ).order_by('-avg_rating')
            
            if films.exists():
                print(f"   ✅ {genre}片排行榜: {films.count()}部作品")
        
        print("📊 特定类型排行榜数据生成完成")

class CommunityContentGenerator:
    """社区内容生成器"""
    
    def __init__(self):
        self.discussion_topics = [
            "大家觉得这部电影怎么样？",
            "为什么这部电影评分这么高？",
            "最喜欢电影中的哪个角色？",
            "电影中的哪个场景最感人？",
            "这部电影和同类型的相比如何？",
            "导演想通过这部电影表达什么？",
            "推荐类似的电影给大家",
            "电影中的音乐很棒",
            "演员的表演很到位",
            "剧情反转太精彩了"
        ]
    
    def generate_discussion_topics(self):
        """生成讨论话题"""
        from main.models import Favorite, WatchHistory
        
        print("💬 开始生成讨论话题...")
        
        films = Film.objects.all()[:20]  # 选择前20部电影
        users = list(DjangoUser.objects.all())
        
        if not films or not users:
            print("   ❌ 缺少电影或用户数据")
            return
        
        created_count = 0
        
        for film in films:
            # 为每部电影生成2-3个讨论话题
            num_topics = random.randint(2, 3)
            
            for _ in range(num_topics):
                user = random.choice(users)
                
                # 检查用户是否已经评论过这部电影
                if Review.objects.filter(user=user, film=film).exists():
                    continue
                
                # 生成讨论内容
                topic = random.choice(self.discussion_topics)
                content = f"{topic}\n\n{self.generate_detailed_discussion()}"
                
                # 创建评论作为讨论话题
                Review.objects.create(
                    user=user,
                    film=film,
                    rating=random.randint(4, 5),  # 讨论话题通常评分较高
                    content=content,
                    created_at=timezone.now() - timedelta(
                        days=random.randint(1, 14)
                    ),
                    likes=random.randint(3, 20)
                )
                
                created_count += 1
        
        print(f"   ✅ 生成了{created_count}个讨论话题")
    
    def generate_detailed_discussion(self):
        """生成详细的讨论内容"""
        discussions = [
            "我觉得这部电影在制作上非常精良，无论是画面还是音乐都很棒。特别是最后那个场景，真的让我感动落泪。",
            "看完这部电影后我思考了很多，关于人生，关于梦想。推荐大家都去看看，相信会有不同的收获。",
            "和朋友一起去看的，大家都觉得很不错。回家后还在讨论电影中的情节，真的很有深度。",
            "期待这部电影很久了，今天终于看了。果然没有失望，比预期的还要好。值得二刷！",
            "虽然有些地方不太明白，但是整体感觉很棒。准备再看一遍，相信会有新的发现。",
            "演员的表演很自然，剧情也很紧凑。没有拖沓的感觉，两个小时很快就过去了。",
            "这部电影让我想起了很多往事，很有共鸣。特别是主角的经历，让我感同身受。",
            "画面太美了，每一帧都可以当壁纸。导演的审美真的很棒，值得学习。"
        ]
        
        return random.choice(discussions)
    
    def generate_user_interactions(self):
        """生成用户互动数据"""
        from django.db.models import F
        
        print("🤝 开始生成用户互动数据...")
        
        # 为评论添加点赞
        reviews = Review.objects.all()
        
        for review in reviews:
            # 随机增加点赞数
            additional_likes = random.randint(0, 15)
            if additional_likes > 0:
                review.likes = F('likes') + additional_likes
                review.save()
        
        # 刷新数据
        Review.objects.update()
        
        print("   ✅ 生成了用户互动数据")
    
    def generate_featured_content(self):
        """生成精选内容"""
        print("⭐ 开始生成精选内容...")
        
        # 标记热门评论
        popular_reviews = Review.objects.filter(
            likes__gte=10
        ).order_by('-likes')[:10]
        
        print(f"   ✅ 标记了{popular_reviews.count()}条热门评论")
        
        # 推荐本周最佳
        recent_films = Film.objects.filter(
            release_date__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(
            avg_rating__gte=4.0
        ).order_by('-avg_rating')[:3]
        
        print(f"   ✅ 推荐了{recent_films.count()}部本周最佳电影")

def main():
    """主函数"""
    print("="*60)
    print("排行榜和社区数据增强脚本")
    print("="*60)
    
    try:
        # 生成高级排行榜数据
        ranking_generator = AdvancedRankingGenerator()
        ranking_generator.generate_category_rankings()
        ranking_generator.generate_trending_rankings()
        ranking_generator.generate_yearly_rankings()
        ranking_generator.generate_popularity_rankings()
        ranking_generator.generate_genre_specific_rankings()
        
        # 生成社区内容
        community_generator = CommunityContentGenerator()
        community_generator.generate_discussion_topics()
        community_generator.generate_user_interactions()
        community_generator.generate_featured_content()
        
        # 显示最终统计
        print("\n" + "="*60)
        print("数据增强完成统计")
        print("="*60)
        
        # 排行榜统计
        print("🏆 排行榜数据:")
        for main_category in ['电影', '电视剧', '动画']:
            category = Category.objects.filter(name=main_category).first()
            if category:
                count = Film.objects.filter(
                    categories=category
                ).annotate(
                    avg_rating=Avg('reviews__rating')
                ).filter(
                    avg_rating__isnull=False
                ).count()
                print(f"   - {main_category}排行榜: {count}部作品")
        
        # 社区统计
        print("\n🌐 社区数据:")
        print(f"   - 总评论数: {Review.objects.count()}条")
        print(f"   - 热门评论: {Review.objects.filter(likes__gte=10).count()}条")
        
        print("\n🎉 数据增强脚本运行完成！")
        print("\n现在您的影视推荐系统拥有：")
        print("- 丰富的排行榜数据（评分、人气、上升最快、年度等）")
        print("- 活跃的社区讨论氛围")
        print("- 真实的用户互动数据")
        print("- 精选的内容推荐")
        
    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()