from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """影视分类模型"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, null=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '影视分类'
        verbose_name_plural = '影视分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Film(models.Model):
    """影视作品模型"""
    title = models.CharField(max_length=200, verbose_name='标题')
    categories = models.ManyToManyField(Category, related_name='films', verbose_name='分类')
    director = models.CharField(max_length=100, blank=True, null=True, verbose_name='导演')
    actors = models.CharField(max_length=500, blank=True, null=True, verbose_name='演员')
    release_date = models.DateField(blank=True, null=True, verbose_name='上映日期')
    description = models.TextField(blank=True, null=True, verbose_name='剧情描述')
    poster = models.ImageField(upload_to='posters/', blank=True, null=True, verbose_name='海报')
    rating = models.FloatField(default=0, verbose_name='评分')
    rating_count = models.IntegerField(default=0, verbose_name='评分人数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '影视作品'
        verbose_name_plural = '影视作品'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class WatchHistory(models.Model):
    """观看历史模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history', verbose_name='用户')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='watch_records', verbose_name='影视作品')
    watch_time = models.DateTimeField(default=timezone.now, verbose_name='观看时间')
    watch_duration = models.IntegerField(default=0, verbose_name='观看时长(秒)')
    
    class Meta:
        verbose_name = '观看历史'
        verbose_name_plural = '观看历史'
        ordering = ['-watch_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.film.title} - {self.watch_time}"

class Favorite(models.Model):
    """收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='影视作品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ('user', 'film')  # 一个用户只能收藏一个影视一次
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.film.title}"

class Review(models.Model):
    """评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='用户')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='reviews', verbose_name='影视作品')
    rating = models.IntegerField(default=5, verbose_name='评分', choices=[(i, i) for i in range(1, 6)])
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 对 {self.film.title} 的评论"

class UserProfile(models.Model):
    """用户资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    bio = models.TextField(blank=True, null=True, verbose_name='个人简介')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    favorite_categories = models.ManyToManyField(Category, blank=True, related_name='favorite_users', verbose_name='喜欢的分类')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f"{self.user.username} 的资料"