# main/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import os
from django.conf import settings

def get_poster_path(instance, filename):
    """获取海报存储路径"""
    if filename:
        ext = filename.split('.')[-1]
        filename = f"{slugify(instance.title)}.{ext}"
    return os.path.join('posters', filename)

def get_avatar_path(instance, filename):
    """获取头像存储路径"""
    if filename:
        ext = filename.split('.')[-1]
        filename = f"user_{instance.user.id}.{ext}"
    return os.path.join('avatars', filename)

class User(AbstractUser):
    """自定义用户模型"""
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to=get_avatar_path, blank=True, null=True)
    favorite_categories = models.CharField(max_length=200, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def avatar_url(self):
        """获取头像URL，如果没有则返回默认头像"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return os.path.join(settings.STATIC_URL, 'images', 'default_avatar.png')

class Category(models.Model):
    """影视分类模型"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Film(models.Model):
    """影视作品模型"""
    title = models.CharField(max_length=200)
    director = models.CharField(max_length=200)
    actors = models.CharField(max_length=500)
    release_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    poster = models.ImageField(upload_to=get_poster_path, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    rating_count = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, related_name='films')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def poster_url(self):
        """获取海报URL，如果没有则返回默认海报"""
        if self.poster and hasattr(self.poster, 'url'):
            return self.poster.url
        return os.path.join(settings.STATIC_URL, 'images', 'default_poster.png')

class Review(models.Model):
    """评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 对 {self.film.title} 的评论'

class Favorite(models.Model):
    """收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'film']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 收藏了 {self.film.title}'

class WatchHistory(models.Model):
    """观看历史模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='watch_history')
    watch_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-watch_time']

    def __str__(self):
        return f'{self.user.username} 观看了 {self.film.title}'