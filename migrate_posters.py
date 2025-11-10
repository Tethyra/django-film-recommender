
import os
import shutil
import django
import sys


def migrate_poster_files():
    """迁移海报文件"""

    print("=== Windows版海报文件迁移脚本 ===")
    print()

    # 获取脚本所在目录（应该是项目根目录）
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    print(f"脚本所在目录: {script_dir}")

    # 源目录和目标目录（相对于脚本目录）
    source_dir = os.path.join(script_dir, 'static', 'posters')
    target_dir = os.path.join(script_dir, 'media', 'posters')

    print(f"源目录: {source_dir}")
    print(f"目标目录: {target_dir}")
    print()

    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"错误：源目录不存在: {source_dir}")
        print("请确认：")
        print(f"1. 脚本是否在项目根目录下（{script_dir} 应该包含 manage.py）")
        print(f"2. static/posters 目录是否存在")
        return False

    # 创建目标目录（如果不存在）
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"已创建目标目录: {target_dir}")
    else:
        print(f"目标目录已存在: {target_dir}")

    # 获取源目录中的所有图片文件
    try:
        image_files = []
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            if os.path.isfile(file_path):
                # 检查是否为图片文件
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_files.append(filename)

        print(f"发现 {len(image_files)} 个图片文件")

        # 移动文件
        moved_files = 0
        for filename in image_files:
            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)

            try:
                # 检查目标文件是否已存在
                if os.path.exists(target_path):
                    print(f"跳过: {filename} (目标文件已存在)")
                    continue

                # 移动文件
                shutil.move(source_path, target_path)
                print(f"已移动: {filename}")
                moved_files += 1

            except Exception as e:
                print(f"移动文件 {filename} 时出错: {str(e)}")

        print(f"\n迁移完成！成功移动 {moved_files} 个文件")

        return True

    except Exception as e:
        print(f"读取源目录时出错: {str(e)}")
        return False


def main():
    """主函数"""
    try:
        # 首先尝试迁移文件
        migrate_success = migrate_poster_files()

        print("\n=== 重要提示 ===")
        print("1. 请确保已更新 urls.py 文件，添加了媒体文件的URL路由")
        print("2. 请重启Django开发服务器")
        print("3. 访问网站检查图片是否正常显示")

        if not migrate_success:
            print("\n文件迁移失败，请手动检查：")
            print("- static/posters 目录是否存在")
            print("- 目录中是否有图片文件")
            print("- 您是否有访问权限")

        return 0

    except Exception as e:
        print(f"\n执行脚本时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())