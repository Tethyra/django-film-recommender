from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
import json
import os
from django.conf import settings

from .models import Film, Category, Review, Favorite, WatchHistory, User
from .forms import ReviewForm, UserProfileForm, UserLoginForm, UserRegistrationForm
from .image_utils import ImageManager

# 初始化ImageManager
image_manager = ImageManager()

def login_view(request):
    """用户登录视图"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            messages.success(request, f'欢迎回来，{username}！')
            return redirect('index')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'current_page': 'login',
    }
    return render(request, 'login.html', context)

def register(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账号 {username} 创建成功！请登录。')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'current_page': 'register',
    }
    return render(request, 'register.html', context)

def index(request):
    """首页视图"""
    # 获取热门电影（评分最高的前10部）
    popular_films = Film.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:10]
    
    # 获取最新上映的电影
    new_films = Film.objects.filter(release_date__isnull=False).order_by('-release_date')[:10]
    
    # 获取热门分类
    popular_categories = Category.objects.annotate(
        film_count=Count('films')
    ).order_by('-film_count')[:6]
    
    # 获取电影和电视剧排行榜
    movie_category = Category.objects.filter(name='电影').first()
    tv_category = Category.objects.filter(name='电视剧').first()
    
    movie_rankings = Film.objects.filter(categories=movie_category).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:10] if movie_category else []
    
    tv_rankings = Film.objects.filter(categories=tv_category).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:10] if tv_category else []
    
    # 用户个性化内容
    user_favorites = []
    watch_history = []
    recommended_films = []
    
    if request.user.is_authenticated:
        # 用户收藏
        user_favorites = Favorite.objects.filter(user=request.user).select_related('film')[:4]
        
        # 观看历史
        watch_history = WatchHistory.objects.filter(user=request.user).select_related('film')[:4]
        
        # 基于观看历史的推荐
        if watch_history:
            # 获取用户观看过的电影的分类
            watched_categories = []
            for history in watch_history:
                watched_categories.extend(history.film.categories.all())
            
            # 基于分类推荐相似电影
            if watched_categories:
                recommended_films = Film.objects.filter(
                    categories__in=watched_categories
                ).exclude(
                    id__in=[history.film.id for history in watch_history]
                ).distinct().annotate(
                    avg_rating=Avg('reviews__rating')
                ).order_by('-avg_rating')[:4]
    
    context = {
        'popular_films': popular_films,
        'new_films': new_films,
        'popular_categories': popular_categories,
        'movie_rankings': movie_rankings,
        'tv_rankings': tv_rankings,
        'movie_category': movie_category,
        'tv_category': tv_category,
        'user_favorites': user_favorites,
        'watch_history': watch_history,
        'recommended_films': recommended_films,
        'current_page': 'home',
    }
    
    return render(request, 'index.html', context)

def film_detail(request, film_id):
    """电影详情视图"""
    film = get_object_or_404(Film, id=film_id)
    
    # 记录观看历史
    if request.user.is_authenticated:
        WatchHistory.objects.create(user=request.user, film=film)
    
    # 获取评论
    reviews = film.reviews.select_related('user').order_by('-created_at')
    
    # 获取相似电影（同分类）
    similar_films = Film.objects.filter(
        categories__in=film.categories.all()
    ).exclude(id=film.id).distinct()[:6]
    
    # 检查用户是否收藏
    is_favorited = request.user.is_authenticated and Favorite.objects.filter(
        user=request.user, film=film
    ).exists()
    
    # 检查用户是否已经评论
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, film=film).first()
    
    # 评论表单
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.film = film
            
            # 如果用户已经评论过，更新评论
            if user_review:
                user_review.rating = review.rating
                user_review.comment = review.comment
                user_review.updated_at = timezone.now()
                user_review.save()
                messages.success(request, '评论更新成功！')
            else:
                review.save()
                messages.success(request, '评论添加成功！')
            
            return redirect('film_detail', film_id=film.id)
    else:
        form = ReviewForm(initial={'rating': 5} if not user_review else {
            'rating': user_review.rating,
            'comment': user_review.comment
        })
    
    context = {
        'film': film,
        'reviews': reviews,
        'similar_films': similar_films,
        'is_favorited': is_favorited,
        'form': form,
        'user_review': user_review,
        'current_page': 'film_detail',
    }
    
    return render(request, 'film_detail.html', context)

def category(request, category_id=None):
    """分类视图"""
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        films = Film.objects.filter(categories=category)
    else:
        category = None
        films = Film.objects.all()
    
    # 获取排序参数
    sort = request.GET.get('sort', 'rating')
    order = request.GET.get('order', 'desc')
    view = request.GET.get('view', 'grid')
    
    # 排序
    if sort == 'rating':
        films = films.annotate(avg_rating=Avg('reviews__rating')).order_by(f'-avg_rating' if order == 'desc' else 'avg_rating')
    elif sort == 'release_date':
        films = films.order_by(f'-release_date' if order == 'desc' else 'release_date')
    elif sort == 'title':
        films = films.order_by(f'title' if order == 'asc' else '-title')
    else:
        films = films.order_by('-created_at')
    
    # 分页
    paginator = Paginator(films, 12 if view == 'grid' else 10)
    page = request.GET.get('page')
    
    try:
        films = paginator.page(page)
    except PageNotAnInteger:
        films = paginator.page(1)
    except EmptyPage:
        films = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'films': films,
        'sort': sort,
        'order': order,
        'view': view,
        'current_page': 'category',
    }
    
    return render(request, 'category.html', context)

def search(request):
    """搜索视图"""
    query = request.GET.get('query', '')
    category_id = request.GET.get('category')
    
    films = Film.objects.all()
    
    if query:
        films = films.filter(
            Q(title__icontains=query) |
            Q(director__icontains=query) |
            Q(actors__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category_id:
        films = films.filter(categories=category_id)
    
    # 排序
    films = films.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    
    # 分页
    paginator = Paginator(films, 12)
    page = request.GET.get('page')
    
    try:
        films = paginator.page(page)
    except PageNotAnInteger:
        films = paginator.page(1)
    except EmptyPage:
        films = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    
    context = {
        'films': films,
        'query': query,
        'category_id': category_id,
        'categories': categories,
        'current_page': 'search',
    }
    
    return render(request, 'search_results.html', context)

def rankings(request):
    """排行榜视图"""
    sort = request.GET.get('sort', 'rating')
    
    if sort == 'rating':
        films = Film.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gt=0).order_by('-avg_rating')
        title = '评分排行榜'
    elif sort == 'release_date':
        films = Film.objects.filter(release_date__isnull=False).order_by('-release_date')
        title = '新片上映排行榜'
    elif sort == 'popularity':
        films = Film.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')
        title = '热门程度排行榜'
    else:
        films = Film.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')
        title = '综合排行榜'
    
    # 分页
    paginator = Paginator(films, 20)
    page = request.GET.get('page')
    
    try:
        films = paginator.page(page)
    except PageNotAnInteger:
        films = paginator.page(1)
    except EmptyPage:
        films = paginator.page(paginator.num_pages)
    
    context = {
        'films': films,
        'sort': sort,
        'title': title,
        'current_page': 'rankings',
    }
    
    return render(request, 'rankings.html', context)

@login_required
def profile(request, username=None):
    """个人资料视图"""
    if username:
        # 查看他人资料
        user = get_object_or_404(User, username=username)
        is_owner = request.user.username == username
    else:
        # 查看自己的资料
        user = request.user
        is_owner = True
    
    # 获取用户统计信息
    favorite_count = Favorite.objects.filter(user=user).count()
    review_count = Review.objects.filter(user=user).count()
    watch_count = WatchHistory.objects.filter(user=user).count()
    
    # 获取用户的评论
    user_reviews = Review.objects.filter(user=user).select_related('film').order_by('-created_at')[:5]
    
    # 获取用户的收藏
    user_favorites = Favorite.objects.filter(user=user).select_related('film').order_by('-created_at')[:5]
    
    # 编辑资料
    if request.method == 'POST' and is_owner:
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # 处理头像上传
            if 'avatar' in request.FILES:
                # 使用ImageManager处理头像
                avatar_file = request.FILES['avatar']
                avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars', f'user_{user.id}.jpg')
                
                # 保存头像
                with open(avatar_path, 'wb') as f:
                    for chunk in avatar_file.chunks():
                        f.write(chunk)
                
                # 验证头像
                if image_manager.validate_image(avatar_path):
                    user.avatar = f"avatars/user_{user.id}.jpg"
                else:
                    messages.error(request, '头像上传失败，请使用有效的图片文件')
            
            form.save()
            messages.success(request, '个人资料更新成功！')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'user_profile': user,
        'is_owner': is_owner,
        'form': form,
        'favorite_count': favorite_count,
        'review_count': review_count,
        'watch_count': watch_count,
        'user_reviews': user_reviews,
        'user_favorites': user_favorites,
        'current_page': 'profile',
    }
    
    return render(request, 'profile.html', context)

@login_required
def favorites(request):
    """我的收藏视图"""
    favorites = Favorite.objects.filter(user=request.user).select_related('film').order_by('-created_at')
    
    # 分页
    paginator = Paginator(favorites, 12)
    page = request.GET.get('page')
    
    try:
        favorites = paginator.page(page)
    except PageNotAnInteger:
        favorites = paginator.page(1)
    except EmptyPage:
        favorites = paginator.page(paginator.num_pages)
    
    context = {
        'favorites': favorites,
        'current_page': 'favorites',
    }
    
    return render(request, 'favorites.html', context)

@login_required
def history(request):
    """观看历史视图"""
    history = WatchHistory.objects.filter(user=request.user).select_related('film').order_by('-watch_time')
    
    # 分页
    paginator = Paginator(history, 12)
    page = request.GET.get('page')
    
    try:
        history = paginator.page(page)
    except PageNotAnInteger:
        history = paginator.page(1)
    except EmptyPage:
        history = paginator.page(paginator.num_pages)
    
    context = {
        'history': history,
        'current_page': 'history',
    }
    
    return render(request, 'history.html', context)

@login_required
def toggle_favorite(request, film_id):
    """切换收藏状态"""
    film = get_object_or_404(Film, id=film_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, film=film)
    
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'added'})

@login_required
def add_watch_history(request, film_id):
    """添加观看历史"""
    film = get_object_or_404(Film, id=film_id)
    
    # 检查是否已经存在最近的观看记录
    recent_history = WatchHistory.objects.filter(
        user=request.user,
        film=film,
        watch_time__gte=timezone.now() - timezone.timedelta(hours=1)
    ).exists()
    
    if not recent_history:
        WatchHistory.objects.create(user=request.user, film=film)
    
    return JsonResponse({'status': 'success'})

@login_required
def add_review(request, film_id):
    """添加评论"""
    film = get_object_or_404(Film, id=film_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.film = film
            
            # 检查是否已经评论过
            existing_review = Review.objects.filter(user=request.user, film=film).first()
            if existing_review:
                existing_review.rating = review.rating
                existing_review.comment = review.comment
                existing_review.updated_at = timezone.now()
                existing_review.save()
                messages.success(request, '评论更新成功！')
            else:
                review.save()
                messages.success(request, '评论添加成功！')
            
            return redirect('film_detail', film_id=film.id)
    else:
        # 检查是否已经评论过
        existing_review = Review.objects.filter(user=request.user, film=film).first()
        initial_data = {'rating': 5}
        if existing_review:
            initial_data = {'rating': existing_review.rating, 'comment': existing_review.comment}
        
        form = ReviewForm(initial=initial_data)
    
    context = {
        'form': form,
        'film': film,
        'existing_review': existing_review,
    }
    
    return render(request, 'add_review.html', context)

@login_required
def delete_review(request, review_id):
    """删除评论"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        film_id = review.film.id
        review.delete()
        messages.success(request, '评论删除成功！')
        return redirect('film_detail', film_id=film_id)
    
    context = {
        'review': review,
    }
    
    return render(request, 'confirm_delete.html', context)

