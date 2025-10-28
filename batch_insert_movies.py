#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从TMDB批量获取电影数据并插入到数据库
确保数据不重复 - 修复SSL连接问题版本
"""

import os
import sys
import django
import requests
import time
import ssl
from django.utils import timezone
from datetime import datetime

# 解决SSL问题的配置
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def setup_django_env():
    """设置Django环境"""
    try:
        project_root = os.path.abspath(os.path.dirname(__file__))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_recommender.settings")

        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        django.setup()
        print("✅ Django环境设置成功")
        return True

    except Exception as e:
        print(f"❌ Django环境设置失败: {e}")
        return False


def get_tmdb_api_key():
    """获取TMDB API密钥"""
    # 让用户输入API密钥
    print("\n" + "=" * 60)
    print("需要TMDB API密钥")
    print("=" * 60)
    print("请按照以下步骤获取：")
    print("1. 访问 https://www.themoviedb.org/")
    print("2. 注册账号并登录")
    print("3. 访问 https://www.themoviedb.org/settings/api")
    print("4. 申请API密钥（API Key (v3 auth)）")
    print("=" * 60)

    while True:
        api_key = input("请输入您的TMDB API密钥: ").strip()
        if api_key:
            return api_key
        print("❌ API密钥不能为空，请重新输入")


def create_ssl_context():
    """创建SSL上下文"""
    try:
        context = ssl.create_default_context()
        # 降低SSL安全级别以解决某些连接问题
        context.options &= ~ssl.OP_NO_TLSv1_2
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        return context
    except:
        return None


class TMDBClient:
    """TMDB API客户端"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()

        # 配置会话以提高连接稳定性
        self.session.mount('https://', requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        ))

        # 配置超时
        self.timeout = 15

        # SSL上下文
        self.ssl_context = create_ssl_context()

    def make_request(self, url, params=None, retries=3):
        """发送请求并处理重试"""
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                    verify=False  # 临时禁用SSL验证以解决连接问题
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print("❌ API密钥无效或过期")
                    return None
                elif response.status_code == 429:
                    print(f"⚠️ 请求频率过高，正在重试... (第{attempt + 1}次)")
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    print(f"❌ 请求失败: HTTP {response.status_code}")
                    return None

            except requests.exceptions.SSLError as e:
                print(f"⚠️ SSL连接错误 (第{attempt + 1}次): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    # 最后尝试使用HTTP（如果支持）
                    print("🔄 尝试使用HTTP连接...")
                    http_url = url.replace('https://', 'http://')
                    try:
                        response = self.session.get(
                            http_url,
                            params=params,
                            timeout=self.timeout
                        )
                        if response.status_code == 200:
                            return response.json()
                    except Exception as e2:
                        print(f"❌ HTTP连接也失败: {e2}")

            except requests.exceptions.RequestException as e:
                print(f"⚠️ 请求异常 (第{attempt + 1}次): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue

        print("❌ 多次尝试后仍无法连接到TMDB API")
        return None

    def get_popular_movies(self, page=1, language='zh-CN'):
        """获取热门电影列表"""
        try:
            url = f"{self.base_url}/movie/popular"
            params = {
                'api_key': self.api_key,
                'language': language,
                'page': page
            }

            return self.make_request(url, params)

        except Exception as e:
            print(f"❌ 获取热门电影失败: {e}")
            return None

    def get_movie_details(self, movie_id, language='zh-CN'):
        """获取电影详细信息"""
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                'api_key': self.api_key,
                'language': language,
                'append_to_response': 'credits'
            }

            return self.make_request(url, params)

        except Exception as e:
            print(f"❌ 获取电影详情失败 {movie_id}: {e}")
            return None


def cleanup_duplicate_categories():
    """清理重复的分类"""
    from main.models import Category

    print("🔍 检查并清理重复分类...")

    # 获取所有分类名称和对应的ID
    categories = Category.objects.all()
    name_map = {}

    for cat in categories:
        name = cat.name.strip()
        if name not in name_map:
            name_map[name] = []
        name_map[name].append(cat.id)

    # 处理重复的分类
    duplicates_found = False
    for name, ids in name_map.items():
        if len(ids) > 1:
            duplicates_found = True
            print(f"   ⚠️  发现重复分类 '{name}': {len(ids)}个实例")

            # 保留第一个，删除其余的
            keep_id = ids[0]
            delete_ids = ids[1:]

            print(f"   📌 保留分类ID: {keep_id}")
            print(f"   🗑️ 删除分类ID: {delete_ids}")

            # 删除重复的分类
            Category.objects.filter(id__in=delete_ids).delete()

            # 更新电影-分类关联
            try:
                from main.models import Film_categories
                Film_categories.objects.filter(category_id__in=delete_ids).update(category_id=keep_id)
                print(f"   ✅ 已更新关联关系")
            except Exception as e:
                print(f"   ⚠️ 更新关联关系时出错: {e}")

    if not duplicates_found:
        print("   ✅ 未发现重复分类")

    return not duplicates_found


def get_or_create_category(category_name):
    """获取或创建分类（修复重复问题）"""
    from main.models import Category

    # 清理分类名称
    category_name = category_name.strip()
    if not category_name:
        return None

    try:
        # 先尝试获取分类
        # 使用filter().first()避免MultipleObjectsReturned异常
        category = Category.objects.filter(name=category_name).first()

        if category:
            return category

        # 如果不存在，创建新分类
        category = Category.objects.create(
            name=category_name,
            description=f'{category_name}类影视作品',
            created_at=timezone.now()
        )

        print(f"   📁 创建新分类: {category_name}")
        return category

    except Exception as e:
        print(f"   ⚠️  处理分类 '{category_name}' 时出错: {e}")

        # 如果遇到重复问题，再次尝试获取第一个
        category = Category.objects.filter(name=category_name).first()
        if category:
            print(f"   📌 使用现有分类: {category_name}")
            return category

        return None


def insert_movie_data(movie_data):
    """插入电影数据到数据库"""
    from main.models import Film

    # 检查电影是否已存在（根据标题和上映年份）
    title = movie_data.get('title', '')
    release_date = movie_data.get('release_date', '')

    if not title:
        print("   ❌ 电影标题为空，跳过")
        return None

    # 提取年份
    year = None
    if release_date:
        try:
            year = datetime.strptime(release_date, '%Y-%m-%d').year
        except:
            pass

    # 检查重复（使用标题和年份的组合）
    existing_film = Film.objects.filter(title=title)
    if year:
        existing_film = existing_film.filter(release_date__year=year)

    if existing_film.exists():
        print(f"   ⏩ 电影已存在: {title} ({year if year else '未知年份'})")
        return existing_film.first()

    # 准备电影数据
    film_data = {
        'title': title,
        'director': '',
        'actors': '',
        'release_date': release_date if release_date else None,
        'description': movie_data.get('overview', '')[:500],  # 限制描述长度
        'rating': movie_data.get('vote_average', 0),
        'rating_count': movie_data.get('vote_count', 0),
        'tmdb_id': movie_data.get('id'),
        'tmdb_rating': movie_data.get('vote_average'),
        'created_at': timezone.now(),
        'updated_at': timezone.now()
    }

    # 处理导演和演员
    credits = movie_data.get('credits', {})

    # 获取导演
    directors = [crew['name'] for crew in credits.get('crew', []) if crew['job'] == 'Director']
    if directors:
        film_data['director'] = ', '.join(directors[:3])  # 最多显示3个导演

    # 获取演员
    actors = [cast['name'] for cast in credits.get('cast', [])[:5]]  # 最多显示5个演员
    if actors:
        film_data['actors'] = ', '.join(actors)

    # 创建电影记录
    film = Film.objects.create(**film_data)
    print(f"   ✅ 插入新电影: {title} ({year if year else '未知年份'})")

    # 处理分类
    genres = movie_data.get('genres', [])
    for genre in genres:
        category = get_or_create_category(genre['name'])
        if category:
            film.categories.add(category)

    return film


def batch_insert_movies(target_count=200):
    """批量插入电影数据"""
    print("=" * 60)
    print(f"开始批量插入电影数据 (目标: {target_count}部)")
    print("=" * 60)

    try:
        # 清理重复分类
        cleanup_duplicate_categories()

        # 获取TMDB API密钥
        api_key = get_tmdb_api_key()
        if not api_key:
            print("❌ 没有TMDB API密钥，无法继续")
            return 0

        # 初始化TMDB客户端
        tmdb_client = TMDBClient(api_key)

        # 从TMDB获取电影数据
        page = 1
        inserted_count = 0
        processed_movies = set()
        max_pages = 30  # 最多获取30页

        while inserted_count < target_count and page <= max_pages:
            print(f"\n📄 获取第 {page} 页电影数据...")

            # 获取热门电影列表
            popular_movies = tmdb_client.get_popular_movies(page=page)

            if not popular_movies or not popular_movies.get('results'):
                print(f"❌ 无法获取第 {page} 页数据，停止获取")
                break

            # 处理每部电影
            for movie in popular_movies['results']:
                movie_id = movie.get('id')

                if movie_id in processed_movies:
                    continue

                processed_movies.add(movie_id)

                # 获取电影详细信息
                movie_details = tmdb_client.get_movie_details(movie_id)

                if movie_details:
                    try:
                        # 插入电影数据
                        film = insert_movie_data(movie_details)
                        if film:
                            inserted_count += 1

                            # 检查是否达到目标数量
                            if inserted_count >= target_count:
                                break
                    except Exception as e:
                        print(f"   ⚠️  插入电影时出错: {e}")
                        continue

            page += 1

            # 避免请求过于频繁
            time.sleep(1)

        # 统计结果
        print(f"\n" + "=" * 60)
        print(f"批量插入完成")
        print("=" * 60)
        print(f"目标数量: {target_count}部")
        print(f"成功插入: {inserted_count}部")
        print(f"处理页数: {page - 1}页")
        print(f"处理电影ID: {len(processed_movies)}个")
        print("=" * 60)

        # 显示数据库统计
        from main.models import Film, Category
        total_films = Film.objects.count()
        total_categories = Category.objects.count()

        print(f"\n📊 数据库统计:")
        print(f"   总电影数量: {total_films}部")
        print(f"   总分类数量: {total_categories}个")
        print(f"   新增电影数量: {inserted_count}部")

        return inserted_count

    except Exception as e:
        print(f"\n❌ 批量插入失败: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """主函数"""
    if not setup_django_env():
        print("❌ 无法运行批量插入脚本")
        return

    try:
        # 批量插入200部电影
        inserted_count = batch_insert_movies(target_count=200)

        print(f"\n🎉 批量插入脚本运行完成！")
        print(f"📈 成功插入 {inserted_count} 部电影数据")

        # 提示后续操作
        print("\n" + "=" * 60)
        print("后续操作建议")
        print("=" * 60)
        print("1. 更新电影海报: python update_posters_from_tmdb.py")
        print("2. 同步静态文件: python sync_static_to_g_drive.py")
        print("3. 启动服务器验证: python manage.py runserver")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()