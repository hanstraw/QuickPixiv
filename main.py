#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pixiv自动下载器
自动下载推荐作品和已关注画师的最近作品
"""
import sys
import os
if sys.platform.startswith("win"):
    import ctypes
    myappid = 'pixiv.downloader.gui' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QProgressBar, QSpinBox,
                             QComboBox, QFileDialog, QGroupBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSettings
from PyQt6.QtGui import QFont, QTextCursor, QIcon
from token_helper import verify_token
from pixiv_downloader import PixivDownloader



class DownloadThread(QThread):
    progress_updated = pyqtSignal(int, int)
    log_updated = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, downloader, download_type):
        super().__init__()
        self.downloader = downloader
        self.download_type = download_type
        self._stop_flag = False
    
    def run(self):
        def progress_callback(current, total):
            self.progress_updated.emit(current, total)
            if self._stop_flag:
                raise Exception("下载被用户中断")
        
        def log_callback(msg):
            self.log_updated.emit(msg)
        
        self.downloader.log_func = log_callback
        
        try:
            if self.download_type == "recommended":
                self.downloader.download_recommended(progress_callback)
            elif self.download_type == "following":
                self.downloader.download_following(progress_callback)
        except Exception as e:
            self.log_updated.emit(f"下载出错: {e}")
        finally:
            self.finished.emit()
    
    def stop(self):
        self._stop_flag = True

class TokenThread(QThread):
    token_updated = pyqtSignal(str, str)  # token, output
    
    def __init__(self, action, token=None):
        super().__init__()
        self.action = action
        self.token = token
    
    def run(self):
        if self.action == "verify":
            token, output = verify_token(self.token)
            self.token_updated.emit(token, output)

class PixivDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.token_thread = None
        self.settings = QSettings("PixivDownloader", "GUI")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        self.setWindowIcon(QIcon(str(Path("1.ico").absolute())))
        self.setWindowTitle("Pixiv自动下载器")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Token区域
        token_group = QGroupBox("Token设置")
        token_layout = QVBoxLayout()
        
        # Token输入框
        token_input_layout = QHBoxLayout()
        token_input_layout.addWidget(QLabel("Refresh Token:"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("输入refresh_token或点击获取")
        self.token_input.textChanged.connect(self.save_settings)
        token_input_layout.addWidget(self.token_input)
        token_layout.addLayout(token_input_layout)
        
        # Token按钮区域
        token_btn_layout = QHBoxLayout()
        
        self.open_gppt_btn = QPushButton("获取Token")
        self.open_gppt_btn.clicked.connect(self.open_gppt_window)
        token_btn_layout.addWidget(self.open_gppt_btn)
        
        self.verify_token_btn = QPushButton("验证Token")
        self.verify_token_btn.clicked.connect(self.verify_token)
        token_btn_layout.addWidget(self.verify_token_btn)
        
        token_layout.addLayout(token_btn_layout)
        
        token_group.setLayout(token_layout)
        
        layout.addWidget(token_group)
        
        # 下载设置组
        settings_group = QGroupBox("下载设置")
        settings_layout = QGridLayout(settings_group)
        
        # 下载目录
        settings_layout.addWidget(QLabel("下载目录:"), 0, 0)
        self.download_path_input = QLineEdit("./downloads")
        self.download_path_input.textChanged.connect(self.save_settings)
        settings_layout.addWidget(self.download_path_input, 0, 1)
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self.browse_directory)
        settings_layout.addWidget(self.browse_btn, 0, 2)
        
        # 推荐作品数量
        settings_layout.addWidget(QLabel("推荐作品数量:"), 1, 0)
        self.recommended_limit = QSpinBox()
        self.recommended_limit.setRange(1, 10000)
        self.recommended_limit.setValue(20)
        self.recommended_limit.setSingleStep(1)
        self.recommended_limit.setKeyboardTracking(True)
        self.recommended_limit.valueChanged.connect(self.save_settings)
        settings_layout.addWidget(self.recommended_limit, 1, 1)
        
        # 关注画师作品数量
        settings_layout.addWidget(QLabel("关注画师作品数量:"), 2, 0)
        self.following_limit = QSpinBox()
        self.following_limit.setRange(1, 10000)
        self.following_limit.setValue(20)
        self.following_limit.setSingleStep(1)
        self.following_limit.setKeyboardTracking(True)
        self.following_limit.valueChanged.connect(self.save_settings)
        settings_layout.addWidget(self.following_limit, 2, 1)
        
        # 最小收藏数
        settings_layout.addWidget(QLabel("最小收藏数:"), 3, 0)
        self.min_bookmarks = QSpinBox()
        self.min_bookmarks.setRange(0, 10000)
        self.min_bookmarks.setValue(100)
        self.min_bookmarks.setSingleStep(10)
        self.min_bookmarks.setKeyboardTracking(True)
        self.min_bookmarks.valueChanged.connect(self.save_settings)
        settings_layout.addWidget(self.min_bookmarks, 3, 1)
        
        # 最小点赞数
        settings_layout.addWidget(QLabel("最小点赞数:"), 4, 0)
        self.min_likes = QSpinBox()
        self.min_likes.setRange(0, 10000)
        self.min_likes.setValue(50)
        self.min_likes.setSingleStep(10)
        self.min_likes.setKeyboardTracking(True)
        self.min_likes.valueChanged.connect(self.save_settings)
        settings_layout.addWidget(self.min_likes, 4, 1)
        
        # 图片质量
        settings_layout.addWidget(QLabel("图片质量:"), 5, 0)
        self.image_quality = QComboBox()
        self.image_quality.addItems(["original", "large", "medium", "small"])
        self.image_quality.currentTextChanged.connect(self.save_settings)
        settings_layout.addWidget(self.image_quality, 5, 1)
        
        # 下载延迟
        settings_layout.addWidget(QLabel("下载延迟(毫秒):"), 6, 0)
        self.delay = QSpinBox()
        self.delay.setRange(0, 10000)
        self.delay.setValue(1000)
        self.delay.setSingleStep(100)
        self.delay.setSuffix(" ms")
        self.delay.setKeyboardTracking(True)
        self.delay.valueChanged.connect(self.save_settings)
        settings_layout.addWidget(self.delay, 6, 1)
        
        # 多页仅下载单页
        self.single_page_only = QCheckBox("多页仅下载单页")
        self.single_page_only.setToolTip("勾选后，多页作品只下载第一页；不勾选则下载所有页面")
        self.single_page_only.toggled.connect(self.save_settings)
        settings_layout.addWidget(self.single_page_only, 7, 0, 1, 2)
        
        layout.addWidget(settings_group)
        
        # 下载按钮组
        download_group = QGroupBox("下载操作")
        download_layout = QHBoxLayout(download_group)
        
        self.download_recommended_btn = QPushButton("下载推荐作品")
        self.download_recommended_btn.clicked.connect(lambda: self.start_download("recommended"))
        download_layout.addWidget(self.download_recommended_btn)
        
        self.download_following_btn = QPushButton("下载关注画师作品")
        self.download_following_btn.clicked.connect(lambda: self.start_download("following"))
        download_layout.addWidget(self.download_following_btn)
        
        self.stop_download_btn = QPushButton("打断下载")
        self.stop_download_btn.clicked.connect(self.stop_download)
        self.stop_download_btn.setEnabled(False)
        download_layout.addWidget(self.stop_download_btn)
        
        layout.addWidget(download_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("已下载: %v / %m")
        layout.addWidget(self.progress_bar)
        
        # 日志输出
        log_group = QGroupBox("日志输出")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_output)
        
        # 清空日志按钮
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(self.log_output.clear)
        log_layout.addWidget(clear_log_btn)
        
        layout.addWidget(log_group)
    
    def save_settings(self):
        self.settings.setValue("token", self.token_input.text())
        self.settings.setValue("download_path", self.download_path_input.text())
        self.settings.setValue("recommended_limit", self.recommended_limit.value())
        self.settings.setValue("following_limit", self.following_limit.value())
        self.settings.setValue("min_bookmarks", self.min_bookmarks.value())
        self.settings.setValue("min_likes", self.min_likes.value())
        self.settings.setValue("image_quality", self.image_quality.currentText())
        self.settings.setValue("delay", self.delay.value())
        self.settings.setValue("single_page_only", self.single_page_only.isChecked())
        self.settings.sync()  # 强制同步到磁盘
    
    def load_settings(self):
        token = self.settings.value("token", "")
        download_path = self.settings.value("download_path", "./downloads")
        recommended_limit = int(self.settings.value("recommended_limit", 20))
        following_limit = int(self.settings.value("following_limit", 20))
        min_bookmarks = int(self.settings.value("min_bookmarks", 100))
        min_likes = int(self.settings.value("min_likes", 50))
        image_quality = self.settings.value("image_quality", "original")
        delay = int(self.settings.value("delay", 1000))
        single_page_only = self.settings.value("single_page_only", False, type=bool)
        
        self.token_input.setText(token)
        self.download_path_input.setText(download_path)
        self.recommended_limit.setValue(recommended_limit)
        self.following_limit.setValue(following_limit)
        self.min_bookmarks.setValue(min_bookmarks)
        self.min_likes.setValue(min_likes)
        self.image_quality.setCurrentText(image_quality)
        self.delay.setValue(delay)
        self.single_page_only.setChecked(single_page_only)
    
    def log(self, message):
        self.log_output.append(f"[{QApplication.instance().applicationName()}] {message}")
        self.log_output.moveCursor(QTextCursor.MoveOperation.End)
    
    def open_gppt_window(self):
        """打开独立的命令行窗口运行gppt"""
        try:
            import subprocess
            subprocess.Popen(['cmd', '/k', 'gppt login-interactive'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log("已打开命令行窗口，请在窗口中输入账号密码")
        except Exception as e:
            self.log(f"打开命令行窗口失败: {e}")
            self.log("请手动打开命令行并运行: gppt login-interactive")
    
    def verify_token(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "警告", "请先输入要验证的token")
            return
        
        self.log("正在验证token...")
        
        self.token_thread = TokenThread("verify", token)
        self.token_thread.token_updated.connect(self.on_token_updated)
        self.token_thread.finished.connect(self.on_token_finished)
        self.token_thread.start()
    
    def on_token_updated(self, token, output):
        if token:
            self.token_input.setText(token)
            self.log("Token验证成功！")
        else:
            self.log("Token验证失败")
        
        self.log("gppt输出:")
        for line in output.split('\n'):
            if line.strip():
                self.log(line.strip())
        self.save_settings()
    
    def on_token_finished(self):
        self.log("Token验证完成！")
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择下载目录")
        if directory:
            self.download_path_input.setText(directory)
    
    def start_download(self, download_type):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "警告", "请先获取或输入refresh_token")
            return
        
        download_path = self.download_path_input.text().strip()
        if not download_path:
            QMessageBox.warning(self, "警告", "请设置下载目录")
            return
        
        # 创建下载器
        downloader = PixivDownloader(
            refresh_token=token,
            download_path=download_path,
            min_bookmarks=self.min_bookmarks.value(),
            min_likes=self.min_likes.value(),
            image_quality=self.image_quality.currentText(),
            recommended_limit=self.recommended_limit.value(),
            following_limit=self.following_limit.value(),
            delay=self.delay.value() / 1000.0,  # 将毫秒转换为秒
            single_page_only=self.single_page_only.isChecked(),  # 添加多页仅下载单页设置
            log_func=self.log
        )
        
        # 禁用下载按钮
        self.download_recommended_btn.setEnabled(False)
        self.download_following_btn.setEnabled(False)
        self.stop_download_btn.setEnabled(True)
        
        # 启动下载线程
        self.download_thread = DownloadThread(downloader, download_type)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.log_updated.connect(self.log)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def stop_download(self):
        if self.download_thread:
            self.download_thread.stop()
            self.log("已请求中断下载，等待线程退出...")
        self.stop_download_btn.setEnabled(False)
    
    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def on_download_finished(self):
        self.download_recommended_btn.setEnabled(True)
        self.download_following_btn.setEnabled(True)
        self.stop_download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log("下载完成！")

def main():
    
    app = QApplication(sys.argv)
    app.setApplicationName("Pixiv下载器")
    
    window = PixivDownloaderGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 