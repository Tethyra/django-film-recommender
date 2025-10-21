# 影视推荐系统 - Django项目说明

## 项目概述
这是一个基于Django框架开发的影视推荐与评论社区系统，采用MySQL数据库存储数据。系统包含用户管理、影视信息展示、分类浏览、排行榜、观看历史、评论社区等基础功能。

## 项目结构

```
film_project/
├── film_recommender/          # 项目主目录
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py            # 项目设置
│   ├── urls.py                # 主URL配置
│   └── wsgi.py
├── main/                      # 主要应用
│   ├── __init__.py
│   ├── admin.py               # 管理界面配置
│   ├── apps.py
│   ├── forms.py               # 表单定义
│   ├── migrations/            # 数据库迁移文件
│   ├── models.py              # 数据模型
│   ├── tests.py               # 测试文件
│   ├── urls.py                # 应用URL配置
│   └── views.py               # 视图函数
├── templates/                 # 模板文件
│   ├── base.html              # 基础模板
│   ├── index.html             # 首页
│   ├── login.html             # 登录页面
│   ├── register.html          # 注册页面
│   ├── category.html          # 分类页面
│   ├── rankings.html          # 排行榜页面
│   ├── history.html           # 观看历史
│   ├── community.html         # 社区页面
│   ├── blackroom.html         # Blackroom页面
│   ├── film_detail.html       # 影视详情
│   ├── add_review.html        # 添加评论
│   └── profile.html           # 个人资料
├── static/                    # 静态文件
│   ├── css/                   # CSS文件
│   ├── js/                    # JavaScript文件
│   └── images/                # 图片文件
├── media/                     # 用户上传文件
│   ├── posters/               # 影视海报
│   └── avatars/               # 用户头像
├── venv/                      # 虚拟环境
├── manage.py                  # Django管理脚本
└── README.md                  # 项目说明文档
```

## 文件存放位置说明

### 1. 模板文件 (templates/)
- `base.html`: 所有页面的基础模板，包含导航栏、页脚和公共样式
- `index.html`: 首页，展示热门推荐、新片上映、经典重温等内容
- `login.html`: 用户登录页面
- `register.html`: 用户注册页面
- `category.html`: 影视分类浏览页面
- `rankings.html`: 影视排行榜页面
- `history.html`: 用户观看历史页面
- `community.html`: 电影社区评论页面
- `blackroom.html`: Blackroom页面（预留功能）
- `film_detail.html`: 影视详情页面（新增）
- `add_review.html`: 添加评论页面（新增）
- `profile.html`: 个人资料页面（新增）

### 2. 主要应用代码 (main/)
- `models.py`: 定义数据库模型（用户、影视、分类、评论、收藏、观看历史等）
- `views.py`: 实现业务逻辑和页面渲染
- `urls.py`: 配置应用URL路由
- `forms.py`: 定义表单验证规则
- `admin.py`: 配置Django管理后台

### 3. 项目配置 (film_recommender/)
- `settings.py`: 项目全局设置，包括数据库配置、静态文件路径等
- `urls.py`: 项目主URL配置

## 数据库设计

### 主要数据表
1. **User**: Django内置用户模型
2. **UserProfile**: 用户扩展资料
3. **Category**: 影视分类
4. **Film**: 影视作品信息
5. **WatchHistory**: 用户观看历史
6. **Favorite**: 用户收藏记录
7. **Review**: 用户评论和评分

## 功能特点

### 1. 用户管理
- 用户注册、登录、退出
- 个人资料管理（头像、简介、生日、喜好分类）
- 密码安全验证

### 2. 影视浏览
- 按分类浏览影视作品
- 查看影视详细信息
- 搜索功能

### 3. 互动功能
- 收藏喜欢的影视作品
- 发表评论和评分
- 查看观看历史

### 4. 内容展示
- 热门推荐
- 分类浏览
- 排行榜展示
- 社区评论展示

## 后续操作步骤

### 1. 环境准备
```bash
# 进入项目目录
cd film_project

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖包
pip install django mysqlclient pillow
```

### 2. 数据库配置
1. 创建MySQL数据库：
```sql
CREATE DATABASE film_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改`settings.py`中的数据库配置：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'film_recommender',
        'USER': '你的MySQL用户名',
        'PASSWORD': '你的MySQL密码',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

### 3. 数据库迁移
```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser
```

### 4. 运行开发服务器
```bash
python manage.py runserver
```

访问地址：http://127.0.0.1:8000/

### 5. 管理后台
访问地址：http://127.0.0.1:8000/admin/
使用创建的超级管理员账号登录，可以管理用户、影视、分类等数据。

### 6. 添加测试数据
通过管理后台添加一些测试数据：
- 影视分类（电影、电视剧、动画等）
- 影视作品信息
- 用户账号（用于测试功能）

## 部署说明

### 生产环境部署建议
1. 使用Gunicorn作为WSGI服务器
2. 使用Nginx作为反向代理
3. 配置静态文件服务
4. 设置数据库连接池
5. 配置SSL证书
6. 设置定期备份

### 部署步骤概要
```bash
# 安装生产依赖
pip install gunicorn

# 收集静态文件
python manage.py collectstatic

# 使用Gunicorn运行
gunicorn film_recommender.wsgi:application --bind 0.0.0.0:8000
```

## 扩展功能建议

### 1. 推荐系统
- 基于用户行为的协同过滤
- 基于内容的推荐算法
- 混合推荐策略

### 2. 社交功能
- 用户关注系统
- 分享功能
- 私信系统

### 3. 内容管理
- 影视资源管理
- 视频播放功能
- 弹幕系统

### 4. 性能优化
- 缓存机制
- 数据库查询优化
- 异步任务处理

## 技术栈总结
- **后端框架**: Django 5.2.2
- **数据库**: MySQL
- **前端技术**: HTML5, CSS3, JavaScript, Bootstrap 5
- **其他**: Font Awesome图标库

## 注意事项
1. 确保MySQL服务正常运行
2. 定期备份数据库
3. 生产环境中修改SECRET_KEY
4. 关闭DEBUG模式
5. 配置ALLOWED_HOSTS
6. 设置适当的文件上传大小限制

## 联系方式
如有问题或建议，请联系项目开发团队。
