#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复URL配置语法错误的脚本
解决Django项目启动时的SyntaxError问题
"""

import os
import sys
import shutil


def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")


def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")


def print_info(message):
    """打印信息"""
    print(f"ℹ️  {message}")


def backup_file(file_path, backup_suffix='.backup'):
    """备份文件"""
    try:
        if os.path.exists(file_path):
            backup_path = file_path + backup_suffix
            shutil.copy2(file_path, backup_path)
            print_info(f"已备份文件: {file_path} -> {backup_path}")
            return True
    except Exception as e:
        print_error(f"备份文件失败: {file_path}, 错误: {e}")
    return False


def fix_urls_file(project_root):
    """修复urls.py文件"""
    print_info("正在修复urls.py文件...")

    urls_path = os.path.join(project_root, 'film_recommender', 'urls.py')

    if not os.path.exists(urls_path):
        print_error(f"文件不存在: {urls_path}")
        return False

    if not backup_file(urls_path):
        return False

    try:
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print_info("原始文件内容:")
        print(content)
        print("-" * 50)

        # 修复语法错误
        # 问题：urlpatterns = [\n    path('charts/', include('charts.urls')),\n
        # 修复：移除反斜杠，正确格式化

        # 方法1：使用字符串替换修复
        content = content.replace('urlpatterns = [\\n', 'urlpatterns = [\n')
        content = content.replace('urlpatterns = [\n', 'urlpatterns = [\n    ')

        # 方法2：重新构建URL配置（更可靠）
        if 'path(\'charts/\', include(\'charts.urls\'))' in content:
            # 提取现有的URL配置
            lines = content.split('\n')
            new_lines = []
            in_urlpatterns = False
            urlpatterns_lines = []

            for line in lines:
                stripped_line = line.strip()

                if stripped_line.startswith('urlpatterns = ['):
                    in_urlpatterns = True
                    new_lines.append('urlpatterns = [')
                elif in_urlpatterns and stripped_line.endswith(']'):
                    in_urlpatterns = False
                    # 添加charts URL（如果不存在）
                    has_charts = any('charts' in url_line for url_line in urlpatterns_lines)
                    if not has_charts:
                        urlpatterns_lines.insert(0, "    path('charts/', include('charts.urls')),")
                    # 添加所有URL行
                    new_lines.extend(urlpatterns_lines)
                    new_lines.append(line)
                elif in_urlpatterns:
                    if stripped_line and not stripped_line.startswith('#'):
                        urlpatterns_lines.append(line)
                else:
                    new_lines.append(line)

            content = '\n'.join(new_lines)

        print_info("修复后的文件内容:")
        print(content)

        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print_success("urls.py文件修复完成")
        return True

    except Exception as e:
        print_error(f"修复urls.py文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_project_structure(project_root):
    """检查项目结构"""
    print_info("正在检查项目结构...")

    required_files = [
        os.path.join(project_root, 'manage.py'),
        os.path.join(project_root, 'film_recommender', 'settings.py'),
        os.path.join(project_root, 'film_recommender', 'urls.py'),
        os.path.join(project_root, 'main', 'models.py'),
    ]

    all_exists = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"✓ {file_path}")
        else:
            print_error(f"✗ {file_path}")
            all_exists = False

    return all_exists


def get_project_root():
    """获取项目根目录"""
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # 查找包含manage.py的目录
    for root, dirs, files in os.walk(current_dir):
        if 'manage.py' in files:
            return root

    # 如果找不到，提示用户指定
    print_error("无法自动检测项目根目录")
    project_dir = input("请输入项目根目录路径: ").strip()
    if os.path.exists(os.path.join(project_dir, 'manage.py')):
        return project_dir

    print_error("无效的项目目录")
    sys.exit(1)


def main():
    """主函数"""
    print("=" * 60)
    print("Django URL配置修复工具")
    print("修复urls.py文件中的语法错误")
    print("=" * 60)
    print()

    try:
        # 获取项目根目录
        project_root = get_project_root()
        print_info(f"项目根目录: {project_root}")

        # 检查项目结构
        if not check_project_structure(project_root):
            print_error("项目结构不完整")
            sys.exit(1)

        # 修复urls.py文件
        if fix_urls_file(project_root):
            print("\n" + "=" * 60)
            print_success("URL配置修复完成！")
            print("\n下一步操作:")
            print("1. 重新启动Django服务器:")
            print(f"   cd {project_root}")
            print("   python manage.py runserver")
            print("\n2. 如果问题仍然存在，请检查:")
            print("   - Python版本是否兼容")
            print("   - Django版本是否正确")
            print("   - 其他文件是否有语法错误")
            print("\n3. 查看详细错误信息:")
            print("   检查错误日志中的具体行号和错误描述")
        else:
            print_error("修复失败，请手动检查urls.py文件")

    except KeyboardInterrupt:
        print("\n⏹️ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 修复过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()