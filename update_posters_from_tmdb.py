#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从TMDB批量更新电影海报脚本
"""

import os
import sys


def setup_django_env():
    """设置Django环境"""
    try:
        project_root = os.path.abspath(os.path.dirname(__file__))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_recommender.settings")

        # 将项目根目录添加到Python路径
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        import django
        django.setup()
        print("✅ Django环境设置成功")
        return True

    except Exception as e:
        print(f"❌ Django环境设置失败: {e}")
        return False


def update_all_posters():
    """更新所有电影的海报"""
    from main.models import Film
    from main.tmdb_api import TMDBApi
    from django.conf import settings

    print("=" * 60)
    print("从TMDB批量更新电影海报")
    print("=" * 60)

    # 获取所有电影
    films = Film.objects.all()
    total_films = films.count()

    if total_films == 0:
        print("❌ 没有找到电影数据")
        return

    print(f"✅ 找到 {total_films} 部电影")

    tmdb_api = TMDBApi()

    success_count = 0
    failed_count = 0

    for i, film in enumerate(films):
        print(f"\n处理电影 {i + 1}/{total_films}: {film.title}")

        try:
            # 获取或下载海报
            poster_url = tmdb_api.get_or_download_poster(film)

            if poster_url and not poster_url.startswith("https://via.placeholder.com"):
                # 更新电影的海报路径
                film.poster_path = poster_url
                film.save()
                success_count += 1
                print(f"  ✅ 海报更新成功: {os.path.basename(poster_url)}")
            else:
                failed_count += 1
                print(f"  ❌ 海报获取失败")

        except Exception as e:
            failed_count += 1
            print(f"  ❌ 处理失败: {e}")

    # 显示统计结果
    print(f"\n" + "=" * 60)
    print("更新完成统计")
    print("=" * 60)
    print(f"总计电影: {total_films}")
    print(f"成功更新: {success_count}")
    print(f"更新失败: {failed_count}")
    print("=" * 60)

    # 显示存储位置信息
    print(f"\n📁 海报存储位置: {os.path.abspath(settings.POSTER_STORAGE_PATH)}")
    print(f"🌐 海报访问URL: http://localhost:8000/static/posters/")


def main():
    """主函数"""
    if not setup_django_env():
        print("❌ 无法运行海报更新脚本")
        return

    try:
        update_all_posters()
        print("\n🎉 海报批量更新脚本运行完成！")

        # 提示同步到G盘
        print("\n💡 建议运行: python sync_static_to_g_drive.py 同步到G盘")

    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()