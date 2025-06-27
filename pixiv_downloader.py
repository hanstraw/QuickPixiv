import os
import time
import re
import requests
from pathlib import Path
from typing import Optional
from pixivpy3 import AppPixivAPI


class PixivDownloader:
    def __init__(self, refresh_token, download_path, min_bookmarks=0, min_likes=0, image_quality='original',
                 recommended_limit=20, following_limit=20, delay=1.0, single_page_only=False, log_func=None):
        self.api = AppPixivAPI()
        self.refresh_token = refresh_token
        self.download_path = Path(download_path)
        self.min_bookmarks = min_bookmarks
        self.min_likes = min_likes
        self.image_quality = image_quality.lower()
        self.recommended_limit = recommended_limit
        self.following_limit = following_limit
        self.delay = delay
        self.single_page_only = single_page_only
        self.log_func = log_func or print
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.downloaded_ids = set()
        self._load_downloaded_ids()

    def log(self, msg):
        if self.log_func:
            self.log_func(msg)

    def _load_downloaded_ids(self):
        file = self.download_path / "downloaded_ids.txt"
        if file.exists():
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    self.downloaded_ids.add(line.strip())

    def _save_downloaded_id(self, illust_id):
        file = self.download_path / "downloaded_ids.txt"
        with open(file, 'a', encoding='utf-8') as f:
            f.write(f"{illust_id}\n")
        self.downloaded_ids.add(str(illust_id))

    def login(self):
        try:
            self.api.auth(refresh_token=self.refresh_token)
            self.log("登录成功！")
            return True
        except Exception as e:
            self.log(f"登录失败: {e}")
            return False

    def _sanitize_filename(self, filename: str) -> str:
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def _get_image_url(self, illust, page_index=0) -> Optional[str]:
        # 支持多页作品，page_index 默认0
        if self.image_quality == 'original':
            # 单页图的原图
            if 'meta_single_page' in illust and illust['meta_single_page'].get('original_image_url'):
                return illust['meta_single_page']['original_image_url']
            # 多页图取指定页的原图
            if 'meta_pages' in illust and len(illust['meta_pages']) > page_index:
                return illust['meta_pages'][page_index]['image_urls'].get('original')
            # 兜底
            return illust['image_urls'].get('large')
        elif self.image_quality == 'large':
            if 'meta_pages' in illust and len(illust['meta_pages']) > page_index:
                return illust['meta_pages'][page_index]['image_urls'].get('large')
            return illust['image_urls'].get('large')
        elif self.image_quality == 'medium':
            if 'meta_pages' in illust and len(illust['meta_pages']) > page_index:
                return illust['meta_pages'][page_index]['image_urls'].get('medium')
            return illust['image_urls'].get('medium')
        else:
            if 'meta_pages' in illust and len(illust['meta_pages']) > page_index:
                return illust['meta_pages'][page_index]['image_urls'].get('square_medium')
            return illust['image_urls'].get('square_medium')

    def _should_download(self, illust):
        if str(illust['id']) in self.downloaded_ids:
            return False
        if illust.get('total_bookmarks', 0) < self.min_bookmarks:
            return False
        if illust.get('total_view', 0) < self.min_likes:
            return False
        return True

    def download_illust(self, illust):
        try:
            illust_id = illust['id']
            user_name = illust['user']['name']
            title = illust['title']

            # 判断是否多页作品
            pages = illust.get('meta_pages', [])
            if not pages:
                pages = [{}]  # 单页作品用空 dict 模拟

            # 如果设置了只下载单页且是多页作品，则只下载第一页
            if self.single_page_only and len(pages) > 1:
                pages = pages[:1]  # 只保留第一页
                self.log(f"多页作品 {illust_id} 仅下载第一页")

            for i, _ in enumerate(pages):
                url = self._get_image_url(illust, page_index=i)
                if not url:
                    self.log(f"未找到图片URL: {illust_id} 页码: {i}")
                    continue

                ext = url.split('.')[-1].split('?')[0].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                    ext = 'jpg'

                if len(illust.get('meta_pages', [])) > 1:
                    filename = f"{user_name}_{title}_{illust_id}_p{i}.{ext}"
                else:
                    filename = f"{user_name}_{title}_{illust_id}.{ext}"

                filename = self._sanitize_filename(filename)
                filepath = self.download_path / filename

                headers = {
                    'Referer': 'https://www.pixiv.net/',
                    'User-Agent': 'Mozilla/5.0'
                }

                # 下载图片
                response = requests.get(url, headers=headers, stream=True)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                self.log(f"✓ 下载完成: {filename}")
                time.sleep(self.delay)

            self._save_downloaded_id(illust_id)
            return True
        except Exception as e:
            self.log(f"✗ 下载失败 {illust['id']}: {e}")
            return False

    def download_recommended(self, progress_callback=None):
        if not self.login():
            return 0

        self.log(f"开始下载推荐作品 (数量: {self.recommended_limit})")
        offset = 0
        count = 0
        try:
            while count < self.recommended_limit:
                result = self.api.illust_recommended(offset=offset)
                illusts = result.get('illusts', [])
                if not illusts:
                    break
                for illust in illusts:
                    if count >= self.recommended_limit:
                        break
                    if self._should_download(illust):
                        if self.download_illust(illust):
                            count += 1
                            if progress_callback:
                                progress_callback(count, self.recommended_limit)
                    time.sleep(self.delay)
                offset += len(illusts)
        except Exception as e:
            self.log(f"获取推荐作品失败: {e}")

        self.log(f"推荐作品下载完成: {count}/{self.recommended_limit}")
        return count

    def download_following(self, progress_callback=None):
        if not self.login():
            return 0

        self.log(f"开始下载关注画师作品 (数量: {self.following_limit})")
        count = 0
        try:
            following = self.api.user_following(self.api.user_id)
            users = following.get('user_previews', [])
            for user in users:
                if count >= self.following_limit:
                    break
                user_id = user['user']['id']
                try:
                    illusts = self.api.user_illusts(user_id).get('illusts', [])[:5]
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
        except Exception as e:
            self.log(f"获取关注画师作品失败: {e}")

        self.log(f"关注画师作品下载完成: {count}/{self.following_limit}")
        return count

    def run(self):
        self.log("Pixiv自动下载器启动...")
        if not self.login():
            return

        total_downloaded = 0
        total_downloaded += self.download_recommended()
        total_downloaded += self.download_following()

        self.log(f"\n下载完成！总共下载了 {total_downloaded} 个作品")
        self.log(f"文件保存在: {self.download_path}")


