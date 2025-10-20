# film_project_channels/main/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.cache import cache
import time

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 接受WebSocket连接
        await self.accept()
        
        # 如果用户已登录，更新在线状态
        if self.scope['user'].is_authenticated:
            user_id = self.scope['user'].id
            await self.update_online_status(user_id, True)
        
        # 发送当前在线人数
        online_count = await self.get_online_count()
        await self.send_online_count(online_count)

    async def disconnect(self, close_code):
        # 用户断开连接时更新在线状态
        if self.scope['user'].is_authenticated:
            user_id = self.scope['user'].id
            await self.update_online_status(user_id, False)
        
        # 发送更新后的在线人数
        online_count = await self.get_online_count()
        await self.send_online_count(online_count)

    async def receive(self, text_data):
        # 接收客户端发送的消息
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'request_online_count':
            # 客户端请求在线人数
            online_count = await self.get_online_count()
            await self.send_online_count(online_count)

    @database_sync_to_async
    def update_online_status(self, user_id, is_online):
        """更新用户在线状态"""
        cache_key = f'online_user_{user_id}'
        if is_online:
            # 用户上线，记录当前时间
            cache.set(cache_key, time.time(), timeout=300)  # 5分钟过期
        else:
            # 用户下线，移除缓存
            cache.delete(cache_key)

    @database_sync_to_async
    def get_online_count(self):
        """获取当前在线人数"""
        try:
            # 获取所有在线用户的键
            keys = cache.keys('online_user_*')
            now = time.time()
            online_count = 0
            
            # 清理过期的用户记录并计数
            for key in keys:
                user_time = cache.get(key)
                if user_time:
                    if now - user_time <= 300:  # 5分钟内活动过
                        online_count += 1
                    else:
                        cache.delete(key)
            
            return online_count
        except AttributeError:
            # 如果缓存后端不支持keys()方法，返回0
            return 0

    async def send_online_count(self, count):
        """发送在线人数到客户端"""
        await self.send(text_data=json.dumps({
            'type': 'online_count',
            'count': count
        }))