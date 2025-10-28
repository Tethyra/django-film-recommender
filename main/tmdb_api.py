import os
import requests
import json
from django.conf import settings
from django.core.files import File
from urllib.parse import quote


class TMDBApi:
    """TMDB API工具类"""

    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.api_url = settings.TMDB_API_URL
        self.image_url = settings.TMDB_IMAGE_URL
        self.poster_sizes = settings.TMDB_POSTER_SIZES

        # 创建海报存储目录
        os.makedirs(settings.POSTER_STORAGE_PATH, exist_ok=True)

    def search_movie(self, title, year=None):
        """
        搜索电影

        Args:
            title: 电影标题
            year: 上映年份

        Returns:
            电影信息字典或None
        """
        if not self.api_key:
            print("TMDB API密钥未设置")
            return None

        try:
            url = f"{self.api_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': quote(title),
                'language': 'zh-CN',
                'include_adult': 'false'
            }

            if year:
                params['year'] = year

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('results'):
                return data['results'][0]  # 返回第一个匹配结果
            return None

        except Exception as e:
            print(f"搜索电影失败 {title}: {e}")
            return None

    def get_movie_details(self, movie_id):
        """
        获取电影详细信息

        Args:
            movie_id: TMDB电影ID

        Returns:
            电影详细信息字典
        """
        try:
            url = f"{self.api_url}/movie/{movie_id}"
            params = {
                'api_key': self.api_key,
                'language': 'zh-CN',
                'append_to_response': 'credits,release_dates'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"获取电影详情失败 {movie_id}: {e}")
            return None

    def download_poster(self, poster_path, movie_title, size='medium'):
        """
        下载电影海报

        Args:
            poster_path: TMDB海报路径
            movie_title: 电影标题
            size: 海报尺寸

        Returns:
            本地文件路径或None
        """
        if not poster_path:
            return None

        try:
            # 获取指定尺寸的海报URL
            size_code = self.poster_sizes.get(size, self.poster_sizes['medium'])
            poster_url = f"{self.image_url}/{size_code}{poster_path}"

            # 创建安全的文件名
            safe_title = movie_title.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
            filename = f"{safe_title}_{size}.jpg"
            filepath = os.path.join(settings.POSTER_STORAGE_PATH, filename)

            # 如果文件已存在，直接返回路径
            if os.path.exists(filepath):
                return filepath

            # 下载海报
            response = requests.get(poster_url, timeout=15, stream=True)
            response.raise_for_status()

            # 保存海报到静态文件目录
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"成功下载海报: {filename}")
            return filepath

        except Exception as e:
            print(f"下载海报失败 {movie_title}: {e}")
            return None

    def get_or_download_poster(self, film):
        """
        获取或下载电影海报

        Args:
            film: Film对象

        Returns:
            海报URL路径
        """
        # 检查是否已有海报文件
        safe_title = film.title.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
        poster_filename = f"{safe_title}_medium.jpg"
        poster_path = os.path.join(settings.POSTER_STORAGE_PATH, poster_filename)

        if os.path.exists(poster_path):
            return f"/static/posters/{poster_filename}"

        # 如果没有，尝试从TMDB获取
        print(f"正在为电影 {film.title} 从TMDB获取海报...")

        # 搜索电影
        movie_data = self.search_movie(film.title, film.release_date.year if film.release_date else None)

        if movie_data and movie_data.get('poster_path'):
            # 下载海报
            local_path = self.download_poster(
                movie_data['poster_path'],
                film.title,
                'medium'
            )

            if local_path:
                return f"/static/posters/{poster_filename}"

        # 如果获取失败，返回默认海报
        return "https://via.placeholder.com/300x450?text=No+Poster"