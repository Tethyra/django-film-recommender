#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化图表功能模块
为影视推荐系统添加数据可视化功能
"""

import os
import sys
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64

# 设置matplotlib中文字体，防止中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置Django环境
def setup_django_env():
    """设置Django环境"""
    try:
        project_root = os.path.abspath(os.path.dirname(__file__))
        # 确保项目根目录在Python路径中
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # 设置Django环境变量
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_recommender.settings")
        
        import django
        django.setup()
        print("✅ Django环境设置成功")
        return True
        
    except Exception as e:
        print(f"❌ Django环境设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 先设置Django环境
if not setup_django_env():
    print("❌ 无法运行图表功能模块")
    sys.exit(1)

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from main.models import Film, Category, Review, Favorite, WatchHistory, User

class ChartManager:
    """图表管理类"""
    
    @staticmethod
    def generate_chart_image(chart_type, data, **kwargs):
        """生成图表图片"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == 'pie':
                # 饼图
                labels = [item['label'] for item in data]
                sizes = [item['value'] for item in data]
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                         '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
                
                wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                colors=colors[:len(labels)], startangle=90)
                ax.set_title(kwargs.get('title', '数据分布'), fontsize=14, fontweight='bold')
                
            elif chart_type == 'bar':
                # 柱状图
                labels = [item['label'] for item in data]
                values = [item['value'] for item in data]
                
                bars = ax.bar(labels, values, color='#4ECDC4', alpha=0.8)
                ax.set_title(kwargs.get('title', '数据统计'), fontsize=14, fontweight='bold')
                ax.set_xlabel(kwargs.get('xlabel', '类别'), fontsize=12)
                ax.set_ylabel(kwargs.get('ylabel', '数量'), fontsize=12)
                
                # 在柱状图上显示数值
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{value}', ha='center', va='bottom', fontsize=10)
                
                # 旋转x轴标签
                plt.xticks(rotation=45, ha='right')
                
            elif chart_type == 'line':
                # 折线图
                dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in data]
                values = [item['value'] for item in data]
                
                ax.plot(dates, values, marker='o', linewidth=2, markersize=6, color='#FF6B6B')
                ax.set_title(kwargs.get('title', '趋势分析'), fontsize=14, fontweight='bold')
                ax.set_xlabel(kwargs.get('xlabel', '日期'), fontsize=12)
                ax.set_ylabel(kwargs.get('ylabel', '数量'), fontsize=12)
                
                # 设置x轴日期格式
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                plt.xticks(rotation=45)
                
            elif chart_type == 'horizontal_bar':
                # 水平柱状图
                labels = [item['label'] for item in data]
                values = [item['value'] for item in data]
                
                bars = ax.barh(labels, values, color='#96CEB4', alpha=0.8)
                ax.set_title(kwargs.get('title', '数据排名'), fontsize=14, fontweight='bold')
                ax.set_xlabel(kwargs.get('xlabel', '数量'), fontsize=12)
                ax.set_ylabel(kwargs.get('ylabel', '类别'), fontsize=12)
                
                # 在水平柱状图上显示数值
                for bar, value in zip(bars, values):
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                            f'{value}', ha='left', va='center', fontsize=10)
            
            plt.tight_layout()
            
            # 保存图表到内存
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # 转换为base64编码
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"❌ 图表生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

class DataAnalyzer:
    """数据分析类"""
    
    @staticmethod
    def get_overall_stats():
        """获取总体统计数据"""
        try:
            total_films = Film.objects.count()
            total_categories = Category.objects.count()
            total_users = User.objects.count()
            total_reviews = Review.objects.count()
            total_favorites = Favorite.objects.count()
            total_watch_history = WatchHistory.objects.count()
            
            # 平均评分
            avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
            
            return {
                'total_films': total_films,
                'total_categories': total_categories,
                'total_users': total_users,
                'total_reviews': total_reviews,
                'total_favorites': total_favorites,
                'total_watch_history': total_watch_history,
                'avg_rating': round(avg_rating, 1)
            }
        except Exception as e:
            print(f"❌ 获取总体统计失败: {e}")
            return {}
    
    @staticmethod
    def get_category_distribution():
        """获取分类分布数据"""
        try:
            categories = Category.objects.annotate(
                film_count=Count('films')
            ).filter(film_count__gt=0).order_by('-film_count')
            
            return [{'label': cat.name, 'value': cat.film_count} for cat in categories]
        except Exception as e:
            print(f"❌ 获取分类分布失败: {e}")
            return []
    
    @staticmethod
    def get_rating_distribution():
        """获取评分分布数据"""
        try:
            rating_stats = []
            for rating in range(1, 6):
                count = Review.objects.filter(rating=rating).count()
                rating_stats.append({'label': f'{rating}星', 'value': count})
            
            return rating_stats
        except Exception as e:
            print(f"❌ 获取评分分布失败: {e}")
            return []
    
    @staticmethod
    def get_popular_films(limit=10):
        """获取热门电影数据"""
        try:
            popular_films = Film.objects.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(review_count__gt=0).order_by('-avg_rating')[:limit]
            
            return [{'label': film.title, 'value': round(film.avg_rating, 1)} for film in popular_films]
        except Exception as e:
            print(f"❌ 获取热门电影失败: {e}")
            return []
    
    @staticmethod
    def get_user_activity_trend(days=30):
        """获取用户活动趋势数据"""
        try:
            trend_data = []
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            for i in range(days):
                current_date = start_date + timedelta(days=i)
                next_date = current_date + timedelta(days=1)
                
                # 统计当天的评论数量
                review_count = Review.objects.filter(
                    created_at__date=current_date
                ).count()
                
                trend_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'value': review_count
                })
            
            return trend_data
        except Exception as e:
            print(f"❌ 获取用户活动趋势失败: {e}")
            return []
    
    @staticmethod
    def get_top_users(limit=10):
        """获取活跃用户数据"""
        try:
            active_users = User.objects.annotate(
                review_count=Count('reviews')
            ).filter(review_count__gt=0).order_by('-review_count')[:limit]
            
            return [{'label': user.username, 'value': user.review_count} for user in active_users]
        except Exception as e:
            print(f"❌ 获取活跃用户失败: {e}")
            return []

