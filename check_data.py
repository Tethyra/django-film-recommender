#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据检查脚本
检查数据库中的数据完整性
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'film_recommender.settings')
django.setup()

from main.models import Category, Film, Review, User

def check_database():
    """检查数据库完整性"""
    print("=" * 60)
    print("🎬 数据库完整性检查工具")
    print("=" * 60)
    
    try:
        # 检查分类数据
        print("\n📊 检查分类数据...")
        categories = Category.objects.all()
        print(f"   发现 {categories.count()} 个分类")
        
        if categories.count() == 0:
            print("   ⚠️ 警告: 没有找到分类数据")
        else:
            for cat in categories[:5]:
                print(f"   - {cat.name} ({cat.films.count()}部作品)")
        
        # 检查电影数据
        print("\n🎥 检查电影数据...")
        films = Film.objects.all()
        print(f"   发现 {films.count()} 部电影")
        
        if films.count() == 0:
            print("   ⚠️ 警告: 没有找到电影数据")
        else:
            for film in films[:5]:
                print(f"   - {film.title} ({film.director})")
        
        # 检查用户数据
        print("\n👥 检查用户数据...")
        users = User.objects.all()
        print(f"   发现 {users.count()} 个用户")
        
        if users.count() == 0:
            print("   ⚠️ 警告: 没有找到用户数据")
        else:
            for user in users[:5]:
                print(f"   - {user.username} ({user.email})")
        
        # 检查评论数据
        print("\n💬 检查评论数据...")
        reviews = Review.objects.all()
        print(f"   发现 {reviews.count()} 条评论")
        
        if reviews.count() > 0:
            for review in reviews[:5]:
                print(f"   - {review.user.username} 对 {review.film.title} 的评论 (评分: {review.rating})")
        
        # 检查数据关联
        print("\n🔗 检查数据关联...")
        
        # 检查电影分类关联
        film_without_categories = Film.objects.filter(categories__isnull=True).count()
        if film_without_categories > 0:
            print(f"   ⚠️ 警告: 有 {film_without_categories} 部电影没有分类")
        else:
            print("   ✅ 所有电影都有分类")
        
        # 检查评分数据
        films_without_rating = Film.objects.filter(rating_count=0).count()
        if films_without_rating > 0:
            print(f"   ℹ️ 信息: 有 {films_without_rating} 部电影没有评分")
        
        print("\n✅ 数据检查完成！")
        
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()