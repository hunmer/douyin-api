#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Cookie轮换功能测试脚本
用于验证轮换cookie功能是否正常工作
"""

import time
from utils.request import Request
from utils.request_manager import RequestManager
from utils.account_manager import AccountManager


def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 测试传统用法
    print("1. 测试传统用法（固定cookie）")
    req1 = Request()
    webid1 = req1.get_webid()
    print(f"   Webid: {webid1}")
    
    # 测试轮换cookie用法
    print("2. 测试轮换cookie用法")
    req2 = Request.with_rotating_cookies()
    webid2 = req2.get_webid()
    print(f"   Webid: {webid2}")
    
    # 测试RequestManager
    print("3. 测试RequestManager")
    req3 = RequestManager.get_rotating_request()
    webid3 = req3.get_webid()
    print(f"   Webid: {webid3}")


def test_cookie_rotation():
    """测试cookie轮换"""
    print("\n=== 测试cookie轮换 ===")
    
    # 检查账号管理器中的账号数量
    try:
        manager = AccountManager.get_instance()
        accounts = manager.get_all_accounts()
        print(f"当前配置的账号数量: {len(accounts)}")
        
        if len(accounts) == 0:
            print("⚠️  警告: 没有配置任何账号，轮换功能无法测试")
            print("请使用账号管理器添加账号后再测试")
            return
        elif len(accounts) == 1:
            print("⚠️  警告: 只有1个账号，轮换效果不明显")
        
        # 显示账号信息
        for i, account in enumerate(accounts):
            print(f"  账号{i+1}: {account['name']} (最后使用: {account['lastUsed']})")
            
    except Exception as e:
        print(f"获取账号信息失败: {e}")
        return
    
    # 测试多次请求
    print("\n执行多次请求测试轮换效果:")
    req = Request.with_rotating_cookies()
    
    for i in range(3):
        print(f"\n第{i+1}次请求:")
        start_time = time.time()
        
        # 这里模拟一个简单的API调用
        try:
            webid = req.get_webid()
            print(f"  Webid: {webid}")
            print(f"  用时: {time.time() - start_time:.2f}秒")
        except Exception as e:
            print(f"  请求失败: {e}")
        
        time.sleep(1)  # 间隔1秒


def test_performance_comparison():
    """测试性能对比"""
    print("\n=== 性能对比测试 ===")
    
    print("1. 固定cookie性能测试")
    req_fixed = Request()
    start = time.time()
    for i in range(5):
        req_fixed.get_webid()
    fixed_time = time.time() - start
    print(f"   固定cookie 5次调用用时: {fixed_time:.3f}秒")
    
    print("2. 轮换cookie性能测试")
    req_rotating = Request.with_rotating_cookies()
    start = time.time()
    for i in range(5):
        req_rotating.get_webid()
    rotating_time = time.time() - start
    print(f"   轮换cookie 5次调用用时: {rotating_time:.3f}秒")
    
    print(f"3. 性能差异: {((rotating_time - fixed_time) / fixed_time * 100):.1f}%")


def main():
    """主函数"""
    print("Cookie轮换功能测试")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_cookie_rotation()
        test_performance_comparison()
        
        print("\n=== 测试完成 ===")
        print("如果要使用轮换功能，请确保:")
        print("1. 账号管理器中配置了多个有效账号")
        print("2. 账号的cookie是base64编码格式")
        print("3. 使用 Request.with_rotating_cookies() 或 use_rotating_cookies=True")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
