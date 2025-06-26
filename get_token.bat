@echo off
chcp 65001 >nul
title QuickPixiv Token获取工具

echo ========================================
echo        QuickPixiv Token获取工具
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

:: 检查gppt是否存在
if not exist "pixiv_env\Scripts\gppt.exe" (
    echo 错误：找不到gppt工具！
    echo 请确保虚拟环境中已安装gppt。
    pause
    exit /b 1
)

echo 正在启动gppt工具获取Pixiv Token...
echo 请在弹出的窗口中输入你的Pixiv账号和密码。
echo.

:: 直接使用gppt.exe
gppt.exe login-interactive

echo.
echo Token获取完成！请将获取到的refresh_token复制到主程序中。
pause 