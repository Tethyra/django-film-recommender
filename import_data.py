#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入脚本
从CSV文件导入分类和电影数据
"""

import os
import sys
import django
import csv
from datetime import datetime
import random

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'film_recommender.settings')
django.setup()

from main.models import Category, Film, User
from django.contrib.auth.models import Group

def import_categories():
    """从CSV文件导入分类数据"""
    print("📥 正在导入分类数据...")
    
    try:
        with open('categories.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                # 检查分类是否已存在
                category, created = Category.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'description': row['description'],
                        'slug': row['slug']
                    }
                )
                
                if created:
                    count += 1
                    print(f"   ✅ 新增分类: {row['name']}")
                else:
                    print(f"   ℹ️ 分类已存在: {row['name']}")
            
            print(f"📊 分类导入完成，新增 {count} 个分类")
            return count
            
    except FileNotFoundError:
        print("❌ 未找到categories.csv文件")
        return 0
    except Exception as e:
        print(f"❌ 导入分类时出错: {str(e)}")
        return 0

def import_films():
    """从CSV文件导入电影数据"""
    print("\n📥 正在导入电影数据...")
    
    try:
        with open('films.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                # 检查电影是否已存在
                film_exists = Film.objects.filter(title=row['title']).exists()
                
                if not film_exists:
                    # 处理上映日期
                    release_date = None
                    if row['release_date']:
                        try:
                            release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
                        except:
                            pass
                    
                    # 创建电影
                    film = Film(
                        title=row['title'],
                        director=row['director'],
                        actors=row['actors'],
                        release_date=release_date,
                        description=row['description'],
                        rating=float(row['rating']) if row['rating'] else 0,
                        rating_count=int(row['rating_count']) if row['rating_count'] else 0
                    )
                    film.save()
                    
                    # 添加分类
                    if row['categories']:
                        category_names = [cat.strip() for cat in row['categories'].split(',')]
                        for category_name in category_names:
                            try:
                                category = Category.objects.get(name=category_name)
                                film.categories.add(category)
                            except Category.DoesNotExist:
                                print(f"   ⚠️ 分类不存在: {category_name}")
                    
                    count += 1
                    print(f"   ✅ 新增电影: {row['title']}")
                else:
                    print(f"   ℹ️ 电影已存在: {row['title']}")
            
            print(f"📊 电影导入完成，新增 {count} 部电影")
            return count
            
    except FileNotFoundError:
        print("❌ 未找到films.csv文件")
        return 0
    except Exception as e:
        print(f"❌ 导入电影时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

def create_sample_users():
    """创建示例用户"""
    print("\n👥 正在创建示例用户...")
    
    sample_users = [
        {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'password123',
            'bio': '电影爱好者，喜欢各种类型的电影',
            'favorite_categories': '动作,科幻,喜剧'
        },
        {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'password123',
            'bio': '资深影评人，专注于独立电影和纪录片',
            'favorite_categories': '剧情,纪录片,文艺'
        },
        {
            'username': 'user3',
            'email': 'user3@example.com',
            'password': 'password123',
            'bio': '电视剧迷，追各种热门剧集',
            'favorite_categories': '电视剧,悬疑,犯罪'
        }
    ]
    
    count = 0
    for user_data in sample_users:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                bio=user_data['bio'],
                favorite_categories=user_data['favorite_categories']
            )
            count += 1
            print(f"   ✅ 创建用户: {user_data['username']}")
        else:
            print(f"   ℹ️ 用户已存在: {user_data['username']}")
    
    print(f"📊 用户创建完成，新增 {count} 个用户")
    return count

def main():
    print("=" * 60)
    print("🎬 Django影视推荐系统 - 数据导入工具")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 导入分类
        category_count = import_categories()
        
        # 导入电影
        film_count = import_films()
        
        # 创建示例用户
        user_count = create_sample_users()
        
        print("\n" + "=" * 60)
        print("🎉 数据导入完成！")
        print(f"📊 总计新增:")
        print(f"   - 分类: {category_count} 个")
        print(f"   - 电影: {film_count} 部")
        print(f"   - 用户: {user_count} 个")
        print("💡 提示: 可以使用 python download_posters.py 下载电影海报")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 导入过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()