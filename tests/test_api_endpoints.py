"""
测试账号管理API的脚本
"""

import requests
import json

BASE_URL = "http://127.0.0.1:3010/api/v1/account"

def test_api():
    print("=== 测试账号管理API ===")
    
    # 1. 测试添加账号
    print("\n1. 测试添加账号")
    add_data = {
        "name": "test1",
        "cookie": "test_cookie_123",
        "description": "测试账号1",
        "testLogin": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/add", 
                               headers={"Content-Type": "application/json"},
                               json=add_data)
        print(f"添加账号响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"添加账号失败: {e}")
    
    # 2. 测试获取账号列表
    print("\n2. 测试获取账号列表")
    try:
        response = requests.get(f"{BASE_URL}/list")
        print(f"获取列表响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"获取列表失败: {e}")
    
    # 3. 测试更新账号（使用POST）
    print("\n3. 测试更新账号")
    update_data = {
        "name": "test1",
        "description": "更新后的测试账号1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/update",
                               headers={"Content-Type": "application/json"},
                               json=update_data)
        print(f"更新账号响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"更新账号失败: {e}")
    
    # 4. 测试删除账号（使用DELETE）
    print("\n4. 测试删除账号（DELETE方法）")
    delete_data = {
        "name": "test1"
    }
    
    try:
        response = requests.delete(f"{BASE_URL}/delete",
                                 headers={"Content-Type": "application/json"},
                                 json=delete_data)
        print(f"删除账号响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"删除账号失败: {e}")
    
    # 5. 再次添加并用POST方法删除
    print("\n5. 测试POST方法删除")
    # 先添加
    requests.post(f"{BASE_URL}/add", 
                 headers={"Content-Type": "application/json"},
                 json=add_data)
    
    # 再用POST删除
    try:
        response = requests.post(f"{BASE_URL}/delete",
                               headers={"Content-Type": "application/json"},
                               json=delete_data)
        print(f"POST删除账号响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"POST删除账号失败: {e}")


if __name__ == "__main__":
    test_api()
