import os
import base64

import httpx
import ujson as json
from loguru import logger
import browser_cookie3

from .util import save_json


def get_cookie_dict(cookie='', name=None) -> dict:
    """获取cookie字典
    
    Args:
        cookie: cookie字符串，如果为空则从账号管理器获取
        name: 账号名称，用于从账号管理器获取指定账号的cookie
    """
    # 如果没有提供cookie，尝试从账号管理器获取
    if not cookie or cookie == '':
        try:
            from utils.account_manager import AccountManager
            manager = AccountManager.get_instance()
            if manager and hasattr(manager, 'accounts') and manager.accounts:
                cookie_dict = manager.get_cookie_dict(name)
                if cookie_dict:
                    return cookie_dict
            # 如果账号管理器中没有账号，不输出警告日志，直接尝试其他方式
        except Exception as e:
            # 减少日志输出，只在真正出错时记录
            pass
    
    # 原有的逻辑保持不变
    if cookie:
        # 自动读取的cookie有效期短，且不一定有效
        if cookie in ['edge', 'chrome']:
            cj = eval(f"browser_cookie3.{cookie}(domain_name='douyin.com')")
            cookie = httpx.Cookies(cj)
        else:
            # 只接受base64格式的cookie
            try:
                decoded_cookie = base64.b64decode(cookie).decode('utf-8')
                cookie = cookies_str_to_dict(decoded_cookie)
            except Exception as e:
                logger.error(f"Cookie必须是base64格式: {e}")
                return {}
        save_cookie(cookie)
    elif os.path.exists('config/cookie.json'):
        with open('config/cookie.json', 'r', encoding='utf-8') as f:
            cookie = json.load(f)
    elif os.path.exists('config/cookie.txt'):
        with open('config/cookie.txt', 'r', encoding='utf-8') as f:
            # 只接受base64格式的cookie
            try:
                decoded_cookie = base64.b64decode(f.read().strip()).decode('utf-8')
                cookie = cookies_str_to_dict(decoded_cookie)
            except Exception as e:
                logger.error(f"Cookie文件必须包含base64格式的cookie: {e}")
                return {}
    else:
        # 只有在真正使用时才提示，避免启动时的噪音
        # 返回空字典，让调用者决定如何处理
        return {}
    return cookie


def save_cookie(cookie: dict):
    save_json('config/cookie', cookie)


def test_cookie(cookie):
    """使用get_user_info_self API测试cookie是否有效"""
    from utils.request import Request
    
    # 处理cookie格式
    if type(cookie) is dict:
        cookie_dict = cookie
    elif type(cookie) is str:
        # 假设传入的已经是解码后的cookie字符串
        cookie_dict = cookies_str_to_dict(cookie)
    else:
        logger.error('cookie格式不正确')
        return False

    try:
        # 创建Request实例并测试cookie
        request_instance = Request(cookie=cookies_dict_to_str(cookie_dict))
        url = '/aweme/v1/web/user/profile/self/'
        params = {}
        
        user_info = request_instance.getJSON(url, params)
        
        # 检查返回结果
        if user_info and 'user' in user_info and user_info['user']:
            logger.success('cookie已登录')
            return True
        else:
            logger.error('cookie未登录或无效')
            return False
            
    except Exception as e:
        logger.error(f'测试cookie时发生错误: {e}')
        return False


def cookies_str_to_dict(cookie_string: str) -> dict:
    """将cookie字符串转换为字典（假设传入的是已解码的cookie字符串）"""
    if not cookie_string:
        return {}
    
    cookies = cookie_string.strip().split('; ')
    cookie_dict = {}
    for cookie in cookies:
        if cookie == '' or cookie == 'douyin.com':
            continue
        if '=' not in cookie:
            continue
        key, value = cookie.split('=', 1)
        cookie_dict[key] = value
    return cookie_dict


def cookies_dict_to_str(cookie_string: dict) -> str:
    return '; '.join([f'{key}={value}' for key, value in cookie_string.items()])


# if __name__ == "__main__":
    # save_json('edge_cookie', get_cookie_dict())
    # save_json('dict_cookie', cookies_to_dict(x))
