#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库修复脚本 - 解决 main_category 表缺少 updated_at 字段的问题
"""

import os
import django
import MySQLdb

def fix_database():
    """修复数据库问题"""
    
    # 设置Django环境
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_recommender.settings")
    django.setup()
    
    try:
        # 1. 检查并应用迁移
        print("正在检查和应用数据库迁移...")
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        
        # 2. 检查字段是否存在
        print("正在检查数据库表结构...")
        
        # 使用原始SQL检查字段
        from django.db import connection
        cursor = connection.cursor()
        
        # 检查main_category表的字段
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'main_category' AND COLUMN_NAME = 'updated_at'
        """)
        
        result = cursor.fetchone()
        
        if not result:
            print("发现问题：main_category表缺少updated_at字段")
            print("正在手动添加字段...")
            
            # 手动添加缺失的字段
            cursor.execute("""
                ALTER TABLE main_category 
                ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            """)
            print("成功添加updated_at字段")
        else:
            print("✓ main_category表结构正常")
        
        # 3. 检查数据是否存在
        print("\n正在检查分类数据...")
        from main.models import Category
        
        if Category.objects.count() == 0:
            print("警告：分类表为空，正在导入示例数据...")
            import import_data
            import_data.import_categories()
            print("成功导入分类数据")
        else:
            print(f"✓ 发现 {Category.objects.count()} 个分类")
        
        # 4. 检查电影数据
        from main.models import Film
        if Film.objects.count() == 0:
            print("警告：电影表为空，建议导入示例数据")
            print("请运行: python import_data.py")
        else:
            print(f"✓ 发现 {Film.objects.count()} 部电影")
        
        print("\n✓ 数据库修复完成！")
        print("\n请重新启动服务器:")
        print("python manage.py runserver")
        
    except Exception as e:
        print(f"\n❌ 修复过程中出现错误: {str(e)}")
        print("\n建议方案:")
        print("1. 重新创建数据库:")
        print("   mysql -u root -p -e \"DROP DATABASE film_recommender;\"")
        print("   mysql -u root -p -e \"CREATE DATABASE film_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\"")
        print("   python manage.py migrate")
        print("   python import_data.py")
        print()
        print("2. 或手动添加字段:")
        print("   mysql -u root -p film_recommender")
        print("   ALTER TABLE main_category ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;")

if __name__ == "__main__":
    print("=== Django影视推荐系统数据库修复工具 ===\n")
    fix_database()