# -*- encoding: utf-8 -*-
"""
轮换Cookie使用示例
展示如何使用Request类的轮换cookie功能
"""

from utils.request import Request


def example_basic_usage():
    """基本用法示例 - 每个请求使用固定cookie（原有行为）"""
    print("=== 基本用法（固定cookie） ===")
    
    # 创建普通Request实例，使用固定cookie
    request = Request()
    
    # 多次请求会使用同一个cookie
    for i in range(3):
        webid = request.get_webid()
        print(f"第{i+1}次请求 webid: {webid}")


def example_rotating_cookies():
    """轮换cookie用法示例 - 每个请求使用不同cookie"""
    print("\n=== 轮换cookie用法 ===")
    
    # 方法1: 使用构造函数参数
    request = Request(use_rotating_cookies=True)
    
    # 方法2: 使用类方法（推荐）
    # request = Request.with_rotating_cookies()
    
    # 多次请求会使用不同的cookie
    for i in range(3):
        # 每次getJSON调用都会轮换到新的cookie（如果有多个可用账号）
        params = {}
        result = request.getJSON('/aweme/v1/web/general/search/single/', params)
        print(f"第{i+1}次请求使用了新的cookie，结果: {type(result)}")


def example_with_specific_cookie():
    """指定cookie的示例 - 不会轮换"""
    print("\n=== 指定特定cookie（不轮换） ===")
    
    # 如果指定了特定的cookie，即使启用轮换也不会改变
    specific_cookie = "your_base64_encoded_cookie_here"
    request = Request(cookie=specific_cookie, use_rotating_cookies=True)
    
    for i in range(3):
        webid = request.get_webid()
        print(f"第{i+1}次请求 webid: {webid} (使用固定cookie)")


if __name__ == "__main__":
    # 运行示例
    example_basic_usage()
    example_rotating_cookies()
    example_with_specific_cookie()
    
    print("\n=== 注意事项 ===")
    print("1. 轮换cookie需要在账号管理器中配置多个有效账号")
    print("2. 如果只有一个账号或没有账号，轮换功能相当于没有启用")
    print("3. 如果指定了具体的cookie，轮换功能会被忽略")
    print("4. 轮换功能主要用于分散请求，避免单个账号请求过于频繁")
