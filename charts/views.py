#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表功能视图
为影视推荐系统提供数据可视化功能
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

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import cache_page
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
                
                # 美化文字
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
            elif chart_type == 'bar':
                # 柱状图
                labels = [item['label'] for item in data]
                values = [item['value'] for item in data]
                
                bars = ax.bar(labels, values, color='#4ECDC4', alpha=0.8, edgecolor='#26de81', linewidth=2)
                ax.set_title(kwargs.get('title', '数据统计'), fontsize=14, fontweight='bold')
                ax.set_xlabel(kwargs.get('xlabel', '类别'), fontsize=12)
                ax.set_ylabel(kwargs.get('ylabel', '数量'), fontsize=12)
                
                # 在柱状图上显示数值
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{value}', ha='center', va='bottom', fontsize=10, fontweight='bold')
                
                # 旋转x轴标签
                plt.xticks(rotation=45, ha='right')
                
                # 设置网格
                ax.grid(True, axis='y', alpha=0.3, linestyle='--')
                
            elif chart_type == 'line':
                # 折线图
                dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in data]
                values = [item['value'] for item in data]
                
                line = ax.plot(dates, values, marker='o', linewidth=3, markersize=6, 
                             color='#FF6B6B', markerfacecolor='white', markeredgecolor='#FF6B6B', markeredgewidth=2)
                ax.set_title(kwargs.get('title', '趋势分析'), fontsize=14, fontweight='bold')
                ax.set_xlabel(kwargs.get('xlabel', '日期'), fontsize=12)
                ax.set_ylabel(kwargs.get('ylabel', '数量'), fontsize=12)
                
                # 设置x轴日期格式
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
                plt.xticks(rotation=45)
                
                # 填充区域
                ax.fill_between(dates, values, alpha=0.3, color='#FF6B6B')
                
                # 设置网格
                ax.grid(True, alpha=0.3, linestyle='--')
                
            elif chart_type == 'horizontal_bar':
                # 水平柱状图
                labels = [item['label'] for item in data]
                values = [item['value'] for item in data]
                
                bars = ax.barh(labels, values, color='#96CEB4', alpha=0.8, edgecolor='#68d391', linewidth=2)
                ax.set_title(kwargs.get('title', '数据排名'), fontsize=14, fontweight='bold')
                ax.set_xlabel(kwargs.get('xlabel', '数量'), fontsize=12)
                ax.set_ylabel(kwargs.get('ylabel', '类别'), fontsize=12)
                
                # 在水平柱状图上显示数值
                for bar, value in zip(bars, values):
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                            f'{value}', ha='left', va='center', fontsize=10, fontweight='bold')
                
                # 设置网格
                ax.grid(True, axis='x', alpha=0.3, linestyle='--')
            
            # 美化图表
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cccccc')
            ax.spines['bottom'].set_color('#cccccc')
            
            plt.tight_layout()
            
            # 保存图表到内存
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
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
            
            # 今日新增
            today = timezone.now().date()
            new_reviews_today = Review.objects.filter(created_at__date=today).count()
            new_users_today = User.objects.filter(date_joined__date=today).count()
            
            return {
                'total_films': total_films,
                'total_categories': total_categories,
                'total_users': total_users,
                'total_reviews': total_reviews,
                'total_favorites': total_favorites,
                'total_watch_history': total_watch_history,
                'avg_rating': round(avg_rating, 1),
                'new_reviews_today': new_reviews_today,
                'new_users_today': new_users_today
            }
        except Exception as e:
            print(f"❌ 获取总体统计失败: {e}")
            import traceback
            traceback.print_exc()
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
            import traceback
            traceback.print_exc()
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
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_popular_films(limit=10):
        """获取热门电影数据"""
        try:
            popular_films = Film.objects.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(review_count__gt=0).order_by('-avg_rating')[:limit]
            
            return [{'label': film.title, 'value': round(film.avg_rating, 1), 'review_count': film.review_count} 
                   for film in popular_films]
        except Exception as e:
            print(f"❌ 获取热门电影失败: {e}")
            import traceback
            traceback.print_exc()
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
                
                # 统计当天的观看记录
                watch_count = WatchHistory.objects.filter(
                    watch_time__date=current_date
                ).count()
                
                trend_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'value': review_count,
                    'watch_count': watch_count
                })
            
            return trend_data
        except Exception as e:
            print(f"❌ 获取用户活动趋势失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_top_users(limit=10):
        """获取活跃用户数据"""
        try:
            active_users = User.objects.annotate(
                review_count=Count('reviews'),
                favorite_count=Count('favorites'),
                watch_count=Count('watch_history')
            ).filter(review_count__gt=0).order_by('-review_count')[:limit]
            
            return [{'label': user.username, 'value': user.review_count,
                    'favorite_count': user.favorite_count, 'watch_count': user.watch_count} 
                   for user in active_users]
        except Exception as e:
            print(f"❌ 获取活跃用户失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_monthly_trend(months=12):
        """获取月度趋势数据"""
        try:
            trend_data = []
            end_date = timezone.now()
            start_date = end_date - timedelta(days=months*30)
            
            for i in range(months):
                current_date = start_date + timedelta(days=i*30)
                next_date = current_date + timedelta(days=30)
                
                # 统计当月新增用户
                new_users = User.objects.filter(
                    date_joined__gte=current_date,
                    date_joined__lt=next_date
                ).count()
                
                # 统计当月新增评论
                new_reviews = Review.objects.filter(
                    created_at__gte=current_date,
                    created_at__lt=next_date
                ).count()
                
                trend_data.append({
                    'month': current_date.strftime('%Y-%m'),
                    'new_users': new_users,
                    'new_reviews': new_reviews
                })
            
            return trend_data
        except Exception as e:
            print(f"❌ 获取月度趋势失败: {e}")
            import traceback
            traceback.print_exc()
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
@cache_page(60 * 15)  # 缓存15分钟
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
        
        elif chart_type == 'monthly_trend':
            data = analyzer.get_monthly_trend()
            # 这里可以生成月度趋势图表
        
        return JsonResponse({
            'status': 'success',
            'data': data,
            'chart_image': chart_image,
            'generated_at': timezone.now().isoformat()
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
        
        elif chart_type == 'top_users':
            data = analyzer.get_top_users()
            title = '活跃用户排行'
            chart_image = chart_manager.generate_chart_image('horizontal_bar', data, title=title)
        
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

@login_required
def export_chart_data(request, chart_type):
    """导出图表数据"""
    try:
        analyzer = DataAnalyzer()
        
        data = {}
        filename = f'chart_data_{chart_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        if chart_type == 'all':
            data = {
                'overall_stats': analyzer.get_overall_stats(),
                'category_distribution': analyzer.get_category_distribution(),
                'rating_distribution': analyzer.get_rating_distribution(),
                'popular_films': analyzer.get_popular_films(),
                'user_activity': analyzer.get_user_activity_trend(),
                'top_users': analyzer.get_top_users(),
                'monthly_trend': analyzer.get_monthly_trend(),
                'exported_at': datetime.now().isoformat()
            }
        elif chart_type == 'category_distribution':
            data = analyzer.get_category_distribution()
        elif chart_type == 'rating_distribution':
            data = analyzer.get_rating_distribution()
        elif chart_type == 'popular_films':
            data = analyzer.get_popular_films()
        elif chart_type == 'user_activity':
            data = analyzer.get_user_activity_trend()
        elif chart_type == 'top_users':
            data = analyzer.get_top_users()
        elif chart_type == 'monthly_trend':
            data = analyzer.get_monthly_trend()
        
        response = HttpResponse(json.dumps(data, ensure_ascii=False, indent=2), 
                               content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        print(f"❌ 导出图表数据失败: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

# API视图 - 用于前端异步加载数据
@login_required
def api_overall_stats(request):
    """获取总体统计数据API"""
    try:
        data = DataAnalyzer.get_overall_stats()
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def api_category_distribution(request):
    """获取分类分布数据API"""
    try:
        data = DataAnalyzer.get_category_distribution()
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def api_rating_distribution(request):
    """获取评分分布数据API"""
    try:
        data = DataAnalyzer.get_rating_distribution()
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def api_popular_films(request):
    """获取热门电影数据API"""
    try:
        limit = int(request.GET.get('limit', 10))
        data = DataAnalyzer.get_popular_films(limit)
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def api_user_activity(request):
    """获取用户活动数据API"""
    try:
        days = int(request.GET.get('days', 30))
        data = DataAnalyzer.get_user_activity_trend(days)
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def api_top_users(request):
    """获取活跃用户数据API"""
    try:
        limit = int(request.GET.get('limit', 10))
        data = DataAnalyzer.get_top_users(limit)
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})