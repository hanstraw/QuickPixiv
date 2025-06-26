# QuickPixiv

一个基于PyQt6的Pixiv自动下载器，支持下载推荐作品和关注画师的最新作品。

## 功能特性

- 🎨 **推荐作品下载**：自动下载Pixiv推荐的作品
- 👥 **关注画师作品**：下载已关注画师的最新作品
- ⚙️ **智能筛选**：支持按收藏数、点赞数筛选作品
- 🖼️ **多质量选择**：支持original、large、medium、small四种图片质量
- ⏱️ **下载控制**：可调节下载延迟，避免请求过于频繁
- 💾 **设置持久化**：所有设置自动保存，重启后不丢失
- 🚫 **下载中断**：支持随时中断下载任务
- 📊 **进度显示**：实时显示下载进度

## 安装要求

- Python 3.8+
- Windows 10/11

## 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/QuickPixiv.git
cd QuickPixiv
```

2. **创建虚拟环境**
```bash
python -m venv pixiv_env
pixiv_env\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **获取Pixiv Token**
   - 运行程序后点击"获取Token"按钮
   - 在弹出的命令行窗口中输入Pixiv账号密码
   - 复制获取到的refresh_token到程序中

## 使用方法

1. **启动程序**
```bash
python main.py
```

2. **获取Token**
   - 点击"获取Token"按钮打开命令行窗口
   - 输入Pixiv账号和密码
   - 将获取到的refresh_token复制到输入框
   - 点击"验证Token"确认有效性

3. **配置下载设置**
   - 设置下载目录
   - 调整作品数量限制
   - 设置筛选条件（最小收藏数、点赞数）
   - 选择图片质量
   - 设置下载延迟

4. **开始下载**
   - 点击"下载推荐作品"下载推荐内容
   - 点击"下载关注画师作品"下载关注画师作品
   - 可随时点击"打断下载"中断任务

## 配置说明

### 下载设置
- **推荐作品数量**：1-10000，控制下载的推荐作品数量
- **关注画师作品数量**：1-10000，控制下载的关注画师作品数量
- **最小收藏数**：0-10000，只下载收藏数超过此值的作品
- **最小点赞数**：0-10000，只下载点赞数超过此值的作品
- **图片质量**：original/large/medium/small，选择下载的图片质量
- **下载延迟**：0-10000毫秒，控制下载间隔

### 文件结构
```
QuickPixiv/
├── main.py              # 主程序入口
├── pixiv_downloader.py  # 下载器核心类
├── token_helper.py      # Token管理工具
├── requirements.txt     # 依赖列表
├── README.md           # 项目说明
└── downloads/          # 下载目录（自动创建）
```

## 注意事项

- 请遵守Pixiv的使用条款和版权规定
- 建议设置适当的下载延迟，避免对服务器造成压力
- Token有效期为30天，过期需要重新获取
- 下载的作品会保存在downloads目录中，按画师ID分类

## 技术栈

- **GUI框架**：PyQt6
- **Pixiv API**：pixivpy3
- **Token获取**：gppt
- **网络请求**：requests + cloudscraper
- **图片处理**：Pillow

## 许可证

本项目仅供学习和个人使用，请遵守相关法律法规和网站使用条款。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持推荐作品和关注画师作品下载
- 完整的PyQt6图形界面
- 设置持久化保存
- 下载进度显示和中断功能 