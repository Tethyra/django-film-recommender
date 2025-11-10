#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
影视推荐系统 - 海报下载工具
用于重新下载误删的电影海报文件
下载目录：G:\\film_project\\static\\posters
文件名格式：电影名_medium.jpg
"""

import os
import requests
import sys
from datetime import datetime

class PosterDownloader:
    def __init__(self):
        self.api_key = "8d60f94ecd468445247d2e956f979364"  # TMDB API密钥
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"  # 中等分辨率海报
        self.download_dir = "G:\\film_project\\static\\posters"
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
        
        # 常见电影列表（根据用户截图中的文件名）
        self.popular_movies = [
            "阿甘正传",
            "盗梦空间", 
            "泰坦尼克号",
            "肖申克的救赎",
            "星际穿越",
            "楚门的世界",
            "千与千寻",
            "疯狂动物城",
            "寻梦环游记",
            "飞屋环游记",
            "摔跤吧爸爸",
            "三傻大闹宝莱坞",
            "复仇者联盟",
            "钢铁侠",
            "蜘蛛侠",
            "蝙蝠侠",
            "超人",
            "美国队长",
            "雷神",
            "绿巨人"
        ]
        
    def search_movie(self, movie_name, year=None):
        """搜索电影信息"""
        print(f"🔍 正在搜索电影: {movie_name}")
        
        try:
            url = f"{self.base_url}/search/movie"
            params = {
                "api_key": self.api_key,
                "query": movie_name,
                "language": "zh-CN",
                "include_adult": False
            }
            
            if year:
                params["year"] = year
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data["results"]:
                # 返回第一个搜索结果
                return data["results"][0]
            else:
                print(f"❌ 未找到电影: {movie_name}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 搜索电影失败 {movie_name}: {str(e)}")
            return None
    
    def download_poster(self, movie_info, movie_name):
        """下载电影海报"""
        if not movie_info or "poster_path" not in movie_info or not movie_info["poster_path"]:
            print(f"❌ 没有找到 {movie_name} 的海报信息")
            return False
        
        try:
            # 构建海报URL
            poster_url = f"{self.image_base_url}{movie_info['poster_path']}"
            print(f"📥 正在下载海报: {poster_url}")
            
            # 构建文件名
            filename = f"{movie_name}_medium.jpg"
            filepath = os.path.join(self.download_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(filepath):
                print(f"ℹ️ 海报已存在: {filename}")
                return True
            
            # 下载海报
            response = requests.get(poster_url, timeout=30)
            response.raise_for_status()
            
            # 保存海报
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 海报下载成功: {filename}")
            print(f"💾 保存路径: {filepath}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 下载海报失败 {movie_name}: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 保存海报失败 {movie_name}: {str(e)}")
            return False
    
    def download_all_posters(self, movies=None):
        """下载所有电影海报"""
        print("="*60)
        print("🎬 影视推荐系统 - 海报批量下载")
        print("="*60)
        print(f"📁 下载目录: {self.download_dir}")
        print(f"🎯 计划下载: {len(movies) if movies else len(self.popular_movies)} 个海报")
        print("="*60)
        
        movies_to_download = movies if movies else self.popular_movies
        success_count = 0
        fail_count = 0
        
        for i, movie_name in enumerate(movies_to_download, 1):
            print(f"\n{i}/{len(movies_to_download)}")
            movie_info = self.search_movie(movie_name)
            
            if movie_info:
                if self.download_poster(movie_info, movie_name):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1
        
        print("\n" + "="*60)
        print("📊 下载完成报告")
        print("="*60)
        print(f"✅ 成功下载: {success_count} 个海报")
        print(f"❌ 下载失败: {fail_count} 个海报")
        print(f"📁 下载目录: {self.download_dir}")
        
        # 显示已下载的文件
        downloaded_files = [f for f in os.listdir(self.download_dir) if f.endswith("_medium.jpg")]
        print(f"\n📋 已下载的海报文件:")
        for i, filename in enumerate(downloaded_files, 1):
            print(f"   {i}. {filename}")
        
        return success_count
    
    def download_single_poster(self, movie_name):
        """下载单个电影海报"""
        print("="*60)
        print(f"🎬 下载单个海报: {movie_name}")
        print("="*60)
        
        movie_info = self.search_movie(movie_name)
        
        if movie_info:
            return self.download_poster(movie_info, movie_name)
        else:
            return False
    
    def set_download_dir(self, new_dir):
        """设置下载目录"""
        self.download_dir = new_dir
        os.makedirs(self.download_dir, exist_ok=True)
        print(f"📁 下载目录已设置为: {self.download_dir}")
    
    def list_available_movies(self):
        """列出可用的电影列表"""
        print("="*60)
        print("🎬 可用的电影列表")
        print("="*60)
        for i, movie in enumerate(self.popular_movies, 1):
            print(f"   {i:2d}. {movie}")
        print("="*60)
        print(f"总计: {len(self.popular_movies)} 部电影")

def main():
    """主函数"""
    downloader = PosterDownloader()
    
    print("="*60)
    print("🎬 影视推荐系统 - 海报下载工具")
    print("="*60)
    print("功能:")
    print("1. 批量下载热门电影海报")
    print("2. 下载单个电影海报")
    print("3. 列出可用电影列表")
    print("4. 自定义下载目录")
    print("="*60)
    
    while True:
        print("\n请选择操作:")
        print("1. 批量下载所有热门电影海报")
        print("2. 下载单个电影海报")
        print("3. 列出可用电影列表")
        print("4. 修改下载目录")
        print("5. 退出程序")
        
        choice = input("请输入选项 (1-5): ").strip()
        
        if choice == "1":
            # 批量下载
            downloader.download_all_posters()
            
        elif choice == "2":
            # 单个下载
            movie_name = input("请输入电影名称: ").strip()
            if movie_name:
                downloader.download_single_poster(movie_name)
            else:
                print("❌ 请输入有效的电影名称")
                
        elif choice == "3":
            # 列出电影
            downloader.list_available_movies()
            
        elif choice == "4":
            # 修改目录
            new_dir = input("请输入新的下载目录 (默认: G:\\film_project\\static\\posters): ").strip()
            if new_dir:
                downloader.set_download_dir(new_dir)
            else:
                print("ℹ️ 保持默认下载目录")
                
        elif choice == "5":
            # 退出
            print("👋 感谢使用海报下载工具！")
            break
            
        else:
            print("❌ 无效的选项，请重新选择")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()