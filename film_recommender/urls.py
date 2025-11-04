"""
影视推荐系统 - 主URL配置
"""

from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    # 管理员界面
    path('admin/', admin.site.urls),
    
    # 主应用URL
    path('', include('main.urls')),
    
    # 图表功能
    path('charts/', include('charts.urls')),
]

# 开发环境下的媒体文件配置
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    # 开发环境下提供静态文件服务
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # 添加媒体文件的URL配置（这是缺失的部分）
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
