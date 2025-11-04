#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django图表功能诊断和修复工具（修复版）
避免死循环问题
"""

import os
import sys
import shutil
import datetime
import traceback


class DjangoChartDiagnostic:
    def __init__(self):
        self.project_root = None
        self.issues = []
        self.fixes_applied = []

    def print_success(self, message):
        """打印成功信息"""
        print(f"✅ {message}")

    def print_error(self, message):
        """打印错误信息"""
        print(f"❌ {message}")
        self.issues.append(message)

    def print_warning(self, message):
        """打印警告信息"""
        print(f"⚠️  {message}")

    def print_info(self, message):
        """打印信息"""
        print(f"ℹ️  {message}")

    def backup_file(self, file_path, backup_suffix=None):
        """备份文件"""
        try:
            if os.path.exists(file_path):
                if backup_suffix is None:
                    backup_suffix = '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = file_path + backup_suffix
                shutil.copy2(file_path, backup_path)
                self.print_info(f"已备份文件: {file_path} -> {backup_path}")
                return True
        except Exception as e:
            self.print_error(f"备份文件失败: {file_path}, 错误: {e}")
        return False

    def detect_project_root(self):
        """检测项目根目录"""
        self.print_info("正在检测项目根目录...")

        # 从当前目录开始查找
        current_dir = os.path.abspath(os.path.dirname(__file__))

        # 查找包含manage.py的目录
        for root, dirs, files in os.walk(current_dir):
            if 'manage.py' in files:
                self.project_root = root
                self.print_success(f"找到项目根目录: {self.project_root}")
                return True

        # 如果找不到，让用户输入（最多尝试3次）
        self.print_error("无法自动检测项目根目录")
        max_attempts = 3
        for attempt in range(max_attempts):
            self.print_info(f"尝试 {attempt + 1}/{max_attempts}")
            project_dir = input("请输入项目根目录路径 (输入 'q' 退出): ").strip()

            if project_dir.lower() == 'q':
                self.print_info("用户选择退出")
                return False

            if os.path.exists(os.path.join(project_dir, 'manage.py')):
                self.project_root = project_dir
                self.print_success(f"使用项目根目录: {self.project_root}")
                return True
            else:
                self.print_error("无效的项目目录，请重新输入")

        self.print_error(f"超过最大尝试次数 ({max_attempts})")
        return False

    def check_urls_syntax_simple(self):
        """简单检查URL语法"""
        self.print_info("正在检查URL配置语法...")

        urls_path = os.path.join(self.project_root, 'film_recommender', 'urls.py')

        if not os.path.exists(urls_path):
            self.print_error("urls.py文件不存在")
            return False

        try:
            with open(urls_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查常见的语法错误
            syntax_errors = []

            # 检查反斜杠问题
            if 'urlpatterns = [\\' in content:
                syntax_errors.append("发现反斜杠语法错误")

            # 检查\n字符问题
            if '\\n' in content:
                syntax_errors.append("发现\\n字符问题")

            # 检查逗号问题
            if 'path(' in content and 'path(' in content.replace('path(', '', 1):
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'path(' in line and '),' not in line and 'urlpatterns' not in line:
                        syntax_errors.append(f"第{i + 1}行可能缺少逗号")

            if syntax_errors:
                for error in syntax_errors:
                    self.print_error(error)
                return False
            else:
                self.print_success("URL配置语法检查通过")
                return True

        except Exception as e:
            self.print_error(f"检查URL配置失败: {e}")
            return False

    def fix_urls_file_simple(self):
        """简单修复URL文件"""
        self.print_info("正在修复URL配置...")

        urls_path = os.path.join(self.project_root, 'film_recommender', 'urls.py')

        if not self.backup_file(urls_path):
            return False

        try:
            with open(urls_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 保存原始内容用于对比
            original_content = content

            # 简单修复
            content = content.replace('urlpatterns = [\\', 'urlpatterns = [')
            content = content.replace('\\n', '\n')

            # 确保charts URL存在
            if 'charts/' not in content:
                content = content.replace(
                    'urlpatterns = [',
                    'urlpatterns = [\n    path(\'charts/\', include(\'charts.urls\')),'
                )

            if content != original_content:
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.print_success("URL配置修复完成")
                self.fixes_applied.append("URL配置修复")
                return True
            else:
                self.print_info("URL配置无需修复")
                return True

        except Exception as e:
            self.print_error(f"修复URL配置失败: {e}")
            return False

    def check_basic_requirements(self):
        """检查基本要求"""
        self.print_info("正在检查基本要求...")

        required_files = [
            ('manage.py', '项目管理文件'),
            ('film_recommender/settings.py', '项目设置'),
            ('film_recommender/urls.py', '主URL配置'),
            ('main/models.py', '主应用模型'),
        ]

        all_ok = True
        for path, description in required_files:
            full_path = os.path.join(self.project_root, path)
            if os.path.exists(full_path):
                self.print_success(f"✓ {path} - {description}")
            else:
                self.print_error(f"✗ {path} - {description}")
                all_ok = False

        return all_ok

    def check_charts_app_basic(self):
        """检查charts应用基本结构"""
        self.print_info("正在检查charts应用...")

        charts_dir = os.path.join(self.project_root, 'charts')

        if not os.path.exists(charts_dir):
            self.print_error("charts应用目录不存在")
            return False

        required_files = [
            '__init__.py',
            'apps.py',
            'urls.py',
            'views.py',
        ]

        missing_files = []
        for file in required_files:
            file_path = os.path.join(charts_dir, file)
            if os.path.exists(file_path):
                self.print_success(f"✓ charts/{file}")
            else:
                self.print_error(f"✗ charts/{file}")
                missing_files.append(file)

        if missing_files:
            self.print_warning("发现缺失文件")
            return False
        else:
            self.print_success("charts应用检查通过")
            return True

    def create_minimal_charts_app(self):
        """创建最小化的charts应用"""
        self.print_info("正在创建最小化charts应用...")

        charts_dir = os.path.join(self.project_root, 'charts')

        if os.path.exists(charts_dir):
            self.print_warning("charts目录已存在，跳过创建")
            return True

        try:
            os.makedirs(charts_dir)

            # 创建最小化的必要文件
            init_content = '''"""图表应用初始化"""
default_app_config = 'charts.apps.ChartsConfig'
'''

            apps_content = '''"""图表应用配置"""
from django.apps import AppConfig

class ChartsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'charts'
'''

            urls_content = '''"""图表URL配置"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.charts_dashboard, name='charts_dashboard'),
    path('data/<str:chart_type>/', views.get_chart_data, name='get_chart_data'),
]
'''

            with open(os.path.join(charts_dir, '__init__.py'), 'w', encoding='utf-8') as f:
                f.write(init_content)

            with open(os.path.join(charts_dir, 'apps.py'), 'w', encoding='utf-8') as f:
                f.write(apps_content)

            with open(os.path.join(charts_dir, 'urls.py'), 'w', encoding='utf-8') as f:
                f.write(urls_content)

            self.print_success("最小化charts应用创建完成")
            self.fixes_applied.append("创建charts应用")
            return True

        except Exception as e:
            self.print_error(f"创建charts应用失败: {e}")
            return False

    def check_settings_basic(self):
        """检查基本设置"""
        self.print_info("正在检查基本设置...")

        settings_path = os.path.join(self.project_root, 'film_recommender', 'settings.py')

        if not os.path.exists(settings_path):
            self.print_error("settings.py文件不存在")
            return False

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查INSTALLED_APPS
            if 'charts' in content:
                self.print_success("✓ charts应用已配置")
            else:
                self.print_error("✗ charts应用未配置")
                return False

            # 检查静态文件配置
            if 'STATIC_URL' in content:
                self.print_success("✓ 静态文件配置已存在")
            else:
                self.print_warning("✗ 静态文件配置缺失")

            return True

        except Exception as e:
            self.print_error(f"检查设置失败: {e}")
            return False

    def add_charts_to_settings(self):
        """添加charts到设置"""
        self.print_info("正在添加charts到项目设置...")

        settings_path = os.path.join(self.project_root, 'film_recommender', 'settings.py')

        if not self.backup_file(settings_path):
            return False

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'charts' not in content:
                # 找到INSTALLED_APPS部分
                if 'INSTALLED_APPS = [' in content:
                    # 在main应用后添加charts
                    content = content.replace(
                        'main.apps.MainConfig',
                        'main.apps.MainConfig,\\n    \'charts.apps.ChartsConfig\''
                    )
                    self.print_success("已添加charts到INSTALLED_APPS")
                else:
                    self.print_error("未找到INSTALLED_APPS配置")
                    return False

            # 添加静态文件配置
            if 'STATIC_URL' not in content:
                static_config = '''
