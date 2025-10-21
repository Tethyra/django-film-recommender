#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电影海报爬取工具
用于从电影网站爬取海报图片并保存到本地
"""

import os
import sys
import requests
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class PosterCrawler:
    def __init__(self, save_dir='media/posters', max_retries=3, delay=1):
        """
        初始化海报爬虫
        
        Args:
            save_dir: 图片保存目录
            max_retries: 最大重试次数
            delay: 请求间隔时间（秒）
        """
        self.save_dir = save_dir
        self.max_retries = max_retries
        self.delay = delay
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 初始化请求会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 已下载的图片URL集合，避免重复下载
        self.downloaded_urls = set()
        
    def get_page(self, url, params=None):
        """
        获取网页内容
        
        Args:
            url: 网页URL
            params: 请求参数
            
        Returns:
            BeautifulSoup对象或None
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                # 随机延迟，避免被反爬
                time.sleep(random.uniform(self.delay, self.delay * 2))
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.exceptions.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(random.uniform(2, 5))
                else:
                    print(f"多次请求失败，放弃: {url}")
                    return None
    
    def download_image(self, img_url, filename=None):
        """
        下载图片
        
        Args:
            img_url: 图片URL
            filename: 保存文件名
            
        Returns:
            保存的文件路径或None
        """
        if img_url in self.downloaded_urls:
            print(f"图片已下载: {img_url}")
            return None
            
        try:
            # 随机延迟
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(img_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # 确定文件名
            if not filename:
                # 从URL提取文件名
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                
                # 如果没有扩展名，添加.jpg
                if not os.path.splitext(filename)[1]:
                    filename += '.jpg'
            
            # 保存文件
            filepath = os.path.join(self.save_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_urls.add(img_url)
            print(f"下载成功: {filename}")
            return filepath
            
        except Exception as e:
            print(f"下载失败 {img_url}: {e}")
            return None
    
    def crawl_douban_movies(self, start=0, count=20):
        """
        从豆瓣电影Top250爬取海报
        
        Args:
            start: 起始位置
            count: 爬取数量
            
        Returns:
            下载的图片数量
        """
        print(f"开始从豆瓣电影Top250爬取海报 (起始位置: {start}, 数量: {count})")
        
        base_url = 'https://movie.douban.com/top250'
        downloaded_count = 0
        
        try:
            for i in range(0, count, 25):
                current_start = start + i
                params = {'start': current_start, 'filter': ''}
                
                print(f"正在爬取第 {current_start // 25 + 1} 页...")
                soup = self.get_page(base_url, params=params)
                
                if not soup:
                    continue
                
                # 找到所有电影条目
                movie_items = soup.find_all('div', class_='item')
                
                for item in movie_items:
                    if downloaded_count >= count:
                        break
                        
                    # 提取电影信息
                    img_tag = item.find('img')
                    if img_tag and 'src' in img_tag.attrs:
                        img_url = img_tag['src']
                        title = img_tag.get('alt', 'unknown_movie')
                        
                        # 清理文件名
                        filename = f"{title.replace(' ', '_').replace('/', '_')}_{downloaded_count + 1}.jpg"
                        
                        # 下载图片
                        if self.download_image(img_url, filename):
                            downloaded_count += 1
                
                if downloaded_count >= count:
                    break
                    
        except KeyboardInterrupt:
            print("\n用户中断爬取")
        except Exception as e:
            print(f"爬取过程中发生错误: {e}")
        
        print(f"豆瓣电影海报爬取完成，共下载 {downloaded_count} 张图片")
        return downloaded_count
    
    def crawl_themoviedb(self, api_key=None, language='zh-CN', page=1, count=20):
        """
        使用The Movie Database API爬取海报
        
        Args:
            api_key: TMDB API密钥
            language: 语言
            page: 页码
            count: 爬取数量
            
        Returns:
            下载的图片数量
        """
        if not api_key:
            print("请提供TMDB API密钥")
            return 0
            
        print(f"开始使用TMDB API爬取海报 (页面: {page}, 数量: {count})")
        
        base_url = 'https://api.themoviedb.org/3'
        image_base_url = 'https://image.tmdb.org/t/p/w500'
        downloaded_count = 0
        
        try:
            # 获取热门电影
            response = requests.get(
                f"{base_url}/movie/popular",
                params={
                    'api_key': api_key,
                    'language': language,
                    'page': page
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            for movie in data.get('results', []):
                if downloaded_count >= count:
                    break
                    
                if movie.get('poster_path'):
                    img_url = f"{image_base_url}{movie['poster_path']}"
                    title = movie.get('title', 'unknown_movie')
                    movie_id = movie.get('id', downloaded_count + 1)
                    
                    filename = f"{title.replace(' ', '_').replace('/', '_')}_{movie_id}.jpg"
                    
                    if self.download_image(img_url, filename):
                        downloaded_count += 1
            
        except Exception as e:
            print(f"TMDB API爬取失败: {e}")
        
        print(f"TMDB海报爬取完成，共下载 {downloaded_count} 张图片")
        return downloaded_count
    
    def crawl_movie_poster_db(self, page=1, count=20):
        """
        从Movie Poster Database爬取海报
        
        Args:
            page: 页码
            count: 爬取数量
            
        Returns:
            下载的图片数量
        """
        print(f"开始从Movie Poster Database爬取海报 (页面: {page}, 数量: {count})")
        
        base_url = 'https://www.movieposterdb.com'
        downloaded_count = 0
        
        try:
            soup = self.get_page(f"{base_url}/browse/movies?page={page}")
            
            if not soup:
                return 0
            
            # 找到所有海报缩略图
            poster_items = soup.find_all('div', class_='poster-thumb')
            
            for item in poster_items:
                if downloaded_count >= count:
                    break
                    
                img_tag = item.find('img')
                if img_tag and 'data-src' in img_tag.attrs:
                    # 提取大图URL
                    thumb_url = img_tag['data-src']
                    # 将缩略图URL转换为大图URL
                    img_url = thumb_url.replace('/thumbs/', '/posters/').replace('_thumb', '')
                    
                    title = img_tag.get('alt', 'unknown_movie').split('(')[0].strip()
                    
                    filename = f"{title.replace(' ', '_').replace('/', '_')}_{downloaded_count + 1}.jpg"
                    
                    if self.download_image(img_url, filename):
                        downloaded_count += 1
            
        except Exception as e:
            print(f"Movie Poster Database爬取失败: {e}")
        
        print(f"Movie Poster Database爬取完成，共下载 {downloaded_count} 张图片")
        return downloaded_count
    
    def crawl_from_url_list(self, url_list, prefix=''):
        """
        从URL列表中爬取图片
        
        Args:
            url_list: 图片URL列表
            prefix: 文件名前缀
            
        Returns:
            下载的图片数量
        """
        print(f"开始从URL列表爬取海报 (数量: {len(url_list)})")
        
        downloaded_count = 0
        
        for i, img_url in enumerate(url_list):
            try:
                filename = f"{prefix}_{i + 1}_{os.path.basename(img_url).split('?')[0]}"
                if self.download_image(img_url, filename):
                    downloaded_count += 1
            except Exception as e:
                print(f"处理URL失败 {img_url}: {e}")
        
        print(f"URL列表爬取完成，共下载 {downloaded_count} 张图片")
        return downloaded_count

def main():
    """
    主函数 - 演示如何使用海报爬虫
    """
    print("=" * 60)
    print("电影海报爬取工具")
    print("=" * 60)
    
    # 初始化爬虫，保存到项目的media/posters目录
    crawler = PosterCrawler(save_dir='media/posters', delay=1)
    
    try:
        # 菜单
        while True:
            print("\n请选择爬取方式:")
            print("1. 从豆瓣电影Top250爬取")
            print("2. 使用TMDB API爬取 (需要API密钥)")
            print("3. 从Movie Poster Database爬取")
            print("4. 退出")
            
            choice = input("请输入选项 (1-4): ")
            
            if choice == '1':
                try:
                    start = int(input("请输入起始位置 (0-249): "))
                    count = int(input("请输入爬取数量: "))
                    crawler.crawl_douban_movies(start=start, count=count)
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '2':
                api_key = input("请输入TMDB API密钥: ")
                if api_key:
                    try:
                        page = int(input("请输入页码: "))
                        count = int(input("请输入爬取数量: "))
                        crawler.crawl_themoviedb(api_key=api_key, page=page, count=count)
                    except ValueError:
                        print("请输入有效的数字")
            
            elif choice == '3':
                try:
                    page = int(input("请输入页码: "))
                    count = int(input("请输入爬取数量: "))
                    crawler.crawl_movie_poster_db(page=page, count=count)
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '4':
                print("感谢使用，再见！")
                break
            
            else:
                print("无效的选项，请重新选择")
                
    except KeyboardInterrupt:
        print("\n程序被中断")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()