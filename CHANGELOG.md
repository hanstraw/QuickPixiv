# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Added
- 🎨 完整的PyQt6图形界面
- 🔐 Token获取和验证功能
- 📥 推荐作品自动下载
- 👥 关注画师作品下载
- ⚙️ 智能筛选功能（收藏数、点赞数）
- 🖼️ 多图片质量选择（original/large/medium/small）
- ⏱️ 可调节下载延迟
- 💾 设置持久化保存
- 📊 实时下载进度显示
- 🚫 下载中断功能
- ⌨️ 所有设置支持键盘输入

### Features
- 使用gppt工具获取Pixiv refresh_token
- 支持按收藏数和点赞数筛选作品
- 自动记录已下载作品，避免重复下载
- 所有设置自动保存到系统注册表
- 下载进度显示"已下载/总数"格式
- 支持最多10000个作品的批量下载

### Technical
- 基于PyQt6构建现代化界面
- 使用pixivpy3进行API调用
- 多线程下载，不阻塞界面
- 完整的错误处理和日志输出
- 支持Windows 10/11系统

### Dependencies
- PyQt6 >= 6.0.0
- pixivpy3 >= 3.7.5
- gppt >= 4.1.1
- requests >= 2.32.4
- cloudscraper >= 1.2.71
- Pillow >= 10.0.1
- tqdm >= 4.66.1 