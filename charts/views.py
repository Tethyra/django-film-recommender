from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import Film, Category, Review, User, WatchHistory, Favorite
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

@login_required
def charts_dashboard(request):
    """图表仪表板视图"""
    
    # 检查用户是否为管理员
    is_admin = request.user.is_staff
    
    # 1. 电影分类统计
    category_stats = Category.objects.annotate(
        film_count=Count('films'),
        avg_rating=Avg('films__rating')
    ).order_by('-film_count')
    
    # 2. 评分分布统计
    rating_distribution = []
    for i in range(1, 6):
        count = Film.objects.filter(rating__gte=i, rating__lt=i+1).count()
        rating_distribution.append({
            'rating': f'{i}-{i+1}',
            'count': count
        })
    
    # 3. 月度新增电影统计
    monthly_stats = []
    for i in range(12):
        date = timezone.now() - timedelta(days=i*30)
        count = Film.objects.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        monthly_stats.append({
            'month': date.strftime('%Y-%m'),
            'count': count
        })
    monthly_stats.reverse()
    
    # 4. 用户活跃度统计
    user_activity = User.objects.annotate(
        review_count=Count('reviews'),
        watch_count=Count('watch_history'),
        favorite_count=Count('favorites')
    ).filter(
        Q(review_count__gt=0) | Q(watch_count__gt=0) | Q(favorite_count__gt=0)
    ).order_by('-review_count')[:10]
    
    # 5. 热门电影统计
    popular_films = Film.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count')[:10]
    
    # 6. 用户个人统计（仅普通用户可见）
    personal_stats = None
    if not is_admin:
        personal_stats = {
            'watch_count': WatchHistory.objects.filter(user=request.user).count(),
            'favorite_count': Favorite.objects.filter(user=request.user).count(),
            'review_count': Review.objects.filter(user=request.user).count(),
            'avg_rating': Review.objects.filter(user=request.user).aggregate(avg=Avg('rating'))['avg'] or 0,
            'total_watch_time': WatchHistory.objects.filter(user=request.user).aggregate(total=Sum('watch_duration'))['total'] or 0
        }
    
    # 7. 管理员统计（仅管理员可见）
    admin_stats = None
    if is_admin:
        admin_stats = {
            'total_users': User.objects.count(),
            'total_films': Film.objects.count(),
            'total_reviews': Review.objects.count(),
            'total_watch_history': WatchHistory.objects.count(),
            'total_favorites': Favorite.objects.count()
        }
    
    context = {
        'page_title': '数据可视化仪表板',
        'current_page': 'charts',
        'is_admin': is_admin,
        
        # 图表数据
        'category_stats': category_stats,
        'rating_distribution': rating_distribution,
        'monthly_stats': monthly_stats,
        'user_activity': user_activity,
        'popular_films': popular_films,
        'personal_stats': personal_stats,
        'admin_stats': admin_stats,
        
        # JSON格式数据，用于Chart.js
        'category_data': json.dumps([{
            'name': cat.name,
            'count': cat.film_count,
            'rating': round(cat.avg_rating or 0, 1)
        } for cat in category_stats]),
        
        'rating_data': json.dumps(rating_distribution),
        'monthly_data': json.dumps(monthly_stats),
        
        'user_activity_data': json.dumps([{
            'username': user.username,
            'reviews': user.review_count,
            'watches': user.watch_count,
            'favorites': user.favorite_count
        } for user in user_activity]),
        
        'popular_films_data': json.dumps([{
            'title': film.title,
            'reviews': film.review_count,
            'rating': round(film.avg_rating or 0, 1)
        } for film in popular_films])
    }
    
    return render(request, 'charts/dashboard.html', context)