QuickPixiv 便携版使用说明
================================

这是一个完整的便携版QuickPixiv，包含了Python解释器、虚拟环境和所有依赖。

使用方法：
1. 解压到任意目录
2. 双击 run.bat 启动主程序
3. 双击 get_token.bat 获取Pixiv Token

文件说明：
- run.bat          - 主程序启动脚本
- get_token.bat    - Token获取工具
- main.py          - 主程序文件
- pixiv_downloader.py - 下载器核心
- token_helper.py  - Token管理工具
- requirements.txt - 依赖列表
- pixiv_env/       - Python虚拟环境（包含Python解释器和所有依赖）

注意事项：
1. 首次运行可能需要较长时间启动
2. 请确保网络连接正常
3. 某些地区可能需要代理才能访问Pixiv
4. 建议设置适当的下载延迟

故障排除：
- 如果程序无法启动，请检查杀毒软件是否误报
- 如果获取Token失败，请检查网络连接
- 如果下载失败，请检查Token是否有效

技术支持：
https://github.com/hanstraw/QuickPixiv 