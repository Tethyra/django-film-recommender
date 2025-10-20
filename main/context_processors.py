# main/context_processors.py
from django.core.cache import cache
import time

def online_user_count(request):
    """提供在线用户数量给模板"""
    now = time.time()
    online_count = 0
    
    try:
        # 尝试使用keys()方法获取所有在线用户键
        keys = cache.keys('online_user_*')
        
        # 清理过期的用户记录并计数
        for key in keys:
            user_time = cache.get(key)
            if user_time:
                if now - user_time <= 300:  # 5分钟内活动过
                    online_count += 1
                else:
                    cache.delete(key)
    except AttributeError:
        # 如果缓存后端不支持keys()方法（如LocMemCache）
        # 使用一个替代方案，或者返回0
        # 对于开发环境，可以使用一个简单的估算或者固定值
        online_count = 0
    
    return {
        'online_user_count': online_count
    }