def image_test(request):
    """图片测试页面"""
    films = Film.objects.all()[:10]
    
    context = {
        'films': films,
    }
    
    return render(request, 'test_images.html', context)

# 管理员视图
@login_required
def admin_dashboard(request):
    """管理员控制面板"""
    if not request.user.is_staff:
        messages.error(request, '您没有访问权限')
        return redirect('index')
    
    # 统计信息
    total_films = Film.objects.count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()
    total_reviews = Review.objects.count()
    
    # 最新电影
    recent_films = Film.objects.order_by('-created_at')[:5]
    
    # 最新用户
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # 最新评论
    recent_reviews = Review.objects.select_related('user', 'film').order_by('-created_at')[:5]
    
    context = {
        'total_films': total_films,
        'total_categories': total_categories,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'recent_films': recent_films,
        'recent_users': recent_users,
        'recent_reviews': recent_reviews,
        'current_page': 'admin_dashboard',
    }
    
    return render(request, 'admin_dashboard.html', context)

# 缺失的视图函数
def community(request):
    """社区页面视图"""
    # 获取热门评论
    popular_reviews = Review.objects.select_related('user', 'film').annotate(
        likes_count=Count('likes')
    ).order_by('-created_at')[:10]
    
    # 获取活跃用户
    active_users = User.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:5]
    
    context = {
        'popular_reviews': popular_reviews,
        'active_users': active_users,
        'current_page': 'community',
    }
    
    return render(request, 'community.html', context)

@login_required
def share_film(request, film_id):
    """分享电影"""
    film = get_object_or_404(Film, id=film_id)
    
    # 生成分享链接
    share_url = request.build_absolute_uri(reverse('film_detail', args=[film_id]))
    
    # 可以添加分享到社交媒体的逻辑
    messages.success(request, f'电影分享链接已复制到剪贴板：{share_url}')
    return redirect('film_detail', film_id=film_id)

@login_required
def my_reviews(request):
    """我的评论"""
    reviews = Review.objects.filter(user=request.user).select_related('film').order_by('-created_at')
    
    # 分页
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    
    context = {
        'reviews': reviews,
        'current_page': 'my_reviews',
    }
    
    return render(request, 'my_reviews.html', context)