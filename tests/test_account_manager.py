"""
多账号管理功能测试脚本
"""

import os
import sys
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.account_manager import AccountManager
from utils.cookies import get_cookie_dict


def test_account_manager():
    """测试账号管理器功能"""
    print("=== 测试账号管理器 ===")
    
    # 初始化账号管理器
    manager = AccountManager.initialize("test_data")
    
    # 测试添加账号
    print("1. 测试添加账号")
    success = manager.add_account(
        name="test_account_1",
        cookie="sessionid=123456; uid=789; sid=abc",
        description="测试账号1"
    )
    print(f"添加账号1: {'成功' if success else '失败'}")
    
    success = manager.add_account(
        name="test_account_2", 
        cookie="sessionid=654321; uid=987; sid=def",
        description="测试账号2"
    )
    print(f"添加账号2: {'成功' if success else '失败'}")
    
    # 测试获取账号列表
    print("\n2. 测试获取账号列表")
    accounts = manager.get_all_accounts()
    for account in accounts:
        print(f"  - {account['name']}: {account['description']}")
    
    # 测试获取cookie（自动选择）
    print("\n3. 测试自动选择账号")
    cookie1 = manager.get_cookie()
    print(f"第一次获取cookie: {cookie1[:20]}...")
    
    time.sleep(1)  # 等待1秒确保时间戳不同
    
    cookie2 = manager.get_cookie()
    print(f"第二次获取cookie: {cookie2[:20]}...")
    
    # 测试指定账号获取cookie
    print("\n4. 测试指定账号获取cookie")
    cookie3 = manager.get_cookie("test_account_1")
    print(f"指定账号1的cookie: {cookie3[:20]}...")
    
    # 测试更新账号
    print("\n5. 测试更新账号")
    success = manager.update_account(
        name="test_account_1",
        description="更新后的测试账号1"
    )
    print(f"更新账号1: {'成功' if success else '失败'}")
    
    # 测试删除账号
    print("\n6. 测试删除账号")
    success = manager.delete_account("test_account_2")
    print(f"删除账号2: {'成功' if success else '失败'}")
    
    # 再次查看账号列表
    print("\n7. 更新后的账号列表")
    accounts = manager.get_all_accounts()
    for account in accounts:
        print(f"  - {account['name']}: {account['description']}")


def test_cookie_integration():
    """测试cookie集成功能"""
    print("\n=== 测试Cookie集成功能 ===")
    
    # 测试通过get_cookie_dict获取cookie
    print("1. 测试get_cookie_dict自动选择")
    cookie_dict = get_cookie_dict()
    print(f"获取到的cookie字典: {list(cookie_dict.keys())}")
    
    # 测试指定账号名
    print("\n2. 测试get_cookie_dict指定账号")
    cookie_dict = get_cookie_dict(name="test_account_1")
    if cookie_dict:
        print(f"指定账号的cookie字典: {list(cookie_dict.keys())}")
    else:
        print("未找到指定账号的cookie")


def cleanup():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    import shutil
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")
        print("已清理测试数据目录")


if __name__ == "__main__":
    try:
        test_account_manager()
        test_cookie_integration()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        cleanup()
