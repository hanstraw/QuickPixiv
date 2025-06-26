#!/usr/bin/env python3
"""
QuickPixiv 便携版打包脚本
创建包含Python解释器和虚拟环境的完整便携包
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def create_portable_package():
    """创建便携版包"""
    print("=" * 60)
    print("QuickPixiv 便携版打包工具")
    print("=" * 60)
    
    # 创建便携版目录
    portable_dir = Path("QuickPixiv-Portable")
    if portable_dir.exists():
        print(f"清理目录: {portable_dir}")
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    print(f"创建便携版目录: {portable_dir}")
    
    # 复制核心文件
    core_files = [
        "main.py",
        "pixiv_downloader.py", 
        "token_helper.py",
        "requirements.txt",
        "run.bat",
        "get_token.bat",
        "README-便携版.txt"
    ]
    
    for file in core_files:
        if Path(file).exists():
            shutil.copy2(file, portable_dir / file)
            print(f"复制文件: {file}")
        else:
            print(f"警告: 文件不存在 {file}")
    
    # 复制虚拟环境
    venv_source = Path("pixiv_env")
    venv_dest = portable_dir / "pixiv_env"
    
    if venv_source.exists():
        print("复制虚拟环境...")
        shutil.copytree(venv_source, venv_dest)
        print("虚拟环境复制完成")
    else:
        print("错误: 虚拟环境不存在，请先创建虚拟环境并安装依赖")
        return False
    
    # 创建压缩包
    zip_name = "QuickPixiv-Portable.zip"
    print(f"创建压缩包: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(portable_dir)
                zipf.write(file_path, arc_name)
                print(f"添加文件: {arc_name}")
    
    # 清理临时目录
    shutil.rmtree(portable_dir)
    
    print("\n" + "=" * 60)
    print("便携版打包完成！")
    print(f"压缩包: {zip_name}")
    print("=" * 60)
    
    return True

def main():
    """主函数"""
    try:
        if create_portable_package():
            print("\n✅ 打包成功！")
            print("现在可以将 QuickPixiv-Portable.zip 分发给其他用户。")
            print("用户解压后双击 run.bat 即可运行程序。")
        else:
            print("\n❌ 打包失败！")
    except Exception as e:
        print(f"\n❌ 打包过程中出现错误: {e}")

if __name__ == "__main__":
    main() 