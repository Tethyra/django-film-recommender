# main/middleware.py
import time
from django.core.cache import cache
from django.conf import settings

class OnlineUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 处理请求前
        if request.user.is_authenticated:
            # 为登录用户更新在线状态
            user_id = request.user.id
            now = time.time()
            cache_key = f'online_user_{user_id}'
            cache.set(cache_key, now, timeout=300)  # 5分钟过期

        # 清理过期的在线用户记录
        self.cleanup_expired_users()

        response = self.get_response(request)

        # 处理请求后
        return response

    def cleanup_expired_users(self):
        """清理过期的在线用户记录"""
        now = time.time()
        
        # 获取所有在线用户的键（使用更兼容的方式）
        try:
            # 尝试使用keys()方法（Redis等缓存支持）
            keys = cache.keys('online_user_*')
        except AttributeError:
            # 如果不支持keys()方法，使用一个替代方案
            # 注意：LocMemCache不支持keys()，这里需要使用其他方法
            # 对于开发环境，我们可以跳过清理或者使用一个全局变量来跟踪键
            return
        
        for key in keys:
            user_time = cache.get(key)
            if user_time and now - user_time > 300:  # 5分钟未活动
                cache.delete(key)