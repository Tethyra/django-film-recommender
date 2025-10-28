#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步静态文件到G盘指定路径
"""

import os
import shutil
import sys


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


def sync_static_files():
    """同步静态文件到G盘"""
    from django.conf import settings

    print("=" * 60)
    print("同步静态文件到G盘")
    print("=" * 60)

    # 源目录和目标目录
    source_dir = settings.STATIC_ROOT
    target_dir = "G:\\film_project\\static"

    print(f"📁 源目录: {source_dir}")
    print(f"📁 目标目录: {target_dir}")

    if not os.path.exists(source_dir):
        print(f"❌ 源目录不存在: {source_dir}")
        return

    try:
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)

        # 同步海报目录
        posters_source = os.path.join(source_dir, 'posters')
        posters_target = os.path.join(target_dir, 'posters')

        if os.path.exists(posters_source):
            # 复制海报文件
            for filename in os.listdir(posters_source):
                source_file = os.path.join(posters_source, filename)
                target_file = os.path.join(posters_target, filename)

                # 如果文件不存在或已更新，复制
                if not os.path.exists(target_file) or os.path.getmtime(source_file) > os.path.getmtime(target_file):
                    os.makedirs(posters_target, exist_ok=True)
                    shutil.copy2(source_file, target_file)
                    print(f"📤 复制文件: {filename}")
                else:
                    print(f"⏩ 文件已最新: {filename}")

        print(f"\n✅ 静态文件同步完成！")
        print(f"🌐 访问路径: http://localhost:8000/static/posters/")

    except Exception as e:
        print(f"❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    if not setup_django_env():
        print("❌ 无法运行同步脚本")
        return

    try:
        sync_static_files()
        print("\n🎉 静态文件同步脚本运行完成！")
    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()