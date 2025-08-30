"""
使用示例：在API中使用多账号功能
"""

from flask import request
from utils.request_manager import RequestManager


def get_user_info_with_account():
    """用户信息API示例 - 支持指定账号"""
    
    # 从请求中获取账号名（可选）
    account_name = request.args.get('account_name')
    
    # 获取对应账号的请求实例
    req = RequestManager.get_request(account_name=account_name)
    
    # 使用该实例进行API调用
    # ... API逻辑
    
    return {"message": f"使用账号: {account_name or '自动选择'}"}


def get_video_info_with_account():
    """视频信息API示例 - 支持指定账号"""
    
    data = request.get_json() or {}
    account_name = data.get('account_name')
    
    # 获取对应账号的请求实例  
    req = RequestManager.get_request(account_name=account_name)
    
    # 使用该实例进行API调用
    # ... API逻辑
    
    return {"message": f"使用账号: {account_name or '自动选择'}"}


# 向后兼容的使用方式
def traditional_usage():
    """传统使用方式仍然有效"""
    from utils.request import Request
    
    # 传统方式：直接创建Request实例
    req = Request()
    
    # 新方式：通过管理器获取（推荐）
    req = RequestManager.get_default_request()
    
    return req
