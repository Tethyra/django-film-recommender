"""
图片处理工具类
用于处理用户上传的图片，包括缩放、裁剪、格式转换等操作
"""

import os
import uuid
from PIL import Image
from django.conf import settings

class ImageManager:
    """图片管理器类"""
    
    def __init__(self):
        """初始化图片管理器"""
        self.upload_dir = settings.MEDIA_ROOT
        self.allowed_formats = ['jpg', 'jpeg', 'png', 'gif']
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        
    def validate_image(self, image_file):
        """
        验证图片文件
        :param image_file: 图片文件对象
        :return: 验证结果和错误信息
        """
        # 检查文件大小
        if image_file.size > self.max_file_size:
            return False, f"文件大小不能超过{self.max_file_size / 1024 / 1024}MB"
        
        # 检查文件格式
        file_ext = image_file.name.split('.')[-1].lower()
        if file_ext not in self.allowed_formats:
            return False, f"支持的图片格式：{', '.join(self.allowed_formats)}"
        
        return True, ""
    
    def generate_filename(self, original_filename):
        """
        生成唯一的文件名
        :param original_filename: 原始文件名
        :return: 唯一文件名
        """
        file_ext = original_filename.split('.')[-1].lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}.{file_ext}"
    
    def save_image(self, image_file, upload_path='uploads/', width=None, height=None):
        """
        保存图片文件
        :param image_file: 图片文件对象
        :param upload_path: 上传路径
        :param width: 目标宽度
        :param height: 目标高度
        :return: 保存的文件路径
        """
        # 验证图片
        valid, message = self.validate_image(image_file)
        if not valid:
            raise ValueError(message)
        
        # 创建上传目录
        full_upload_path = os.path.join(self.upload_dir, upload_path)
        os.makedirs(full_upload_path, exist_ok=True)
        
        # 生成文件名
        filename = self.generate_filename(image_file.name)
        full_path = os.path.join(full_upload_path, filename)
        
        # 打开并处理图片
        with Image.open(image_file) as img:
            # 如果指定了尺寸，按比例缩放
            if width and height:
                # 计算按比例缩放后的尺寸
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                
                if original_width > original_height:
                    new_width = width
                    new_height = int(width / aspect_ratio)
                else:
                    new_height = height
                    new_width = int(height * aspect_ratio)
                
                # 调整图片尺寸
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存图片
            img.save(full_path)
        
        # 返回相对路径（相对于MEDIA_ROOT）
        relative_path = os.path.join(upload_path, filename)
        return relative_path
    
    def create_thumbnail(self, image_path, thumbnail_path='thumbnails/', size=(100, 100)):
        """
        创建缩略图
        :param image_path: 原图路径
        :param thumbnail_path: 缩略图保存路径
        :param size: 缩略图尺寸
        :return: 缩略图路径
        """
        full_image_path = os.path.join(self.upload_dir, image_path)
        
        if not os.path.exists(full_image_path):
            raise FileNotFoundError(f"图片文件不存在：{full_image_path}")
        
        # 创建缩略图保存目录
        full_thumbnail_path = os.path.join(self.upload_dir, thumbnail_path)
        os.makedirs(full_thumbnail_path, exist_ok=True)
        
        # 生成缩略图文件名
        filename = os.path.basename(image_path)
        thumbnail_filename = f"thumb_{filename}"
        full_thumbnail_filepath = os.path.join(full_thumbnail_path, thumbnail_filename)
        
        # 创建缩略图
        with Image.open(full_image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(full_thumbnail_filepath)
        
        return os.path.join(thumbnail_path, thumbnail_filename)
    
    def delete_image(self, image_path):
        """
        删除图片文件
        :param image_path: 图片路径
        """
        full_path = os.path.join(self.upload_dir, image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            
            # 同时删除可能存在的缩略图
            thumbnail_path = os.path.join('thumbnails', f"thumb_{os.path.basename(image_path)}")
            full_thumbnail_path = os.path.join(self.upload_dir, thumbnail_path)
            if os.path.exists(full_thumbnail_path):
                os.remove(full_thumbnail_path)
    
    def get_image_info(self, image_path):
        """
        获取图片信息
        :param image_path: 图片路径
        :return: 图片信息字典
        """
        full_path = os.path.join(self.upload_dir, image_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"图片文件不存在：{full_path}")
        
        with Image.open(full_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size': os.path.getsize(full_path)
            }

# 创建全局实例
image_manager = ImageManager()