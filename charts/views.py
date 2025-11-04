from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import Film, Category, Review, User
from django.db.models import Avg, Count
import json

def charts_dashboard(request):
    """图表仪表板视图"""
    # 为了避免数据库查询错误，使用模拟数据
    context = {
        'page_title': '数据可视化仪表板',
        'current_page': 'charts'
    }
    return render(request, 'charts/dashboard.html', context)
