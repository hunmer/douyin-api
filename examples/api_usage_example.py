"""
使用示例：在API中使用多账号功能和cookie轮换
"""

from flask import request
from utils.request_manager import RequestManager


def get_user_info_with_rotating_cookies():
    """用户信息API示例 - 使用轮换cookie"""
    
    # 获取启用cookie轮换的请求实例
    req = RequestManager.get_rotating_request()
    
    # 使用该实例进行API调用，每次请求都会使用不同的cookie
    # ... API逻辑
    
    return {"message": "使用轮换cookie的账号"}


def get_user_info_with_account():
    """用户信息API示例 - 使用自动选择的账号（传统方式）"""
    
    # 获取自动选择的请求实例（使用固定账号）
    req = RequestManager.get_request()
    
    # 使用该实例进行API调用
    # ... API逻辑
    
    return {"message": "使用固定账号"}


def get_video_info_with_account():
    """视频信息API示例 - 使用自动选择的账号"""
    
    # 获取自动选择的请求实例（使用最近未使用的账号）
    req = RequestManager.get_request()
    
    # 使用该实例进行API调用
    # ... API逻辑
    
    return {"message": "使用自动选择的账号"}


def high_frequency_requests():
    """高频请求示例 - 推荐使用轮换cookie"""
    
    # 对于需要大量请求的场景，推荐使用轮换cookie
    req = RequestManager.get_rotating_request()
    
    results = []
    for i in range(10):
        # 每次循环都会使用不同的cookie（如果有多个账号）
        result = req.getJSON('/aweme/v1/web/general/search/single/', {'keyword': f'test{i}'})
        results.append(result)
    
    return {"message": "完成高频请求", "count": len(results)}


# 向后兼容的使用方式
def traditional_usage():
    """传统使用方式仍然有效"""
    from utils.request import Request
    
    # 传统方式：直接创建Request实例
    req = Request()
    
    # 新方式1：通过管理器获取（固定cookie）
    req = RequestManager.get_default_request()
    
    # 新方式2：通过管理器获取（轮换cookie）
    req = RequestManager.get_rotating_request()
    
    # 新方式3：直接使用Request类方法
    req = Request.with_rotating_cookies()
    
    return req
