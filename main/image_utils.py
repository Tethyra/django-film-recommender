# main/image_utils.py
import os
import requests
from django.conf import settings
from PIL import Image
import io
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL证书验证警告
urllib3.disable_warnings(InsecureRequestWarning)

class ImageManager:
    """图片管理类，处理图片的下载、保存和处理"""
    
    @staticmethod
    def create_image_directory():
        """创建图片存储目录"""
        poster_dir = os.path.join(settings.MEDIA_ROOT, 'posters')
        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        
        # 创建海报目录
        if not os.path.exists(poster_dir):
            os.makedirs(poster_dir, exist_ok=True)
            os.chmod(poster_dir, 0o755)
        
        # 创建头像目录
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir, exist_ok=True)
            os.chmod(avatar_dir, 0o755)
            
        return poster_dir, avatar_dir
    
    @staticmethod
    def download_image(url, save_path, timeout=10, retries=3):
        """
        下载图片并保存到指定路径
        使用picsum.photos作为可靠的图片源
        """
        if not url or not save_path:
            return False
            
        # 创建目录
        ImageManager.create_image_directory()
        
        # 确保保存路径存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        session = requests.Session()
        session.verify = False  # 跳过SSL证书验证
        
        for attempt in range(retries):
            try:
                response = session.get(url, timeout=timeout, stream=True)
                response.raise_for_status()
                
                # 检查是否是图片
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    continue
                
                # 保存图片
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # 验证图片完整性
                if ImageManager.validate_image(save_path):
                    return True
                    
            except Exception as e:
                print(f"下载图片失败 (尝试 {attempt+1}/{retries}): {e}")
                continue
        
        return False
    
    @staticmethod
    def validate_image(file_path):
        """验证图片文件的完整性"""
        try:
            with Image.open(file_path) as img:
                img.verify()  # 验证文件是否是有效的图片
                return True
        except Exception as e:
            print(f"图片验证失败: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return False
    
    @staticmethod
    def create_placeholder_image(text, save_path, size=(300, 450)):
        """创建占位符图片"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建图片
            img = Image.new('RGB', size, color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # 使用默认字体
            try:
                font = ImageFont.truetype('arial.ttf', 16)
            except:
                font = ImageFont.load_default()
            
            # 计算文本位置
            lines = text.split('\n')
            y_text = size[1] // 2 - len(lines) * 10
            
            for line in lines:
                text_width = draw.textlength(line, font=font)
                x_text = (size[0] - text_width) // 2
                draw.text((x_text, y_text), line, font=font, fill='black')
                y_text += 20
            
            # 保存图片
            img.save(save_path, 'JPEG', quality=85)
            return True
            
        except Exception as e:
            print(f"创建占位符图片失败: {e}")
            return False
    
    @staticmethod
    def get_film_poster_url(film_id, width=300, height=450):
        """获取电影海报URL（使用picsum.photos）"""
        # 使用电影ID作为seed，确保每个电影都有唯一的图片
        return f"https://picsum.photos/seed/film{film_id}/{width}/{height}"
    
    @staticmethod
    def download_film_posters(films):
        """批量下载电影海报"""
        poster_dir, _ = ImageManager.create_image_directory()
        success_count = 0
        
        for film in films:
            print(f"正在处理电影: {film.title}")
            
            # 创建保存路径
            poster_path = os.path.join(poster_dir, f"{film.id}.jpg")
            
            if not os.path.exists(poster_path):
                # 获取图片URL
                img_url = ImageManager.get_film_poster_url(film.id)
                
                # 下载图片
                if ImageManager.download_image(img_url, poster_path):
                    # 更新电影海报字段
                    film.poster = f"posters/{film.id}.jpg"
                    film.save()
                    success_count += 1
                    print(f"✓ 成功下载: {film.title}")
                else:
                    # 创建占位符
                    placeholder_text = f"{film.title}\n({film.release_date.year if film.release_date else '未知年份'})"
                    if ImageManager.create_placeholder_image(placeholder_text, poster_path):
                        film.poster = f"posters/{film.id}.jpg"
                        film.save()
                        success_count += 1
                        print(f"✓ 创建占位符: {film.title}")
                    else:
                        print(f"✗ 下载失败: {film.title}")
            else:
                # 图片已存在
                if ImageManager.validate_image(poster_path):
                    film.poster = f"posters/{film.id}.jpg"
                    film.save()
                    success_count += 1
                    print(f"✓ 图片已存在: {film.title}")
                else:
                    os.remove(poster_path)
                    print(f"✗ 图片损坏，重新下载: {film.title}")
        
        return success_count, len(films)