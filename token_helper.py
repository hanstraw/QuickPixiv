import subprocess
import sys
import re
from pixivpy3 import *

def get_token_interactive():
    """调用gppt交互式获取refresh_token"""
    try:
        # 使用正确的gppt命令格式
        result = subprocess.run([
            'gppt', 'login-interactive'
        ], capture_output=True, text=True, timeout=300)  # 5分钟超时
        
        # 提取refresh_token
        match = re.search(r'refresh_token: (\w+)', result.stdout)
        if match:
            return match.group(1), result.stdout
        else:
            return None, result.stdout + "\n" + result.stderr
            
    except subprocess.TimeoutExpired:
        return None, "获取token超时，请手动运行: gppt login-interactive"
    except Exception as e:
        return None, str(e)

def refresh_token(old_token):
    """调用gppt刷新refresh_token"""
    try:
        result = subprocess.run([
            'gppt', 'refresh', old_token
        ], capture_output=True, text=True)
        match = re.search(r'refresh_token: (\w+)', result.stdout)
        if match:
            return match.group(1), result.stdout
        else:
            return None, result.stdout
    except Exception as e:
        return None, str(e)

def verify_token(token):
    """验证token是否有效"""
    try:
        # 创建API实例
        api = AppPixivAPI()
        
        # 尝试使用token登录
        result = api.auth(refresh_token=token)
        
        if result:
            # 获取用户信息来验证token
            user_info = api.user_detail(api.user_id)
            username = user_info.user.name
            return token, f"Token验证成功！用户名: {username}"
        else:
            return None, "Token验证失败：登录失败"
            
    except Exception as e:
        return None, f"Token验证失败：{str(e)}" 