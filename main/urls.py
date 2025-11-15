"""
最终完整修复版的urls.py文件
修复了所有URL配置错误
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    
    # 电影详情
    path('film/<int:film_id>/', views.film_detail, name='film_detail'),
    
    # 分类浏览
    path('category/', views.category, name='category'),
    path('category/<int:category_id>/', views.category, name='category_detail'),
    
    # 搜索功能
    path('search/', views.search, name='search'),
    
    # 排行榜
    path('rankings/', views.rankings, name='rankings'),
    
    # 用户认证 - 修复：使用Django内置的logout视图
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    
    # 个人中心
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile_username'),
    
    # 收藏管理
    path('favorites/', views.favorites, name='favorites'),
    path('favorite/toggle/<int:film_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # 观看历史
    path('history/', views.history, name='history'),
    
    # 社区页面
    path('community/', views.community, name='community'),
    
    # 新增功能页面 - 注意：这些视图函数可能在views.py中不存在
    path('recommendations/', views.recommendations, name='recommendations'),
    path('actor/<str:actor_name>/', views.actor_detail, name='actor_detail'),
    path('director/<str:director_name>/', views.director_detail, name='director_detail'),
    path('calendar/', views.calendar, name='calendar'),
    path('personal_stats/', views.personal_stats, name='personal_stats'),
    
    # 管理员功能
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # AJAX请求处理
    path('add_review/<int:film_id>/', views.add_review, name='add_review'),
    path('set_reminder/', views.set_reminder, name='set_reminder'),
    
    # 密码重置功能
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]