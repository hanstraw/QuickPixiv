@echo off
chcp 65001 >nul
title QuickPixiv 启动器

echo ========================================
echo        QuickPixiv 启动器
echo ========================================
echo.

:: 检查虚拟环境
if not exist "pixiv_env\Scripts\activate.bat" (
    echo 错误：找不到虚拟环境！
    echo 请确保pixiv_env目录完整。
    pause
    exit /b 1
)

:: 激活虚拟环境
call pixiv_env\Scripts\activate.bat

:: 用pythonw.exe启动主程序（无命令行窗口）
start "" pythonw.exe main.py

exit 