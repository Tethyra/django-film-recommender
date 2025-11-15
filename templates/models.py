# models.py - UserProfile模型定义示例
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """电影分类模型"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Film(models.Model):
    """电影模型"""
    title = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    actors = models.TextField()
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    duration = models.IntegerField(help_text="电影时长（分钟）")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='films')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    """用户资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    favorite_genres = models.ManyToManyField(Category, blank=True, related_name='favorite_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Review(models.Model):
    """电影评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.film.title} ({self.rating})"
    
    class Meta:
        unique_together = ('user', 'film')

class Favorite(models.Model):
    """电影收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} favorited {self.film.title}"
    
    class Meta:
        unique_together = ('user', 'film')

class WatchHistory(models.Model):
    """观看历史模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='watch_history')
    watch_time = models.DateTimeField(default=timezone.now)
    watch_duration = models.IntegerField(default=0, help_text="观看时长（秒）")
    
    def __str__(self):
        return f"{self.user.username} watched {self.film.title} at {self.watch_time}"