from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    
    # 登录和注册
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 分类页面
    path('category/', views.category, name='category'),
    path('category/<int:category_id>/', views.category, name='category_detail'),
    
    # 排行榜页面
    path('rankings/', views.rankings, name='rankings'),
    
    # 观看历史
    path('history/', views.history, name='history'),
    
    # 社区页面
    path('community/', views.community, name='community'),
    
    # Blackroom页面
    path('blackroom/', views.blackroom, name='blackroom'),
    
    # 影视详情
    path('film/<int:film_id>/', views.film_detail, name='film_detail'),
    
    # 添加评论
    path('film/<int:film_id>/review/', views.add_review, name='add_review'),
    
    # 收藏/取消收藏
    path('film/<int:film_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # 个人资料
    path('profile/', views.profile, name='profile'),
]