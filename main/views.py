from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Film, Category, WatchHistory, Favorite, Review, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, ReviewForm, ProfileUpdateForm, SearchForm

def index(request):
    """首页视图"""
    # 获取热门推荐影片（评分最高的前3部）
    popular_films = Film.objects.annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:3]
    
    # 获取最新上映影片
    new_films = Film.objects.order_by('-release_date')[:3]
    
    # 获取经典影片（评分高且评分人数多）
    classic_films = Film.objects.filter(rating_count__gte=10).order_by('-rating')[:3]
    
    # 获取上升最快的影片
    trending_films = Film.objects.order_by('-created_at')[:3]
    
    context = {
        'popular_films': popular_films,
        'new_films': new_films,
        'classic_films': classic_films,
        'trending_films': trending_films,
        'title': '首页 - CineSphere',
    }
    return render(request, 'index.html', context)

def search(request):
    """搜索功能"""
    form = SearchForm(request.GET)
    films = []
    
    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            films = Film.objects.filter(
                Q(title__icontains=query) | 
                Q(director__icontains=query) |
                Q(actors__icontains=query) |
                Q(description__icontains=query) |
                Q(categories__name__icontains=query)
            ).distinct()
    
    # 分页
    paginator = Paginator(films, 12)
    page = request.GET.get('page')
    
    try:
        films_paginated = paginator.page(page)
    except PageNotAnInteger:
        films_paginated = paginator.page(1)
    except EmptyPage:
        films_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'form': form,
        'films': films_paginated,
        'query': request.GET.get('query', ''),
        'title': '搜索结果 - CineSphere',
    }
    return render(request, 'search_results.html', context)

def login_view(request):
    """登录视图"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '登录成功！')
                next_page = request.GET.get('next', 'index')
                return redirect(next_page)
            else:
                messages.error(request, '用户名或密码错误！')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': '登录 - CineSphere',
    }
    return render(request, 'login.html', context)

def register(request):
    """注册视图"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 创建用户资料
            UserProfile.objects.create(user=user)
            messages.success(request, '注册成功！请登录。')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': '注册 - CineSphere',
    }
    return render(request, 'register.html', context)

def category(request, category_id=None):
    """分类视图"""
    categories = Category.objects.all()
    selected_category = None
    films = Film.objects.all()
    
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        films = films.filter(categories=selected_category)
    
    # 分页
    paginator = Paginator(films, 12)
    page = request.GET.get('page')
    
    try:
        films_paginated = paginator.page(page)
    except PageNotAnInteger:
        films_paginated = paginator.page(1)
    except EmptyPage:
        films_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
        'selected_category': selected_category,
        'films': films_paginated,
        'title': '影视分类 - CineSphere',
    }
    return render(request, 'category.html', context)

def rankings(request):
    """排行榜视图"""
    # 电影排行榜
    film_rankings = Film.objects.filter(categories__name__icontains='电影').order_by('-rating')[:10]
    
    # 剧集排行榜
    series_rankings = Film.objects.filter(categories__name__icontains='剧集').order_by('-rating')[:10]
    
    # 动画排行榜
    animation_rankings = Film.objects.filter(categories__name__icontains='动画').order_by('-rating')[:10]
    
    # 上升最快
    trending_rankings = Film.objects.order_by('-created_at')[:10]
    
    # 最新上映
    new_release_rankings = Film.objects.order_by('-release_date')[:10]
    
    context = {
        'film_rankings': film_rankings,
        'series_rankings': series_rankings,
        'animation_rankings': animation_rankings,
        'trending_rankings': trending_rankings,
        'new_release_rankings': new_release_rankings,
        'title': '影视排行榜 - CineSphere',
    }
    return render(request, 'rankings.html', context)

@login_required
def history(request):
    """观看历史视图"""
    watch_history = WatchHistory.objects.filter(user=request.user).order_by('-watch_time')
    
    # 分页
    paginator = Paginator(watch_history, 10)
    page = request.GET.get('page')
    
    try:
        history_paginated = paginator.page(page)
    except PageNotAnInteger:
        history_paginated = paginator.page(1)
    except EmptyPage:
        history_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'watch_history': history_paginated,
        'title': '我的观看记录 - CineSphere',
    }
    return render(request, 'history.html', context)

def community(request):
    """社区视图"""
    # 获取最新评论
    latest_reviews = Review.objects.order_by('-created_at')
    
    # 分页
    paginator = Paginator(latest_reviews, 20)
    page = request.GET.get('page')
    
    try:
        reviews_paginated = paginator.page(page)
    except PageNotAnInteger:
        reviews_paginated = paginator.page(1)
    except EmptyPage:
        reviews_paginated = paginator.page(paginator.num_pages)
    
    # 获取热门讨论的影片
    popular_films = Film.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:5]
    
    context = {
        'latest_reviews': reviews_paginated,
        'popular_films': popular_films,
        'title': '电影社区 - CineSphere',
    }
    return render(request, 'community.html', context)

