"""
URL configuration for film_recommender project.
修复后的完整URL配置文件
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # 包含main应用的URL
]

if settings.DEBUG:
    # 开发环境下提供静态文件服务
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # 添加媒体文件URL路由配置 - 修复海报显示问题
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)