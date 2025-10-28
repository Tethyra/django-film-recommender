#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为电影模型添加海报相关字段的数据库迁移脚本
"""

import os
import sys
import django
from django.db import migrations, models


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


def create_migration():
    """创建数据库迁移"""
    from django.core.management import call_command
    from django.conf import settings

    print("=" * 60)
    print("创建电影模型字段迁移")
    print("=" * 60)

    try:
        # 生成迁移文件
        print("📝 生成迁移文件...")
        call_command('makemigrations', 'main', '--name', 'add_poster_and_tmdb_fields')

        # 应用迁移
        print("\n🔄 应用数据库迁移...")
        call_command('migrate', 'main')

        print(f"\n✅ 数据库迁移完成！")
        print("📋 已添加的字段：")
        print("   - poster_path: 海报路径")
        print("   - tmdb_id: TMDB电影ID")
        print("   - tmdb_rating: TMDB评分")

    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

        # 尝试手动创建字段（如果自动迁移失败）
        print("\n🔧 尝试手动创建字段...")
        manual_migrate()


def manual_migrate():
    """手动执行SQL迁移"""
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            # 检查字段是否已存在
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'main_film' AND COLUMN_NAME = 'poster_path'
            """)
            poster_path_exists = cursor.fetchone() is not None

            if not poster_path_exists:
                # 添加poster_path字段
                cursor.execute("""
                    ALTER TABLE main_film 
                    ADD COLUMN poster_path VARCHAR(255) NULL AFTER description
                """)
                print("   ✅ 已添加 poster_path 字段")

            # 检查tmdb_id字段
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'main_film' AND COLUMN_NAME = 'tmdb_id'
            """)
            tmdb_id_exists = cursor.fetchone() is not None

            if not tmdb_id_exists:
                # 添加tmdb_id字段
                cursor.execute("""
                    ALTER TABLE main_film 
                    ADD COLUMN tmdb_id INT NULL AFTER rating_count
                """)
                print("   ✅ 已添加 tmdb_id 字段")

            # 检查tmdb_rating字段
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'main_film' AND COLUMN_NAME = 'tmdb_rating'
            """)
            tmdb_rating_exists = cursor.fetchone() is not None

            if not tmdb_rating_exists:
                # 添加tmdb_rating字段
                cursor.execute("""
                    ALTER TABLE main_film 
                    ADD COLUMN tmdb_rating FLOAT NULL AFTER tmdb_id
                """)
                print("   ✅ 已添加 tmdb_rating 字段")

        print("\n✅ 手动迁移完成！")

    except Exception as e:
        print(f"❌ 手动迁移失败: {e}")
        import traceback
        traceback.print_exc()


def verify_migration():
    """验证迁移是否成功"""
    from main.models import Film

    print("\n" + "=" * 60)
    print("验证迁移结果")
    print("=" * 60)

    try:
        # 检查模型字段
        fields = [f.name for f in Film._meta.get_fields()]
        required_fields = ['poster_path', 'tmdb_id', 'tmdb_rating']

        all_exists = True
        for field in required_fields:
            if field in fields:
                print(f"✅ {field} 字段存在")
            else:
                print(f"❌ {field} 字段不存在")
                all_exists = False

        if all_exists:
            print("\n🎉 数据库迁移验证成功！")
            return True
        else:
            print("\n⚠️ 数据库迁移验证失败！")
            return False

    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
        return False


def main():
    """主函数"""
    if not setup_django_env():
        print("❌ 无法运行迁移脚本")
        return

    try:
        create_migration()
        verify_migration()

        print("\n" + "=" * 60)
        print("下一步操作建议：")
        print("1. 运行 python update_posters_from_tmdb.py 更新海报")
        print("2. 运行 python sync_static_to_g_drive.py 同步到G盘")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()