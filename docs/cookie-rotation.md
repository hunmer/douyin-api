# Cookie轮换功能说明

## 概述

现在Request类支持自动轮换cookie功能，可以让每个API请求使用不同的账号cookie，有效分散请求压力，避免单个账号被限制。

## 功能特点

1. **自动轮换**: 每次请求自动选择最近最少使用的账号cookie
2. **向后兼容**: 不影响现有代码的使用方式
3. **灵活控制**: 可以选择是否启用轮换功能
4. **智能选择**: 基于账号管理器的LRU(最近最少使用)策略

## 使用方法

### 方法1: 构造函数参数

```python
from utils.request import Request

# 启用cookie轮换
request = Request(use_rotating_cookies=True)

# 每次请求都会使用不同的cookie（如果有多个账号）
result1 = request.getJSON('/aweme/v1/web/general/search/single/', {})
result2 = request.getJSON('/aweme/v1/web/aweme/post/', {})  # 使用不同的cookie
```

### 方法2: 类方法（推荐）

```python
from utils.request import Request

# 使用类方法创建轮换cookie实例
request = Request.with_rotating_cookies()

# 使用方式相同
result = request.getJSON('/aweme/v1/web/general/search/single/', {})
```

### 方法3: 传统用法（固定cookie）

```python
from utils.request import Request

# 默认行为不变，使用固定cookie
request = Request()

# 或者明确指定特定cookie
request = Request(cookie='your_base64_cookie')
```

## 配置要求

要使用cookie轮换功能，需要：

1. **配置多个账号**: 在账号管理器中添加多个有效的douyin账号
2. **账号格式**: 每个账号的cookie需要是base64编码的格式
3. **数据文件**: 确保`data/cookies.json`文件存在且包含有效账号信息

### 添加账号示例

```python
from utils.account_manager import AccountManager

# 获取账号管理器实例
manager = AccountManager.get_instance()

# 添加账号（cookie需要base64编码）
manager.add_account('account1', 'base64_encoded_cookie_1', '账号1描述')
manager.add_account('account2', 'base64_encoded_cookie_2', '账号2描述')
manager.add_account('account3', 'base64_encoded_cookie_3', '账号3描述')
```

## 工作原理

1. **首次请求**: 选择`lastUsed`时间最早的账号cookie
2. **后续请求**: 每次都重新选择最近最少使用的账号
3. **使用记录**: 每次使用后会更新该账号的`lastUsed`时间戳
4. **负载均衡**: 自动在多个账号间均匀分配请求

## 注意事项

1. **兼容性**: 如果指定了具体cookie，轮换功能会被自动禁用
2. **单账号**: 如果只有一个账号或没有账号，轮换相当于没有启用
3. **性能**: 每次请求会有轻微的cookie选择开销，但对性能影响很小
4. **日志**: 轮换过程会在debug级别记录日志，便于调试

## 适用场景

- **高频请求**: 需要进行大量API调用的场景
- **数据采集**: 爬虫或数据抓取应用
- **负载分散**: 避免单个账号请求过于集中
- **风控规避**: 降低被平台识别为异常请求的风险

## 升级指南

现有代码无需修改即可继续使用，如需启用轮换功能：

```python
# 旧代码
request = Request()

# 新代码（启用轮换）
request = Request.with_rotating_cookies()
# 或
request = Request(use_rotating_cookies=True)
```
