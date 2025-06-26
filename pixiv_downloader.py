import os
import time
import re
import requests
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm
from pixivpy3 import AppPixivAPI
# from config import Config

class PixivDownloader:
    def __init__(self, refresh_token, download_path, min_bookmarks=0, min_likes=0, image_quality='original',
                 recommended_limit=20, following_limit=20, delay=1.0, log_func=None):
        self.api = AppPixivAPI()
        self.refresh_token = refresh_token
        self.download_path = download_path
        self.min_bookmarks = min_bookmarks
        self.min_likes = min_likes
        self.image_quality = image_quality
        self.recommended_limit = recommended_limit
        self.following_limit = following_limit
        self.delay = delay
        self.log_func = log_func or print
        Path(download_path).mkdir(parents=True, exist_ok=True)
        self.downloaded_ids = set()
        self._load_downloaded_ids()
    
    def log(self, msg):
        if self.log_func:
            self.log_func(msg)
    
    def _load_downloaded_ids(self):
        """加载已下载的作品ID"""
        file = Path(self.download_path) / "downloaded_ids.txt"
        if file.exists():
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    self.downloaded_ids.add(line.strip())
    
    def _save_downloaded_id(self, illust_id):
        """保存已下载的作品ID"""
        file = Path(self.download_path) / "downloaded_ids.txt"
        with open(file, 'a', encoding='utf-8') as f:
            f.write(f"{illust_id}\n")
        self.downloaded_ids.add(str(illust_id))
    
    def login(self):
        """登录Pixiv账号"""
        try:
            self.api.auth(refresh_token=self.refresh_token)
            self.log("登录成功！")
            return True
        except Exception as e:
            self.log(f"登录失败: {e}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    def _get_image_url(self, illust):
        """获取图片URL"""
        urls = illust['image_urls']
        if self.image_quality == 'original':
            return urls.get('large')
        elif self.image_quality == 'large':
            return urls.get('large')
        elif self.image_quality == 'medium':
            return urls.get('medium')
        else:
            return urls.get('square_medium')
    
    def _should_download(self, illust):
        """判断是否应该下载该作品"""
        # 检查是否已下载
        if str(illust['id']) in self.downloaded_ids:
            return False
        
        # 检查收藏数
        if illust.get('total_bookmarks', 0) < self.min_bookmarks:
            return False
        
        # 检查点赞数
        if illust.get('total_view', 0) < self.min_likes:
            return False
        
        return True
    
    def download_illust(self, illust):
        """下载单个作品"""
        try:
            url = self._get_image_url(illust)
            if not url:
                self.log(f"未找到图片URL: {illust['id']}")
                return False
            
            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                ext = 'jpg'
            
            filename = f"{illust['user']['name']}_{illust['title']}_{illust['id']}.{ext}"
            filename = self._sanitize_filename(filename)
            
            filepath = Path(self.download_path) / filename
            
            # 下载图片
            headers = {
                'Referer': 'https://www.pixiv.net/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 保存作品信息
            self._save_downloaded_id(illust['id'])
            
            self.log(f"✓ 下载完成: {filename}")
            return True
            
        except Exception as e:
            self.log(f"✗ 下载失败 {illust['id']}: {e}")
            return False
    
    def download_recommended(self, progress_callback=None):
        """下载推荐作品"""
        if not self.login():
            return
        
        self.log(f"开始下载推荐作品 (数量: {self.recommended_limit})")
        try:
            result = self.api.illust_recommended()
            illusts = result['illusts']
            count = 0
            for i, illust in enumerate(illusts):
                if count >= self.recommended_limit:
                    break
                if self._should_download(illust):
                    if self.download_illust(illust):
                        count += 1
                        if progress_callback:
                            progress_callback(count, self.recommended_limit)
                        time.sleep(self.delay)
            self.log(f"推荐作品下载完成: {count}/{self.recommended_limit}")
        except Exception as e:
            self.log(f"获取推荐作品失败: {e}")
    
    def download_following(self, progress_callback=None):
        """下载关注画师的最近作品"""
        if not self.login():
            return
        
        self.log(f"开始下载关注画师作品 (数量: {self.following_limit})")
        try:
            following = self.api.user_following(self.api.user_id)
            users = following['user_previews']
            count = 0
            for user in users:
                if count >= self.following_limit:
                    break
                user_id = user['user']['id']
                try:
                    illusts = self.api.user_illusts(user_id)['illusts'][:5]  # 每个用户最多5个作品
                    for illust in illusts:
                        if count >= self.following_limit:
                            break
                        if self._should_download(illust):
                            if self.download_illust(illust):
                                count += 1
                                if progress_callback:
                                    progress_callback(count, self.following_limit)
                                time.sleep(self.delay)
                except Exception as e:
                    self.log(f"获取用户{user_id}作品失败: {e}")
            self.log(f"关注画师作品下载完成: {count}/{self.following_limit}")
        except Exception as e:
            self.log(f"获取关注画师作品失败: {e}")
    
    def run(self):
        """运行下载器"""
        self.log("Pixiv自动下载器启动...")
        
        if not self.login():
            return
        
        total_downloaded = 0
        
        # 下载推荐作品
        recommended_count = self.download_recommended()
        total_downloaded += recommended_count
        
        # 下载关注画师作品
        following_count = self.download_following()
        total_downloaded += following_count
        
        self.log(f"\n下载完成！总共下载了 {total_downloaded} 个作品")
        self.log(f"文件保存在: {self.download_path}") 