# 静态文件配置
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
'''
                content += static_config
                self.print_success("已添加静态文件配置")

            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.print_success("项目设置更新完成")
            self.fixes_applied.append("更新项目设置")
            return True

        except Exception as e:
            self.print_error(f"更新设置失败: {e}")
            return False

    def create_basic_template(self):
        """创建基本模板目录"""
        self.print_info("正在创建模板目录...")

        templates_dir = os.path.join(self.project_root, 'templates', 'charts')
        os.makedirs(templates_dir, exist_ok=True)

        # 创建一个简单的模板文件
        basic_template = '''{% extends 'base.html' %}

{% block title %}数据可视化{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>数据可视化仪表板</h1>
    <p>图表功能正在加载...</p>

    {% if error %}
    <div class="alert alert-danger">
        {{ error }}
    </div>
    {% endif %}
</div>
{% endblock %}
'''

        try:
            with open(os.path.join(templates_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
                f.write(basic_template)

            self.print_success("基本模板创建完成")
            self.fixes_applied.append("创建基本模板")
            return True

        except Exception as e:
            self.print_error(f"创建模板失败: {e}")
            return False

    def run_simple_diagnostic(self):
        """运行简单诊断"""
        self.print_info("=" * 60)
        self.print_info("Django图表功能简单诊断工具")
        self.print_info("=" * 60)

        try:
            # 1. 检测项目根目录
            if not self.detect_project_root():
                self.print_error("无法继续诊断，缺少项目根目录")
                return False

            # 2. 检查基本要求
            basic_ok = self.check_basic_requirements()
            if not basic_ok:
                self.print_error("基本项目结构不完整")
                return False

            # 3. 检查URL配置
            urls_ok = self.check_urls_syntax_simple()
            if not urls_ok:
                self.print_info("尝试修复URL配置...")
                self.fix_urls_file_simple()

            # 4. 检查或创建charts应用
            charts_ok = self.check_charts_app_basic()
            if not charts_ok:
                self.print_info("尝试创建charts应用...")
                self.create_minimal_charts_app()

            # 5. 检查项目设置
            settings_ok = self.check_settings_basic()
            if not settings_ok:
                self.print_info("尝试更新项目设置...")
                self.add_charts_to_settings()

            # 6. 创建基本模板
            self.create_basic_template()

            return True

        except Exception as e:
            self.print_error(f"诊断过程中发生错误: {e}")
            traceback.print_exc()
            return False

    def generate_simple_report(self):
        """生成简单报告"""
        self.print_info("\n" + "=" * 60)
        self.print_info("诊断报告摘要")
        self.print_info("=" * 60)

        if self.issues:
            self.print_error(f"发现 {len(self.issues)} 个问题")
        else:
            self.print_success("未发现明显问题")

        if self.fixes_applied:
            self.print_success(f"已应用 {len(self.fixes_applied)} 个修复:")
            for fix in self.fixes_applied:
                self.print_success(f"- {fix}")

        self.print_info("\n下一步操作:")
        self.print_info("1. 确保charts/views.py文件存在且包含正确的视图函数")
        self.print_info("2. 重新启动Django服务器:")
        self.print_info(f"   cd {self.project_root}")
        self.print_info("   python manage.py runserver")
        self.print_info("3. 访问图表功能: http://127.0.0.1:8000/charts/")

        if not self.issues:
            self.print_info("\n如果仍然有问题，请:")
            self.print_info("- 检查charts/views.py是否包含charts_dashboard函数")
            self.print_info("- 确保所有依赖包已安装: pip install matplotlib Pillow")
            self.print_info("- 查看Django服务器日志获取详细错误信息")


def main():
    """主函数"""
    diagnostic = DjangoChartDiagnostic()

    try:
        diagnostic.run_simple_diagnostic()
        diagnostic.generate_simple_report()

    except KeyboardInterrupt:
        diagnostic.print_info("\n⏹️ 操作被用户中断")
    except Exception as e:
        diagnostic.print_error(f"程序运行中发生错误: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()