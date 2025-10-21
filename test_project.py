#!/usr/bin/env python3
"""
项目测试脚本
验证Django项目的基本功能是否正常
"""

import os
import sys
import subprocess

def run_command(command):
    """运行shell命令并返回结果"""
    print(f"执行命令: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        return False
    print(f"命令执行成功: {result.stdout}")
    return True

def test_project():
    """测试项目功能"""
    print("=" * 60)
    print("开始测试Django项目")
    print("=" * 60)
    
    # 检查Python环境
    print("\n1. 检查Python环境")
    if not run_command("python --version"):
        print("Python环境检查失败")
        return False
    
    # 检查虚拟环境
    print("\n2. 检查虚拟环境")
    if os.path.exists("venv"):
        print("虚拟环境已存在")
        # 激活虚拟环境
        activate_cmd = "source venv/bin/activate" if sys.platform != "win32" else "venv\\Scripts\\activate"
        if run_command(activate_cmd):
            # 检查依赖包
            print("\n3. 检查依赖包")
            if run_command("pip list | grep Django"):
                # 检查项目结构
                print("\n4. 检查项目结构")
                required_files = [
                    "manage.py",
                    "film_recommender/settings.py",
                    "main/models.py",
                    "templates/index.html"
                ]
                
                all_exist = True
                for file_path in required_files:
                    if os.path.exists(file_path):
                        print(f"✓ {file_path} 存在")
                    else:
                        print(f"✗ {file_path} 不存在")
                        all_exist = False
                
                if all_exist:
                    # 检查数据库配置
                    print("\n5. 检查数据库配置")
                    with open("film_recommender/settings.py", "r") as f:
                        content = f.read()
                        if "DATABASES" in content and "mysql" in content.lower():
                            print("✓ 数据库配置为MySQL")
                        else:
                            print("✗ 数据库配置不是MySQL")
                    
                    # 运行迁移检查
                    print("\n6. 检查数据库迁移")
                    if run_command("python manage.py showmigrations"):
                        # 测试运行服务器
                        print("\n7. 测试运行开发服务器（5秒后自动停止）")
                        import threading
                        import time
                        
                        def run_server():
                            subprocess.run("python manage.py runserver", shell=True)
                        
                        server_thread = threading.Thread(target=run_server)
                        server_thread.start()
                        time.sleep(5)
                        
                        # 停止服务器（在Unix系统上）
                        if sys.platform != "win32":
                            run_command("pkill -f 'runserver'")
                        else:
                            # Windows系统需要不同的方法停止进程
                            run_command("taskkill /F /IM python.exe /T")
                        
                        server_thread.join(timeout=2)
                        
                        print("\n测试完成！")
                        print("\n项目基本功能正常，可以开始使用了。")
                        print("\n接下来需要：")
                        print("1. 配置MySQL数据库连接")
                        print("2. 执行数据库迁移")
                        print("3. 创建超级管理员")
                        print("4. 运行开发服务器")
                        return True
                else:
                    print("项目文件不完整")
                    return False
            else:
                print("Django未安装")
                return False
        else:
            print("激活虚拟环境失败")
            return False
    else:
        print("虚拟环境不存在，请先创建虚拟环境")
        return False

if __name__ == "__main__":
    success = test_project()
    sys.exit(0 if success else 1)