@login_required
def film_detail(request, film_id):
    """影视详情视图"""
    film = get_object_or_404(Film, id=film_id)
    
    # 记录观看历史
    WatchHistory.objects.create(
        user=request.user,
        film=film,
        watch_time=timezone.now()
    )
    
    # 获取相关评论
    reviews = Review.objects.filter(film=film).order_by('-created_at')
    
    # 检查用户是否收藏
    is_favorited = Favorite.objects.filter(user=request.user, film=film).exists()
    
    # 获取相似影片
    similar_films = Film.objects.filter(
        categories__in=film.categories.all()
    ).exclude(id=film.id).distinct()[:4]
    
    context = {
        'film': film,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'similar_films': similar_films,
        'title': f'{film.title} - CineSphere',
    }
    return render(request, 'film_detail.html', context)

@login_required
def add_review(request, film_id):
    """添加评论视图"""
    film = get_object_or_404(Film, id=film_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.film = film
            review.save()
            
            # 更新电影评分
            film.rating_count += 1
            film.rating = (film.rating * (film.rating_count - 1) + review.rating) / film.rating_count
            film.save()
            
            messages.success(request, '评论发表成功！')
            return redirect('film_detail', film_id=film_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'film': film,
        'title': '发表评论 - CineSphere',
    }
    return render(request, 'add_review.html', context)

@login_required
def toggle_favorite(request, film_id):
    """切换收藏状态"""
    film = get_object_or_404(Film, id=film_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, film=film)
    
    if not created:
        favorite.delete()
        messages.info(request, f'已取消收藏《{film.title}》')
        return JsonResponse({'status': 'removed', 'message': f'已取消收藏《{film.title}》'})
    else:
        messages.success(request, f'已收藏《{film.title}》')
        return JsonResponse({'status': 'added', 'message': f'已收藏《{film.title}》'})

@login_required
def favorites(request):
    """我的收藏页面"""
    favorites = Favorite.objects.filter(user=request.user).select_related('film').order_by('-created_at')
    
    # 分页
    paginator = Paginator(favorites, 12)
    page = request.GET.get('page')
    
    try:
        favorites_paginated = paginator.page(page)
    except PageNotAnInteger:
        favorites_paginated = paginator.page(1)
    except EmptyPage:
        favorites_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'favorites': favorites_paginated,
        'title': '我的收藏 - CineSphere',
    }
    return render(request, 'favorites.html', context)

@login_required
def my_reviews(request):
    """我的评论页面"""
    reviews = Review.objects.filter(user=request.user).select_related('film').order_by('-created_at')
    
    # 分页
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    
    try:
        reviews_paginated = paginator.page(page)
    except PageNotAnInteger:
        reviews_paginated = paginator.page(1)
    except EmptyPage:
        reviews_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'reviews': reviews_paginated,
        'title': '我的评论 - CineSphere',
    }
    return render(request, 'my_reviews.html', context)

@login_required
def profile(request):
    """用户个人资料视图"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料更新成功！')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    # 获取用户统计信息
    favorite_count = Favorite.objects.filter(user=request.user).count()
    review_count = Review.objects.filter(user=request.user).count()
    watch_count = WatchHistory.objects.filter(user=request.user).count()
    
    context = {
        'form': form,
        'favorite_count': favorite_count,
        'review_count': review_count,
        'watch_count': watch_count,
        'title': '个人资料 - CineSphere',
    }
    return render(request, 'profile.html', context)

@login_required
def delete_review(request, review_id):
    """删除评论"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        film_id = review.film.id
        
        # 如果这是该电影的最后一条评论，需要特殊处理
        film = review.film
        if film.rating_count > 1:
            # 重新计算电影评分
            remaining_reviews = Review.objects.filter(film=film).exclude(id=review_id)
            total_rating = sum(r.rating for r in remaining_reviews)
            film.rating = total_rating / len(remaining_reviews)
            film.rating_count -= 1
            film.save()
        else:
            # 如果是最后一条评论，重置评分
            film.rating = 0
            film.rating_count = 0
            film.save()
        
        review.delete()
        messages.success(request, '评论已删除！')
        return redirect('film_detail', film_id=film_id)
    
    context = {
        'review': review,
        'title': '删除评论 - CineSphere',
    }
    return render(request, 'confirm_delete.html', context)

@login_required
def share_film(request, film_id):
    """分享电影"""
    film = get_object_or_404(Film, id=film_id)
    
    # 生成分享链接
    share_url = request.build_absolute_uri(reverse('film_detail', args=[film_id]))
    
    context = {
        'film': film,
        'share_url': share_url,
        'title': '分享电影 - CineSphere',
    }
    return render(request, 'share_film.html', context)