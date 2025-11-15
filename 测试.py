#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FilmInsight 项目一键修复和替换工具
用于自动修复和更新电影推荐系统的HTML模板文件
"""

import os
import sys
import shutil
import argparse
import json
from datetime import datetime
from pathlib import Path


class FilmInsightFixer:
    def __init__(self):
        self.backup_dir = None
        self.project_dir = None
        self.template_dir = None
        self.success_files = []
        self.failed_files = []
        self.skipped_files = []

        # 定义需要替换的文件映射
        self.file_mapping = {
            'templates/main/history.html': 'history_fixed.html',
            'templates/main/category.html': 'category_fixed.html',
            'templates/main/search_results.html': 'search_results_fixed.html',
            'templates/main/index.html': 'index_enhanced.html',
        }

        # 定义需要添加的新文件
        self.new_files = {
            'templates/main/recommendations.html': 'recommendations.html',
            'templates/main/stats_analysis.html': 'stats_analysis.html',
            'templates/main/movie_calendar.html': 'movie_calendar.html',
            'templates/main/rating_analysis.html': 'rating_analysis.html',
            'templates/main/social_share.html': 'social_share.html',
            'templates/main/admin_dashboard.html': 'admin_dashboard.html',
        }

    def print_banner(self):
        """显示工具横幅"""
        print("=" * 60)
        print("FilmInsight 项目一键修复和替换工具")
        print("=" * 60)
        print("本工具将自动修复和更新电影推荐系统的HTML模板文件")
        print("注意：请在运行前备份您的项目数据！")
        print("=" * 60)

    def get_project_path(self):
        """获取项目路径"""
        while True:
            path = input("\n请输入您的Django项目根目录路径: ").strip()
            if os.path.isdir(path):
                # 验证是否是Django项目
                if os.path.isfile(os.path.join(path, 'manage.py')):
                    self.project_dir = os.path.abspath(path)
                    self.template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
                    print(f"✓ 项目路径验证成功: {self.project_dir}")
                    return True
                else:
                    print("✗ 错误：指定的目录不是Django项目（缺少manage.py）")
            else:
                print("✗ 错误：指定的路径不存在")

            retry = input("是否重新输入？(y/n): ").lower()
            if retry != 'y':
                return False

    def create_backup(self):
        """创建备份"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.backup_dir = os.path.join(self.project_dir, f'backup_{timestamp}')
            os.makedirs(self.backup_dir)

            # 备份模板目录
            templates_src = os.path.join(self.project_dir, 'templates')
            templates_dst = os.path.join(self.backup_dir, 'templates')
            shutil.copytree(templates_src, templates_dst)

            print(f"✓ 备份创建成功: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"✗ 备份创建失败: {str(e)}")
            return False

    def validate_template_files(self):
        """验证模板文件是否存在"""
        print("\n正在验证模板文件...")
        template_path = os.path.dirname(os.path.abspath(__file__))

        missing_files = []
        for dest_path, src_filename in list(self.file_mapping.items()) + list(self.new_files.items()):
            src_path = os.path.join(template_path, src_filename)
            if not os.path.isfile(src_path):
                missing_files.append(src_filename)

        if missing_files:
            print(f"✗ 错误：缺少必要的模板文件: {', '.join(missing_files)}")
            print("请确保所有修复文件与本脚本在同一目录下")
            return False

        print("✓ 所有模板文件验证通过")
        return True

    def replace_existing_files(self):
        """替换现有文件"""
        print("\n正在替换现有文件...")

        for dest_rel_path, src_filename in self.file_mapping.items():
            dest_path = os.path.join(self.project_dir, dest_rel_path)
            src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), src_filename)

            try:
                if os.path.isfile(dest_path):
                    # 替换文件
                    shutil.copy2(src_path, dest_path)
                    self.success_files.append(dest_rel_path)
                    print(f"✓ 替换成功: {dest_rel_path}")
                else:
                    self.skipped_files.append(dest_rel_path)
                    print(f"△ 跳过: {dest_rel_path} (文件不存在)")
            except Exception as e:
                self.failed_files.append((dest_rel_path, str(e)))
                print(f"✗ 替换失败: {dest_rel_path} - {str(e)}")

    def add_new_files(self):
        """添加新文件"""
        print("\n正在添加新文件...")

        for dest_rel_path, src_filename in self.new_files.items():
            dest_path = os.path.join(self.project_dir, dest_rel_path)
            src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), src_filename)

            try:
                # 创建目录（如果不存在）
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                if os.path.isfile(dest_path):
                    # 文件已存在，询问是否覆盖
                    overwrite = input(f"文件 {dest_rel_path} 已存在，是否覆盖？(y/n): ").lower()
                    if overwrite == 'y':
                        shutil.copy2(src_path, dest_path)
                        self.success_files.append(dest_rel_path)
                        print(f"✓ 覆盖成功: {dest_rel_path}")
                    else:
                        self.skipped_files.append(dest_rel_path)
                        print(f"△ 跳过: {dest_rel_path} (用户选择不覆盖)")
                else:
                    # 新文件
                    shutil.copy2(src_path, dest_path)
                    self.success_files.append(dest_rel_path)
                    print(f"✓ 添加成功: {dest_rel_path}")
            except Exception as e:
                self.failed_files.append((dest_rel_path, str(e)))
                print(f"✗ 添加失败: {dest_rel_path} - {str(e)}")

    def update_urls(self):
        """更新URL配置"""
        print("\n正在更新URL配置...")

        urls_path = os.path.join(self.project_dir, 'filminsight', 'urls.py')
        if not os.path.isfile(urls_path):
            print("△ 跳过URL更新: urls.py文件不存在")
            return

        # 读取当前urls.py
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 定义需要添加的URL模式
        new_urls = [
            'path(\'recommendations/\', views.recommendations, name=\'recommendations\'),',
            'path(\'stats-analysis/\', views.stats_analysis, name=\'stats_analysis\'),',
            'path(\'movie-calendar/\', views.movie_calendar, name=\'movie_calendar\'),',
            'path(\'rating-analysis/\', views.rating_analysis, name=\'rating_analysis\'),',
            'path(\'social-share/\', views.social_share, name=\'social_share\'),',
            'path(\'admin-dashboard/\', views.admin_dashboard, name=\'admin_dashboard\'),',
        ]

        # 检查URL是否已存在
        urls_added = False
        for url_pattern in new_urls:
            if url_pattern not in content:
                # 在合适的位置添加URL
                if 'urlpatterns = [' in content:
                    content = content.replace('urlpatterns = [', f'urlpatterns = [\n    {url_pattern}')
                    urls_added = True
                    print(f"✓ 添加URL: {url_pattern.strip()}")

        if urls_added:
            # 保存更新后的文件
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✓ URL配置更新成功")
        else:
            print("△ URL配置无需更新（已存在）")

    def run_migrations(self):
        """运行数据库迁移"""
        print("\n正在运行数据库迁移...")

        manage_path = os.path.join(self.project_dir, 'manage.py')
        if not os.path.isfile(manage_path):
            print("△ 跳过迁移: manage.py文件不存在")
            return

        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, manage_path, 'migrate'],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✓ 数据库迁移成功")
            else:
                print(f"△ 迁移警告: {result.stderr}")
        except Exception as e:
            print(f"✗ 迁移失败: {str(e)}")

    def show_summary(self):
        """显示操作总结"""
        print("\n" + "=" * 60)
        print("操作总结")
        print("=" * 60)

        print(f"\n成功处理的文件: {len(self.success_files)}")
        for file in self.success_files:
            print(f"  ✓ {file}")

        if self.skipped_files:
            print(f"\n跳过的文件: {len(self.skipped_files)}")
            for file in self.skipped_files:
                print(f"  △ {file}")

        if self.failed_files:
            print(f"\n失败的文件: {len(self.failed_files)}")
            for file, error in self.failed_files:
                print(f"  ✗ {file}: {error}")

        print(f"\n备份目录: {self.backup_dir}")
        print("\n重要提示:")
        print("1. 请检查项目是否正常运行")
        print("2. 如果出现问题，可以从备份目录恢复")
        print("3. 建议清理浏览器缓存后测试")
        print("4. 新功能需要相应的视图函数支持")

    def run(self):
        """运行工具"""
        self.print_banner()

        # 获取项目路径
        if not self.get_project_path():
            print("\n操作取消")
            return

        # 验证模板文件
        if not self.validate_template_files():
            return

        # 创建备份
        if not self.create_backup():
            confirm = input("备份创建失败，是否继续？(y/n): ").lower()
            if confirm != 'y':
                return

        # 执行替换和添加
        self.replace_existing_files()
        self.add_new_files()

        # 更新URL配置
        self.update_urls()

        # 运行迁移
        self.run_migrations()

        # 显示总结
        self.show_summary()

        print("\n" + "=" * 60)
        print("工具运行完成！")
        print("=" * 60)


if __name__ == "__main__":
    try:
        fixer = FilmInsightFixer()
        fixer.run()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print(f"\n✗ 工具运行出错: {str(e)}")
        import traceback

        traceback.print_exc()