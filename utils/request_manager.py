"""
请求实例管理器，为不同API提供请求实例
支持多账号管理
"""

from utils.request import Request
from typing import Dict, Optional


class RequestManager:
    """请求管理器，管理不同账号的请求实例"""
    
    _instances: Dict[str, Request] = {}
    
    @classmethod
    def get_request(cls, cookie: str = '', UA: str = '', use_rotating_cookies: bool = False) -> Request:
        """获取请求实例
        
        Args:
            cookie: 直接提供的cookie字符串
            UA: User Agent字符串
            use_rotating_cookies: 是否使用轮换cookie
            
        Returns:
            Request实例
        """
        # 生成实例键
        key = f"{hash(cookie)}_{hash(UA)}_{use_rotating_cookies}"
        
        # 如果实例不存在，创建新实例
        if key not in cls._instances:
            cls._instances[key] = Request(cookie=cookie, UA=UA, use_rotating_cookies=use_rotating_cookies)
        
        return cls._instances[key]
    
    @classmethod
    def get_rotating_request(cls, UA: str = '') -> Request:
        """获取启用cookie轮换的请求实例
        
        Args:
            UA: User Agent字符串
            
        Returns:
            启用cookie轮换的Request实例
        """
        return cls.get_request(cookie='', UA=UA, use_rotating_cookies=True)
    
    @classmethod
    def clear_instances(cls):
        """清理所有实例"""
        cls._instances.clear()
    
    @classmethod
    def get_default_request(cls) -> Request:
        """获取默认请求实例（保持向后兼容）"""
        return cls.get_request()


# 延迟创建全局默认实例（保持向后兼容）
def get_default_request():
    """获取默认请求实例（保持向后兼容）"""
    return RequestManager.get_default_request()

# 避免在导入时创建实例，改为函数调用
# default_request = RequestManager.get_default_request()
