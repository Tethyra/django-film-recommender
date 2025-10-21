from django.contrib import admin
from .models import (
    Category, Film, WatchHistory, 
    Favorite, Review, UserProfile
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """影视分类管理"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    """影视作品管理"""
    list_display = ('title', 'director', 'release_date', 'rating', 'rating_count', 'created_at')
    search_fields = ('title', 'director', 'actors', 'description')
    list_filter = ('categories', 'release_date', 'created_at')
    filter_horizontal = ('categories',)
    readonly_fields = ('rating', 'rating_count')

@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    """观看历史管理"""
    list_display = ('user', 'film', 'watch_time', 'watch_duration')
    search_fields = ('user__username', 'film__title')
    list_filter = ('watch_time',)
    date_hierarchy = 'watch_time'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """收藏管理"""
    list_display = ('user', 'film', 'created_at')
    search_fields = ('user__username', 'film__title')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """评论管理"""
    list_display = ('user', 'film', 'rating', 'created_at', 'likes')
    search_fields = ('user__username', 'film__title', 'content')
    list_filter = ('rating', 'created_at')
    date_hierarchy = 'created_at'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户资料管理"""
    list_display = ('user', 'birth_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    list_filter = ('created_at',)
    filter_horizontal = ('favorite_categories',)