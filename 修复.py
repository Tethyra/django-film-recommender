#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复所有模板文件的图片显示问题
确保所有页面都使用正确的静态文件路径
"""

import os
import re
import shutil


def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.template_final_backup"
        shutil.copy2(file_path, backup_path)
        print(f"✓ 已备份: {os.path.basename(file_path)}")
        return True
    return False


def fix_template_file(file_path):
    """修复单个模板文件"""
    if not os.path.exists(file_path):
        print(f"✗ 错误: 找不到文件 - {file_path}")
        return False, 0

    # 备份文件
    backup_file(file_path)

    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes_made = 0

    # 定义所有需要替换的模式
    replacement_patterns = [
        # 模式1: 旧的film.poster.url格式
        (r'{{\s*film\.poster\.url\s*}}', '/static/posters/{{ film.title|slugify }}_medium.jpg'),

        # 模式2: 带if判断的完整块
        (
        r'{% if film\.poster %}\s*<img[^>]*src\s*=\s*"{{\s*film\.poster\.url\s*}}"[^>]*>\s*{% else %}\s*<img[^>]*src\s*=\s*"[^"]*"[^>]*>\s*{% endif %}',
        '<img src="/static/posters/{{ film.title|slugify }}_medium.jpg" alt="{{ film.title }}" class="card-img-top" height="200" onerror="this.onerror=null;this.src=\'https://via.placeholder.com/300x200?text=No+Poster\';">'),

        # 模式3: 带过滤器的格式
        (r'{{\s*film\.poster\.url\|', '/static/posters/{{ film.title|slugify }}_medium.jpg|'),

        # 模式4: 无空格格式
        (r'{{film\.poster\.url}}', '/static/posters/{{ film.title|slugify }}_medium.jpg'),

        # 模式5: 单引号格式
        (r"'{{\s*film\.poster\.url\s*}}'", "'/static/posters/{{ film.title|slugify }}_medium.jpg'"),

        # 模式6: 已经使用static但路径可能错误的格式
        (r'src\s*=\s*"{% static [\'"]([^\'"]*)[\'"] %}"',
         lambda m: f'src="/static/posters/{{ film.title|slugify }}_medium.jpg"' if 'poster' in m.group(1) else m.group(
             0)),

        # 模式7: poster_url方法格式
        (r'{{\s*film\.poster_url\s*}}', '/static/posters/{{ film.title|slugify }}_medium.jpg'),
    ]

    # 应用所有替换模式
    for pattern, replacement in replacement_patterns:
        if callable(replacement):
            # 处理函数类型的替换
            new_content = ''
            last_pos = 0
            for match in re.finditer(pattern, content, flags=re.DOTALL | re.IGNORECASE):
                new_content += content[last_pos:match.start()]
                new_content += replacement(match)
                last_pos = match.end()
                changes_made += 1
            new_content += content[last_pos:]
            content = new_content
        else:
            # 处理字符串类型的替换
            content, count = re.subn(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
            changes_made += count

    # 特别处理图片高度和样式
    # 确保所有海报图片都有一致的高度和错误处理
    img_pattern = r'<img\s+src\s*=\s*"/static/posters/{{ film.title\|slugify }}_medium\.jpg"[^>]*>'
    img_replacement = '<img src="/static/posters/{{ film.title|slugify }}_medium.jpg" alt="{{ film.title }}" class="card-img-top film-poster" height="200" style="object-fit: cover;" onerror="this.onerror=null;this.src=\'https://via.placeholder.com/300x200?text=No+Poster\';">'

    content, count = re.subn(img_pattern, img_replacement, content, flags=re.DOTALL | re.IGNORECASE)
    changes_made += count

    if changes_made > 0:
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes_made
    else:
        return False, 0


def find_all_template_files():
    """查找所有模板文件"""
    project_root = os.getcwd()
    templates_dir = os.path.join(project_root, 'templates')

    if not os.path.exists(templates_dir):
        print(f"✗ 错误: 找不到templates目录 - {templates_dir}")
        return []

    html_files = []
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))

    return html_files


def add_css_styles():
    """添加CSS样式以优化图片显示"""
    base_css = '''
/* 海报图片样式 */
.film-poster {
    object-fit: cover;
    width: 100%;
    height: 200px;
    border-radius: 4px 4px 0 0;
}

.film-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%;
}

.film-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

/* 响应式调整 */
@media (max-width: 768px) {
    .film-poster {
        height: 150px;
    }
}
'''

    # 检查base.html是否存在
    base_html = os.path.join(os.getcwd(), 'templates', 'base.html')
    if os.path.exists(base_html):
        backup_file(base_html)

        with open(base_html, 'r', encoding='utf-8') as f:
            content = f.read()

        # 在head标签内添加样式
        if '<head>' in content and '</head>' in content:
            head_end_pos = content.find('</head>')
            if head_end_pos != -1:
                # 检查样式是否已存在
                if '/* 海报图片样式 */' not in content:
                    new_content = content[:head_end_pos] + '<style>\n' + base_css + '</style>\n' + content[
                                                                                                   head_end_pos:]
                    with open(base_html, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print("✓ 已在base.html中添加CSS样式")
                else:
                    print("  CSS样式已存在，跳过添加")
            else:
                print("✗ 找不到</head>标签，无法添加CSS样式")
        else:
            print("✗ 找不到<head>标签，无法添加CSS样式")


def main():
    """主函数"""
    print("=" * 70)
    print("全面修复模板文件图片显示问题")
    print("功能: 统一所有页面使用静态文件路径显示海报")
    print("=" * 70)
    print()

    # 查找所有模板文件
    html_files = find_all_template_files()

    if not html_files:
        print("✗ 没有找到HTML模板文件")
        return 1

    print(f"找到 {len(html_files)} 个HTML模板文件:")
    for i, file in enumerate(html_files, 1):
        rel_path = os.path.relpath(file, os.getcwd())
        print(f"  {i:2d}. {rel_path}")
    print()

    # 确认修改
    confirm = input("是否要修复这些文件？(y/n): ").strip().lower()
    if confirm != 'y':
        print("✗ 操作已取消")
        return 0

    print()
    print("开始修复文件...")
    print("-" * 50)

    # 执行修复
    modified_files = []
    total_changes = 0

    for file_path in html_files:
        rel_path = os.path.relpath(file_path, os.getcwd())
        success, changes = fix_template_file(file_path)

        if success:
            modified_files.append((rel_path, changes))
            total_changes += changes
            print(f"✓ 修复成功: {rel_path} ({changes}处修改)")
        else:
            if changes == 0:
                print(f"  无需修复: {rel_path}")
            else:
                print(f"✗ 修复失败: {rel_path}")

    print("-" * 50)
    print()

    # 添加CSS样式
    print("添加CSS样式...")
    add_css_styles()
    print()

    # 显示总结
    print("修复总结:")
    print(f"总文件数: {len(html_files)}")
    print(f"修复文件数: {len(modified_files)}")
    print(f"总修改次数: {total_changes}")
    print()

    if modified_files:
        print("修复详情:")
        for file, changes in modified_files:
            print(f"  - {file}: {changes}处修改")
        print()
    else:
        print("✓ 所有文件都已正确配置")

    print("=" * 70)
    print("修复完成！")
    print("=" * 70)
    print()

    print("后续步骤:")
    print("1. 重启Django服务器: python manage.py runserver")
    print("2. 访问所有页面验证图片显示")
    print("3. 检查是否有遗漏的页面")
    print()

    print("验证方法:")
    print("• 首页: http://localhost:8000/")
    print("• 电影详情页: http://localhost:8000/film/1/ (替换ID)")
    print("• 分类页面: http://localhost:8000/category/1/ (替换ID)")
    print("• 排行榜页面: http://localhost:8000/rankings/")
    print()

    return 0


if __name__ == "__main__":
    exit(main())