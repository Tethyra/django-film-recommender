"""
图表应用 URL 配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 图表仪表板首页
    path('', views.charts_dashboard, name='charts_dashboard'),
]
