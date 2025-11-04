# quick_test_data.py - 快速测试数据生成
from django.contrib.auth.models import User
from main.models import Film, Category, Review, Favorite, WatchHistory
from datetime import date, datetime, timedelta
import random

def create_test_data():
    """创建测试数据"""
    print("开始添加测试数据...")
    
    # 1. 创建测试分类
    categories_data = [
        {'name': '电影', 'description': '精彩的电影作品'},
        {'name': '电视剧', 'description': '热门电视剧集'},
        {'name': '动画', 'description': '动画电影和剧集'},
        {'name': '纪录片', 'description': '真实记录的影片'},
        {'name': '动作', 'description': '动作冒险类影片'},
        {'name': '喜剧', 'description': '轻松搞笑的影片'},
        {'name': '爱情', 'description': '浪漫爱情故事'},
        {'name': '科幻', 'description': '科学幻想题材'},
        {'name': '恐怖', 'description': '惊悚恐怖影片'},
        {'name': '悬疑', 'description': '悬疑推理故事'},
    ]
    
    categories = []
    for data in categories_data:
        category, created = Category.objects.get_or_create(
            name=data['name'],
            defaults={'description': data['description']}
        )
        categories.append(category)
        if created:
            print(f"创建分类: {data['name']}")
    
    # 2. 创建测试用户
    users_data = [
        {'username': 'user1', 'email': 'user1@example.com', 'password': 'password123'},
        {'username': 'user2', 'email': 'user2@example.com', 'password': 'password123'},
        {'username': 'user3', 'email': 'user3@example.com', 'password': 'password123'},
    ]
    
    users = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={'email': data['email']}
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"创建用户: {data['username']}")
        users.append(user)
    
    # 3. 创建测试电影
    films_data = [
        {
            'title': '肖申克的救赎',
            'director': '弗兰克·德拉邦特',
            'actors': '蒂姆·罗宾斯, 摩根·弗里曼',
            'release_date': date(1994, 9, 23),
            'description': '银行家安迪被冤枉杀害妻子入狱，在肖申克监狱中寻找自由的故事',
            'rating': 9.3,
            'category_indices': [0, 4]  # 电影、动作
        },
        {
            'title': '阿甘正传',
            'director': '罗伯特·泽米吉斯',
            'actors': '汤姆·汉克斯, 罗宾·怀特',
            'release_date': date(1994, 7, 6),
            'description': '智商不高的阿甘通过努力创造奇迹的励志故事',
            'rating': 9.2,
            'category_indices': [0, 6]  # 电影、爱情
        },
        {
            'title': '楚门的世界',
            'director': '彼得·威尔',
            'actors': '金·凯瑞, 劳拉·琳妮',
            'release_date': date(1998, 6, 5),
            'description': '楚门生活在一个巨大的摄影棚中，他的生活被全世界观看',
            'rating': 8.8,
            'category_indices': [0, 7]  # 电影、科幻
        },
        {
            'title': '盗梦空间',
            'director': '克里斯托弗·诺兰',
            'actors': '莱昂纳多·迪卡普里奥, 约瑟夫·高登-莱维特',
            'release_date': date(2010, 7, 16),
            'description': '一群能够进入他人梦境的盗贼的故事',
            'rating': 9.0,
            'category_indices': [0, 7, 9]  # 电影、科幻、悬疑
        },
        {
            'title': '千与千寻',
            'director': '宫崎骏',
            'actors': '柊瑠美, 入野自由, 夏木真理',
            'release_date': date(2001, 7, 20),
            'description': '少女千寻意外来到神灵世界的冒险故事',
            'rating': 9.4,
            'category_indices': [0, 2, 7]  # 电影、动画、科幻
        },
        {
            'title': '权力的游戏 第一季',
            'director': '蒂莫西·范·帕腾',
            'actors': '彼特·丁拉基, 琳娜·海蒂, 艾米莉亚·克拉克',
            'release_date': date(2011, 4, 17),
            'description': '维斯特洛大陆上各大家族争夺铁王座的故事',
            'rating': 9.5,
            'category_indices': [1, 4, 9]  # 电视剧、动作、悬疑
        },
    ]
    
    films = []
    for data in films_data:
        film, created = Film.objects.get_or_create(
            title=data['title'],
            defaults={
                'director': data['director'],
                'actors': data['actors'],
                'release_date': data['release_date'],
                'description': data['description'],
                'rating': data['rating'],
                'rating_count': random.randint(100, 1000)
            }
        )
        
        if created:
            # 设置分类
            film_categories = [categories[i] for i in data['category_indices']]
            film.categories.set(film_categories)
            film.save()
            print(f"创建电影: {data['title']}")
        films.append(film)
    
    # 4. 创建测试评论
    review_count = 0
    for user in users:
        # 每个用户对随机的2-3部电影发表评论
        films_to_review = random.sample(films, random.randint(2, 3))
        
        for film in films_to_review:
            review, created = Review.objects.get_or_create(
                user=user,
                film=film,
                defaults={
                    'rating': random.randint(4, 5),  # 主要是正面评价
                    'content': generate_review_content(film.title),
                    'likes': random.randint(0, 20)
                }
            )
            if created:
                review_count += 1
    
    print(f"创建了 {review_count} 条评论")
    
    # 5. 创建测试收藏
    favorite_count = 0
    for user in users:
        # 每个用户收藏随机的1-2部电影
        films_to_favorite = random.sample(films, random.randint(1, 2))
        
        for film in films_to_favorite:
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                film=film
            )
            if created:
                favorite_count += 1
    
    print(f"创建了 {favorite_count} 个收藏")
    
    # 6. 创建测试观看历史
    history_count = 0
    for user in users:
        # 每个用户有随机的2-3条观看历史
        films_to_watch = random.sample(films, random.randint(2, 3))
        
        for film in films_to_watch:
            # 随机的观看时间（最近30天内）
            days_ago = random.randint(1, 30)
            watch_time = datetime.now() - timedelta(days=days_ago)
            
            history, created = WatchHistory.objects.get_or_create(
                user=user,
                film=film,
                defaults={
                    'watch_time': watch_time,
                    'watch_duration': random.randint(300, 3600)  # 5分钟到1小时
                }
            )
            if created:
                history_count += 1
    
    print(f"创建了 {history_count} 条观看历史")
    print("测试数据添加完成！")

def generate_review_content(film_title):
    """生成随机评论内容"""
    positive_adjectives = ['精彩', '很棒', '优秀', '出色', '令人难忘', '经典', '震撼', '感人']
    sentiment = ['值得一看', '强烈推荐', '不容错过', '一定要看']
    
    content_templates = [
        f'{film_title} 真的很{random.choice(positive_adjectives)}！{random.choice(sentiment)}。',
        f'看完了{film_title}，感觉{random.choice(positive_adjectives)}。演员的表演很到位，剧情也很吸引人。',
        f'{random.choice(positive_adjectives)}的一部电影，{film_title}让我{random.choice(["感动", "兴奋", "惊喜"])}。',
        f'推荐大家去看{film_title}，这是一部{random.choice(positive_adjectives)}的作品，{random.choice(sentiment)}。',
    ]
    
    return random.choice(content_templates)

# 如果直接运行这个文件，需要配置Django环境
if __name__ == "__main__":
    import os
    import django
    
    # 设置Django环境
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_recommender.settings")
    django.setup()
    
    create_test_data()