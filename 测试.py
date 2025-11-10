#!/usr/bin/env python3
"""
终极简化修复脚本
专门解决 static/posters/ 路径问题
"""

import os
import shutil
import sys


def main():
    """主函数"""
    print("=" * 70)
    print("终极简化修复脚本 - 解决图片显示问题")
    print("=" * 70)
    print()

    try:
        # 检查是否在项目根目录
        if not os.path.exists('manage.py'):
            print("✗ 错误: 请在项目根目录下运行此脚本")
            print("  项目根目录应包含 manage.py 文件")
            return 1

        # 步骤1: 修复urls.py
        print("步骤1/3: 修复URL配置...")
        urls_path = 'film_recommender/urls.py'

        if os.path.exists(urls_path):
            # 备份文件
            shutil.copy2(urls_path, urls_path + '.bak')

            with open(urls_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已有媒体文件配置
            if 'static(settings.MEDIA_URL' not in content:
                # 添加媒体文件配置
                new_content = content + '''
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("  ✓ 已添加媒体文件URL路由")
            else:
                print("  ✓ 媒体文件URL路由已存在")
        else:
            print("  ✗ 未找到 urls.py 文件")

        # 步骤2: 修复模板文件
        print("\n步骤2/3: 修复模板文件...")
        template_dir = 'templates'

        if os.path.exists(template_dir):
            # 创建备份目录
            backup_dir = 'template_backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            fixed_files = 0
            total_files = 0

            # 递归查找所有HTML文件
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith(('.html', '.htm')):
                        total_files += 1
                        file_path = os.path.join(root, file)

                        # 备份文件
                        rel_path = os.path.relpath(file_path, template_dir)
                        backup_path = os.path.join(backup_dir, rel_path)
                        backup_dir_path = os.path.dirname(backup_path)
                        if not os.path.exists(backup_dir_path):
                            os.makedirs(backup_dir_path)
                        shutil.copy2(file_path, backup_path)

                        # 替换内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if 'static/posters/' in content:
                            new_content = content.replace('static/posters/', 'media/posters/')
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            fixed_files += 1
                            print(f"  ✓ 修复: {rel_path}")

            print(f"  ✓ 处理了 {total_files} 个模板文件，修复了 {fixed_files} 个")
        else:
            print("  ✗ 未找到模板目录")

        # 步骤3: 移动图片文件
        print("\n步骤3/3: 迁移图片文件...")
        static_posters = 'static/posters'
        media_posters = 'media/posters'

        if os.path.exists(static_posters):
            # 创建目标目录
            if not os.path.exists(media_posters):
                os.makedirs(media_posters)

            # 移动文件
            import os as os_module
            moved_files = 0

            for filename in os.listdir(static_posters):
                src = os.path.join(static_posters, filename)
                dst = os.path.join(media_posters, filename)

                if os.path.isfile(src) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    if not os.path.exists(dst):
                        shutil.move(src, dst)
                        moved_files += 1

            print(f"  ✓ 从 static/posters 移动了 {moved_files} 个图片文件到 media/posters")

            # 删除空目录
            if not os.listdir(static_posters):
                os.rmdir(static_posters)
                print(f"  ✓ 删除了空目录 static/posters")
        else:
            print("  ✓ static/posters 目录不存在，跳过文件迁移")

        print("\n" + "=" * 70)
        print("🎉 修复完成！")
        print("\n请执行以下命令:")
        print("1. 重启Django服务器: python manage.py runserver")
        print("2. 访问网站: http://127.0.0.1:8000/")
        print("3. 检查电影海报是否正常显示")
        print("\n如果仍然有问题，请运行 verify_fix.py 检查问题")

        return 0

    except Exception as e:
        print(f"\n✗ 脚本执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())