# 视图函数
@login_required
def charts_dashboard(request):
    """图表仪表板视图"""
    try:
        # 获取分析数据
        analyzer = DataAnalyzer()
        
        context = {
            'overall_stats': analyzer.get_overall_stats(),
            'current_page': 'charts',
        }
        
        return render(request, 'charts/dashboard.html', context)
    except Exception as e:
        print(f"❌ 图表仪表板视图失败: {e}")
        import traceback
        traceback.print_exc()
        return render(request, 'error.html', {'message': '图表加载失败'})

@login_required
def get_chart_data(request, chart_type):
    """获取图表数据API"""
    try:
        analyzer = DataAnalyzer()
        chart_manager = ChartManager()
        
        data = []
        chart_image = None
        
        if chart_type == 'category_distribution':
            data = analyzer.get_category_distribution()
            chart_image = chart_manager.generate_chart_image(
                'pie', data, title='影视分类分布', 
                xlabel='分类', ylabel='电影数量'
            )
        
        elif chart_type == 'rating_distribution':
            data = analyzer.get_rating_distribution()
            chart_image = chart_manager.generate_chart_image(
                'bar', data, title='用户评分分布',
                xlabel='评分', ylabel='评论数量'
            )
        
        elif chart_type == 'popular_films':
            data = analyzer.get_popular_films()
            chart_image = chart_manager.generate_chart_image(
                'horizontal_bar', data, title='热门电影排行',
                xlabel='评分', ylabel='电影名称'
            )
        
        elif chart_type == 'user_activity':
            data = analyzer.get_user_activity_trend()
            chart_image = chart_manager.generate_chart_image(
                'line', data, title='用户活动趋势',
                xlabel='日期', ylabel='评论数量'
            )
        
        elif chart_type == 'top_users':
            data = analyzer.get_top_users()
            chart_image = chart_manager.generate_chart_image(
                'horizontal_bar', data, title='活跃用户排行',
                xlabel='评论数量', ylabel='用户名'
            )
        
        return JsonResponse({
            'status': 'success',
            'data': data,
            'chart_image': chart_image
        })
        
    except Exception as e:
        print(f"❌ 获取图表数据失败: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def generate_matplotlib_chart(request):
    """生成matplotlib图表"""
    try:
        chart_type = request.GET.get('type', 'category_distribution')
        analyzer = DataAnalyzer()
        chart_manager = ChartManager()
        
        data = []
        title = ''
        
        if chart_type == 'category_distribution':
            data = analyzer.get_category_distribution()
            title = '影视分类分布'
            chart_image = chart_manager.generate_chart_image('pie', data, title=title)
        
        elif chart_type == 'rating_distribution':
            data = analyzer.get_rating_distribution()
            title = '用户评分分布'
            chart_image = chart_manager.generate_chart_image('bar', data, title=title)
        
        elif chart_type == 'popular_films':
            data = analyzer.get_popular_films()
            title = '热门电影排行'
            chart_image = chart_manager.generate_chart_image('horizontal_bar', data, title=title)
        
        elif chart_type == 'user_activity':
            data = analyzer.get_user_activity_trend()
            title = '用户活动趋势'
            chart_image = chart_manager.generate_chart_image('line', data, title=title)
        
        else:
            return HttpResponse('图表类型不支持', status=400)
        
        if chart_image:
            return HttpResponse(chart_image, content_type='text/plain')
        else:
            return HttpResponse('图表生成失败', status=500)
            
    except Exception as e:
        print(f"❌ 生成matplotlib图表失败: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'图表生成失败: {str(e)}', status=500)

# URL配置
urlpatterns = [
    path('charts/', charts_dashboard, name='charts_dashboard'),
    path('charts/data/<str:chart_type>/', get_chart_data, name='get_chart_data'),
    path('charts/matplotlib/<str:chart_type>/', generate_matplotlib_chart, name='generate_matplotlib_chart'),
]

if __name__ == "__main__":
    # 测试图表生成功能
    print("="*60)
    print("图表功能测试")
    print("="*60)
    
    try:
        analyzer = DataAnalyzer()
        chart_manager = ChartManager()
        
        print("\n1. 测试总体统计数据:")
        stats = analyzer.get_overall_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n2. 测试分类分布数据:")
        category_data = analyzer.get_category_distribution()
        for item in category_data[:5]:
            print(f"   {item['label']}: {item['value']}")
        
        print("\n3. 测试图表生成:")
        if category_data:
            chart_image = chart_manager.generate_chart_image('pie', category_data[:5], title='测试图表')
            if chart_image:
                print("   ✅ 图表生成成功")
            else:
                print("   ❌ 图表生成失败")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()