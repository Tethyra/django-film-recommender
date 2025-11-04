#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL配置语法错误快速修复脚本
专门解决urls.py中的\n字符导致的语法错误
"""

import os
import sys
import shutil


def fix_urls_file_directly(urls_path):
    """直接修复urls.py文件"""
    print("正在修复urls.py文件...")

    if not os.path.exists(urls_path):
        print(f"❌ 文件不存在: {urls_path}")
        return False

    # 备份文件
    backup_path = urls_path + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        shutil.copy2(urls_path, backup_path)
        print(f"✅ 已备份文件到: {backup_path}")
    except Exception as e:
        print(f"⚠️  备份文件失败: {e}")

    try:
        # 读取文件内容
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print("原始内容片段（问题区域）:")
        lines = content.split('\n')
        # 显示第20-25行
        for i in range(max(0, 19), min(len(lines), 25)):
            print(f"{i + 1}: {repr(lines[i])}")

        # 修复问题：移除所有的\n字符
        # 问题是在代码中直接使用了\n，而不是实际的换行
        content = content.replace('\\n', '\n')

        # 同时修复可能的反斜杠问题
        content = content.replace('urlpatterns = [\\', 'urlpatterns = [')
        content = content.replace('path(', '\n    path(')

        # 保存修复后的内容
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("\n修复后的内容片段（问题区域）:")
        new_lines = content.split('\n')
        for i in range(max(0, 19), min(len(new_lines), 25)):
            print(f"{i + 1}: {repr(new_lines[i])}")

        print(f"\n✅ urls.py文件修复完成！")
        return True

    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("URL配置语法错误快速修复工具")
    print("专门解决\\n字符导致的SyntaxError")
    print("=" * 60)

    # 导入datetime模块
    import datetime

    # 让用户输入urls.py文件路径
    print("\n请输入urls.py文件的完整路径:")
    print("例如: G:\\film_project\\film_recommender\\urls.py")
    urls_path = input("路径: ").strip()

    # 验证路径
    if not os.path.exists(urls_path):
        print(f"❌ 文件不存在: {urls_path}")
        # 尝试自动查找
        print("\n正在尝试自动查找...")
        # 检查常见位置
        common_paths = [
            "G:\\film_project\\film_recommender\\urls.py",
            "./film_recommender/urls.py",
            "../film_recommender/urls.py"
        ]

        found_path = None
        for path in common_paths:
            if os.path.exists(path):
                found_path = path
                break

        if found_path:
            print(f"✅ 找到文件: {found_path}")
            urls_path = found_path
        else:
            print("❌ 无法找到urls.py文件")
            sys.exit(1)

    # 执行修复
    if fix_urls_file_directly(urls_path):
        print("\n" + "=" * 60)
        print("🎉 修复完成！")
        print("\n请重新启动Django服务器:")
        print("   python manage.py runserver localhost:8000")
        print("\n如果问题仍然存在，请检查:")
        print("1. 是否还有其他\\n字符在代码中")
        print("2. 检查Python语法是否正确")
        print("3. 确保所有括号都正确闭合")
    else:
        print("\n❌ 修复失败，请手动检查文件")


if __name__ == "__main__":
    main()