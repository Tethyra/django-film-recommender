#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录跳转和个人空间修复脚本
修复登录后无法跳转到个人空间的问题
"""

import os
import sys
import shutil
import datetime


def setup_django_env():
    """设置Django环境"""
    try:
        import django
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


# 先设置Django环境
if not setup_django_env():
    print("❌ 无法运行修复脚本")
    sys.exit(1)

from django.conf import settings


def backup_file(file_path, backup_suffix='.backup'):
    """备份文件"""
    try:
        if os.path.exists(file_path):
            backup_path = file_path + backup_suffix
            shutil.copy2(file_path, backup_path)
            print(f"📋 已备份文件: {file_path} -> {backup_path}")
            return True
    except Exception as e:
        print(f"❌ 备份文件失败: {file_path}, 错误: {e}")
    return False


def fix_login_redirect():
    """修复登录重定向问题"""
    print("\n🔧 开始修复登录重定向问题...")

    # 1. 检查并修改settings.py中的登录重定向设置
    settings_path = os.path.join(settings.BASE_DIR, 'film_recommender', 'settings.py')

    if backup_file(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 添加或修改登录重定向设置
            login_redirect_setting = "LOGIN_REDIRECT_URL = 'profile'"
            logout_redirect_setting = "LOGOUT_REDIRECT_URL = 'login'"

            # 检查是否已存在这些设置
            if 'LOGIN_REDIRECT_URL' not in content:
                # 在适当的位置添加设置（通常在认证设置之后）
                if 'AUTH_PASSWORD_VALIDATORS' in content:
                    content = content.replace(
                        'AUTH_PASSWORD_VALIDATORS = [',
                        f'AUTH_PASSWORD_VALIDATORS = [\n{login_redirect_setting}\n{logout_redirect_setting}\n'
                    )
                else:
                    # 添加到文件末尾
                    content += f'\n\n# 登录重定向设置\n{login_redirect_setting}\n{logout_redirect_setting}\n'

            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print("   ✅ 已设置登录重定向到个人空间")
        except Exception as e:
            print(f"   ❌ 修改settings.py失败: {e}")


def fix_profile_urls():
    """修复个人空间URL配置"""
    print("\n🔧 开始修复个人空间URL配置...")

    # 检查主urls.py文件
    main_urls_path = os.path.join(settings.BASE_DIR, 'main', 'urls.py')

    if backup_file(main_urls_path):
        try:
            with open(main_urls_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已存在个人空间URL配置
            profile_url_pattern = "path('profile/', views.profile, name='profile')"

            if profile_url_pattern not in content:
                # 添加个人空间URL
                if 'urlpatterns = [' in content:
                    content = content.replace(
                        'urlpatterns = [',
                        f'urlpatterns = [\n    {profile_url_pattern},\n'
                    )

                with open(main_urls_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print("   ✅ 已添加个人空间URL配置")
            else:
                print("   ⏩ 个人空间URL配置已存在")
        except Exception as e:
            print(f"   ❌ 修改main/urls.py失败: {e}")


def fix_profile_view():
    """修复个人空间视图函数"""
    print("\n🔧 开始修复个人空间视图函数...")

    views_path = os.path.join(settings.BASE_DIR, 'main', 'views.py')

    if backup_file(views_path):
        try:
            with open(views_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已存在profile视图函数
            if 'def profile(request):' not in content:
                # 添加profile视图函数
                profile_view_code = '''
@login_required
def profile(request):
    """个人空间视图"""
    user = request.user

    # 获取用户的收藏
    favorites = Favorite.objects.filter(user=user).select_related('film')

    # 获取用户的观看历史
    watch_history = WatchHistory.objects.filter(user=user).select_related('film').order_by('-watch_time')[:10]

    # 获取用户的评论
    reviews = Review.objects.filter(user=user).select_related('film').order_by('-created_at')[:10]

    # 获取用户统计信息
    stats = {
        'favorite_count': favorites.count(),
        'review_count': Review.objects.filter(user=user).count(),
        'watch_count': WatchHistory.objects.filter(user=user).count()
    }

    context = {
        'user': user,
        'favorites': favorites,
        'watch_history': watch_history,
        'reviews': reviews,
        'stats': stats
    }

    return render(request, 'profile.html', context)
'''

                # 确保导入必要的模块
                required_imports = [
                    'from django.contrib.auth.decorators import login_required',
                    'from .models import Film, Category, Review, Favorite, WatchHistory'
                ]

                for import_line in required_imports:
                    if import_line not in content:
                        content = import_line + '\n' + content

                # 添加视图函数到文件末尾
                content += profile_view_code

                with open(views_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print("   ✅ 已添加个人空间视图函数")
            else:
                print("   ⏩ 个人空间视图函数已存在")
        except Exception as e:
            print(f"   ❌ 修改main/views.py失败: {e}")


def fix_base_template():
    """修复基础模板中的导航链接"""
    print("\n🔧 开始修复基础模板导航链接...")

    base_template_path = os.path.join(settings.BASE_DIR, 'templates', 'base.html')

    if os.path.exists(base_template_path):
        if backup_file(base_template_path):
            try:
                with open(base_template_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查是否已存在个人空间链接
                profile_link = '<a href="{% url \'profile\' %}" class="nav-link">个人空间</a>'

                if profile_link not in content:
                    # 在导航栏中添加个人空间链接
                    # 查找登录状态下的导航区域
                    if '{% if user.is_authenticated %}' in content:
                        # 使用正确的字符串拼接方式
                        content = content.replace(
                            '{% if user.is_authenticated %}',
                            '{% if user.is_authenticated %}\n          ' + profile_link
                        )

                    with open(base_template_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print("   ✅ 已在导航栏添加个人空间链接")
                else:
                    print("   ⏩ 个人空间导航链接已存在")
            except Exception as e:
                print(f"   ❌ 修改base.html失败: {e}")
    else:
        print("   ❌ base.html模板文件不存在")


def create_profile_template():
    """创建个人空间模板"""
    print("\n🔧 开始创建个人空间模板...")

    profile_template_path = os.path.join(settings.BASE_DIR, 'templates', 'profile.html')

    if not os.path.exists(profile_template_path):
        profile_template_content = '''{% extends 'base.html' %}

{% block title %}个人空间 - {{ user.username }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <!-- 侧边栏 -->
        <div class="col-md-3">
            <div class="card mb-4">
                <div class="card-body text-center">
                    {% if user.userprofile.avatar %}
                    <img src="{{ user.userprofile.avatar.url }}" alt="{{ user.username }}" class="rounded-circle mb-3" style="width: 150px; height: 150px; object-fit: cover;">
                    {% else %}
                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mb-3" style="width: 150px; height: 150px; margin: 0 auto;">
                        <span style="font-size: 48px;">{{ user.username|first|upper }}</span>
                    </div>
                    {% endif %}
                    <h4 class="card-title">{{ user.username }}</h4>
                    <p class="card-text text-muted">{{ user.email }}</p>

                    {% if user.userprofile.bio %}
                    <p class="card-text">{{ user.userprofile.bio }}</p>
                    {% endif %}

                    <div class="row mt-3">
                        <div class="col">
                            <div class="text-center">
                                <div class="font-weight-bold">{{ stats.favorite_count }}</div>
                                <div class="text-sm text-muted">收藏</div>
                            </div>
                        </div>
                        <div class="col">
                            <div class="text-center">
                                <div class="font-weight-bold">{{ stats.review_count }}</div>
                                <div class="text-sm text-muted">评论</div>
                            </div>
                        </div>
                        <div class="col">
                            <div class="text-center">
                                <div class="font-weight-bold">{{ stats.watch_count }}</div>
                                <div class="text-sm text-muted">观看</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 主要内容 -->
        <div class="col-md-9">
            <!-- 统计卡片 -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h5 class="card-title">我的收藏</h5>
                            <p class="card-text display-4">{{ stats.favorite_count }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h5 class="card-title">我的评论</h5>
                            <p class="card-text display-4">{{ stats.review_count }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h5 class="card-title">观看记录</h5>
                            <p class="card-text display-4">{{ stats.watch_count }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 观看历史 -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">最近观看</h5>
                </div>
                <div class="card-body">
                    {% if watch_history %}
                    <div class="row">
                        {% for history in watch_history %}
                        <div class="col-md-3 mb-3">
                            <div class="card h-100">
                                {% if history.film.poster %}
                                <img src="{{ history.film.poster.url }}" alt="{{ history.film.title }}" class="card-img-top" style="height: 200px; object-fit: cover;">
                                {% else %}
                                <div class="bg-secondary text-white d-flex align-items-center justify-content-center" style="height: 200px;">
                                    <span>{{ history.film.title|first|upper }}</span>
                                </div>
                                {% endif %}
                                <div class="card-body">
                                    <h6 class="card-title">{{ history.film.title }}</h6>
                                    <p class="card-text text-muted text-sm">
                                        {{ history.watch_time|date:"Y-m-d H:i" }}
                                    </p>
                                    <a href="{% url 'film_detail' history.film.id %}" class="btn btn-primary btn-sm">观看详情</a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-center text-muted">暂无观看历史</p>
                    {% endif %}
                </div>
            </div>

            <!-- 我的收藏 -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">我的收藏</h5>
                </div>
                <div class="card-body">
                    {% if favorites %}
                    <div class="row">
                        {% for favorite in favorites %}
                        <div class="col-md-3 mb-3">
                            <div class="card h-100">
                                {% if favorite.film.poster %}
                                <img src="{{ favorite.film.poster.url }}" alt="{{ favorite.film.title }}" class="card-img-top" style="height: 200px; object-fit: cover;">
                                {% else %}
                                <div class="bg-secondary text-white d-flex align-items-center justify-content-center" style="height: 200px;">
                                    <span>{{ favorite.film.title|first|upper }}</span>
                                </div>
                                {% endif %}
                                <div class="card-body">
                                    <h6 class="card-title">{{ favorite.film.title }}</h6>
                                    <p class="card-text text-muted text-sm">
                                        评分: {{ favorite.film.rating }}
                                    </p>
                                    <a href="{% url 'film_detail' favorite.film.id %}" class="btn btn-primary btn-sm">查看详情</a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-center text-muted">暂无收藏</p>
                    {% endif %}
                </div>
            </div>

            <!-- 我的评论 -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">我的评论</h5>
                </div>
                <div class="card-body">
                    {% if reviews %}
                    <div class="list-group">
                        {% for review in reviews %}
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">
                                        <a href="{% url 'film_detail' review.film.id %}">{{ review.film.title }}</a>
                                    </h6>
                                    <div class="text-warning">
                                        {% for i in "12345"|make_list %}
                                        {% if forloop.counter <= review.rating %}
                                        ★
                                        {% else %}
                                        ☆
                                        {% endif %}
                                        {% endfor %}
                                    </div>
                                    <p class="mb-1">{{ review.content }}</p>
                                    <small class="text-muted">{{ review.created_at|date:"Y-m-d H:i" }}</small>
                                </div>
                                {% if review.film.poster %}
                                <img src="{{ review.film.poster.url }}" alt="{{ review.film.title }}" style="width: 50px; height: 75px; object-fit: cover; border-radius: 4px;">
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-center text-muted">暂无评论</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        with open(profile_template_path, 'w', encoding='utf-8') as f:
            f.write(profile_template_content)

        print("   ✅ 已创建个人空间模板")
    else:
        print("   ⏩ 个人空间模板已存在")


def main():
    """主函数"""
    print("=" * 60)
    print("登录跳转和个人空间修复工具")
    print("修复登录后无法跳转到个人空间的问题")
    print("=" * 60)

    try:
        # 执行各项修复
        fix_login_redirect()
        fix_profile_urls()
        fix_profile_view()
        fix_base_template()
        create_profile_template()

        print("\n" + "=" * 60)
        print("修复完成！")
        print("=" * 60)
        print("\n修复的内容：")
        print("1.  设置登录成功后自动跳转到个人空间")
        print("2.  配置个人空间URL路由")
        print("3.  添加个人空间视图函数")
        print("4.  在导航栏添加个人空间链接")
        print("5.  创建完整的个人空间模板")

        print("\n使用说明：")
        print("1.  现在登录后会自动跳转到个人空间")
        print("2.  可以通过导航栏的'个人空间'链接访问")
        print("3.  个人空间包含：个人资料、收藏、观看历史、评论等")

        print("\n请重启Django服务器使修改生效：")
        print("   python manage.py runserver")

    except KeyboardInterrupt:
        print("\n⏹️ 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 修复过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()