#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级图片下载脚本
使用ImageManager类来下载和处理电影海报
"""

import os
import sys
import django
import time
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'film_recommender.settings')
django.setup()

from main.models import Film
from main.image_utils import ImageManager

def main():
    print("=" * 60)
    print("🎬 高级电影海报下载工具")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Django环境: {django.get_version()}")
    print("=" * 60)
    
    try:
        # 获取所有电影
        films = Film.objects.all()
        total_films = films.count()
        
        if total_films == 0:
            print("❌ 数据库中没有电影数据，请先导入电影数据")
            print("   可以使用: python import_data.py")
            return
        
        print(f"📊 发现 {total_films} 部电影")
        print()
        
        # 初始化ImageManager
        image_manager = ImageManager()
        
        # 创建目录
        poster_dir, avatar_dir = image_manager.create_image_directory()
        print(f"📁 海报存储目录: {poster_dir}")
        print(f"📁 头像存储目录: {avatar_dir}")
        print()
        
        # 下载海报
        print("🚀 开始下载海报...")
        print("-" * 60)
        
        start_time = time.time()
        success_count, total_count = image_manager.download_film_posters(films)
        
        # 统计结果
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("-" * 60)
        print("📊 下载完成统计")
        print("-" * 60)
        print(f"✅ 成功: {success_count} 张")
        print(f"❌ 失败: {total_count - success_count} 张")
        print(f"📈 成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        print(f"⏱️ 用时: {elapsed_time:.1f} 秒")
        print()
        
        # 验证下载结果
        print("🔍 验证下载结果...")
        valid_posters = Film.objects.exclude(poster__isnull=True).exclude(poster__exact='').count()
        print(f"✅ 有效海报: {valid_posters} 张")
        
        if valid_posters > 0:
            print("🎉 图片下载任务完成！")
            print("💡 提示: 可以通过以下URL访问图片:")
            print("   http://localhost:8000/media/posters/1.jpg")
            print("   http://localhost:8000/media/posters/2.jpg")
        else:
            print("⚠️ 警告: 没有成功下载任何海报")
            print("   建议检查网络连接或使用本地创建模式")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        print("💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 确保Django环境正确配置")
        print("   3. 检查数据库连接")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

if __name__ == "__main__":
    main()