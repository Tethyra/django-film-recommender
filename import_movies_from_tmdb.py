#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从TMDB导入热门电影数据脚本
"""

import os
import sys

from django.contrib.sites import requests


def setup_django_env():
    """设置Django环境"""
    try:
        project_root = os.path.abspath(os.path.dirname(__file__))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_recommender.settings")

        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        import django
        django.setup()
        return True

    except Exception as e:
        print(f"❌ Django环境设置失败: {e}")
        return False


def import_popular_movies():
    """从TMDB导入热门电影"""
    from main.models import Film, Category
    from main.tmdb_api import TMDBApi
    from django.conf import settings
    import datetime

    print("=" * 60)
    print("从TMDB导入热门电影数据")
    print("=" * 60)

    tmdb_api = TMDBApi()

    if not tmdb_api.api_key:
        print("❌ TMDB API密钥未设置，请在settings.py中配置TMDB_API_KEY")
        return

    try:
        # 获取热门电影列表
        url = f"{settings.TMDB_API_URL}/movie/popular"
        params = {
            'api_key': tmdb_api.api_key,
            'language': 'zh-CN',
            'page': 1
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('results'):
            print("❌ 没有获取到电影数据")
            return

        print(f"✅ 从TMDB获取到 {len(data['results'])} 部热门电影")

        # 创建默认分类
        movie_category, _ = Category.objects.get_or_create(name='电影')
        popular_category, _ = Category.objects.get_or_create(name='热门')

        imported_count = 0

        for movie_data in data['results']:
            try:
                # 检查电影是否已存在
                existing_film = Film.objects.filter(
                    title=movie_data['title'],
                    release_date__year=movie_data.get('release_date', '').split('-')[0] if movie_data.get(
                        'release_date') else None
                ).first()

                if existing_film:
                    print(f"  ⏩ 电影 {movie_data['title']} 已存在，跳过")
                    continue

                # 创建电影记录
                release_date = None
                if movie_data.get('release_date'):
                    try:
                        release_date = datetime.datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
                    except:
                        pass

                film = Film.objects.create(
                    title=movie_data['title'],
                    director='',  # 将通过详细信息API获取
                    actors='',  # 将通过详细信息API获取
                    release_date=release_date,
                    description=movie_data.get('overview', ''),
                    rating=movie_data.get('vote_average', 0),
                    rating_count=movie_data.get('vote_count', 0),
                    tmdb_id=movie_data['id'],
                    tmdb_rating=movie_data.get('vote_average')
                )

                # 添加分类
                film.categories.add(movie_category, popular_category)

                # 下载海报
                if movie_data.get('poster_path'):
                    tmdb_api.download_poster(
                        movie_data['poster_path'],
                        film.title,
                        'medium'
                    )

                    # 更新海报路径
                    safe_title = film.title.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
                    film.poster_path = f"/static/posters/{safe_title}_medium.jpg"
                    film.save()

                imported_count += 1
                print(f"  ✅ 导入电影: {movie_data['title']}")

            except Exception as e:
                print(f"  ❌ 导入电影 {movie_data.get('title', '未知电影')} 失败: {e}")

        print(f"\n" + "=" * 60)
        print(f"导入完成！成功导入 {imported_count} 部电影")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    if not setup_django_env():
        print("❌ 无法运行数据导入脚本")
        return

    try:
        import_popular_movies()
        print("\n🎉 电影数据导入脚本运行完成！")
    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()