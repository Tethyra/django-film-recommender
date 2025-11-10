"""
URL configuration for film_recommender project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # 包含main应用的URL
]

# 开发环境下配置静态文件和媒体文件的URL路由
if settings.DEBUG:
    # 配置静态文件URL
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # 配置媒体文件URL - 这是缺少的部分
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)