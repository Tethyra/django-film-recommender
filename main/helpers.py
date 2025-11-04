#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海报显示辅助函数
"""

import os
from django.conf import settings

def get_poster_url(film_title):
    """
    获取海报URL
    使用电影标题生成图片文件名
    """
    # 将标题转换为适合文件名的格式
    safe_title = film_title.replace(' ', '_').replace(':', '').replace('"', '').replace("'", "").replace('?', '').replace('*', '').lower()

    # 检查文件是否存在
    poster_path = os.path.join(settings.STATIC_ROOT, 'posters', f"{safe_title}_medium.jpg")
    if os.path.exists(poster_path):
        return f"/static/posters/{safe_title}_medium.jpg"

    # 检查slugify格式
    from django.utils.text import slugify
    slugified_title = slugify(film_title)
    poster_path_slug = os.path.join(settings.STATIC_ROOT, 'posters', f"{slugified_title}_medium.jpg")
    if os.path.exists(poster_path_slug):
        return f"/static/posters/{slugified_title}_medium.jpg"

    # 默认占位图
    return "https://via.placeholder.com/400x600?text=No+Poster"

def list_poster_files():
    """列出所有海报文件"""
    poster_dir = os.path.join(settings.STATIC_ROOT, 'posters')
    if not os.path.exists(poster_dir):
        return []

    import glob
    poster_files = glob.glob(os.path.join(poster_dir, '*_medium.jpg'))
    return [os.path.basename(f) for f in poster_files]
