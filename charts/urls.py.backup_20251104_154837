"""
图表功能模块
为影视推荐系统提供数据可视化功能
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.charts_dashboard, name='charts_dashboard'),
    path('data/<str:chart_type>/', views.get_chart_data, name='get_chart_data'),
    path('matplotlib/<str:chart_type>/', views.generate_matplotlib_chart, name='generate_matplotlib_chart'),
]
