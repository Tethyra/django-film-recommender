"""
主应用URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 用户认证
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # 密码重置
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # 首页
    path('', views.index, name='index'),
    
    # 电影相关
    path('film/<int:pk>/', views.FilmDetailView.as_view(), name='film_detail'),
    path('film/<int:film_id>/review/', views.add_review, name='add_review'),
    path('film/<int:film_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # 分类相关
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # 排行榜
    path('rankings/', views.rankings, name='rankings'),
    
    # 搜索
    path('search/', views.search, name='search'),
    
    # 用户中心
    path('profile/', views.profile, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('history/', views.watch_history, name='watch_history'),
    
    # 社区
    path('community/', views.community, name='community'),
]
