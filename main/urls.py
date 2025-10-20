from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    
    # 搜索功能
    path('search/', views.search, name='search'),
    
    # 登录和注册
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 密码重置
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # 分类页面
    path('category/', views.category, name='category'),
    path('category/<int:category_id>/', views.category, name='category_detail'),
    
    # 排行榜页面
    path('rankings/', views.rankings, name='rankings'),
    
    # 观看历史
    path('history/', views.history, name='history'),
    
    # 社区页面
    path('community/', views.community, name='community'),
    
    # 影视详情
    path('film/<int:film_id>/', views.film_detail, name='film_detail'),
    
    # 添加评论
    path('film/<int:film_id>/review/', views.add_review, name='add_review'),
    
    # 删除评论
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    
    # 收藏/取消收藏
    path('film/<int:film_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # 分享电影
    path('film/<int:film_id>/share/', views.share_film, name='share_film'),
    
    # 个人资料
    path('profile/', views.profile, name='profile'),
    
    # 我的收藏
    path('favorites/', views.favorites, name='favorites'),
    
    # 我的评论
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]