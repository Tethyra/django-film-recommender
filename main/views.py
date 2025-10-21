from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import Film, Category, WatchHistory, Favorite, Review, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, ReviewForm, ProfileUpdateForm

def index(request):
    """首页视图"""
    # 获取热门推荐影片（评分最高的前3部）
    popular_films = Film.objects.annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:3]
    
    # 获取最新上映影片
    new_films = Film.objects.order_by('-release_date')[:3]
    
    # 获取经典影片（评分高且评分人数多）
    classic_films = Film.objects.filter(rating_count__gte=10).order_by('-rating')[:3]
    
    context = {
        'popular_films': popular_films,
        'new_films': new_films,
        'classic_films': classic_films,
        'title': '首页 - 影视推荐系统',
    }
    return render(request, 'index.html', context)

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
        'title': '登录 - 影视推荐系统',
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
        'title': '注册 - 影视推荐系统',
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
    
    context = {
        'categories': categories,
        'selected_category': selected_category,
        'films': films,
        'title': '影视分类 - 影视推荐系统',
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
    
    context = {
        'film_rankings': film_rankings,
        'series_rankings': series_rankings,
        'animation_rankings': animation_rankings,
        'trending_rankings': trending_rankings,
        'title': '影视排行榜 - 影视推荐系统',
    }
    return render(request, 'rankings.html', context)

@login_required
def history(request):
    """观看历史视图"""
    watch_history = WatchHistory.objects.filter(user=request.user).order_by('-watch_time')
    
    context = {
        'watch_history': watch_history,
        'title': '我的观看记录 - 影视推荐系统',
    }
    return render(request, 'history.html', context)

def community(request):
    """社区视图"""
    # 获取最新评论
    latest_reviews = Review.objects.order_by('-created_at')[:20]
    
    context = {
        'latest_reviews': latest_reviews,
        'title': '电影社区 - 影视推荐系统',
    }
    return render(request, 'community.html', context)

def blackroom(request):
    """Blackroom视图"""
    context = {
        'title': 'Blackroom - 影视推荐系统',
    }
    return render(request, 'blackroom.html', context)

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
    
    context = {
        'film': film,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'title': f'{film.title} - 影视推荐系统',
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
        'title': '发表评论 - 影视推荐系统',
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
    else:
        messages.success(request, f'已收藏《{film.title}》')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('index')))

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
    
    # 获取用户收藏
    favorites = Favorite.objects.filter(user=request.user).select_related('film')
    
    context = {
        'form': form,
        'favorites': favorites,
        'title': '个人资料 - 影视推荐系统',
    }
    return render(request, 'profile.html', context)