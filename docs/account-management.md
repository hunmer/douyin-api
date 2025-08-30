# 多账号Cookie管理功能

## 功能概述

该功能实现了多账号cookie管理，支持：
- 通过命令行参数指定数据目录
- 管理多个douyin账号的cookies
- 根据使用频率自动选择账号
- 提供HTTP API接口进行账号管理

## 启动参数

```bash
python app.py --data-path /path/to/data
```

- `--data-path`: 数据目录路径，默认为 `data`
- 程序会在该目录下创建 `cookies.json` 文件来存储账号信息

## 数据格式

cookies.json 文件格式：
```json
[
  {
    "name": "账号1",
    "cookie": "cookie字符串",
    "description": "账号描述",
    "lastUsed": 1693420800,
    "createTime": 1693420800,
    "updateTime": 1693420800
  },
  {
    "name": "账号2", 
    "cookie": "cookie字符串",
    "description": "账号描述",
    "lastUsed": 0,
    "createTime": 1693420800,
    "updateTime": 1693420800
  }
]
```

## HTTP API 接口

### 1. 获取账号列表
```
GET /api/v1/account/list
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "accounts": [
      {
        "name": "账号1",
        "description": "账号描述",
        "lastUsed": 1693420800,
        "createTime": 1693420800,
        "updateTime": 1693420800
      }
    ],
    "total": 1
  }
}
```

### 2. 添加账号
```
POST /api/v1/account/add
Content-Type: application/json

{
  "name": "账号名称",
  "cookie": "cookie字符串",
  "description": "账号描述（可选）",
  "testLogin": true
}
```

### 3. 更新账号
```
POST /api/v1/account/update
Content-Type: application/json

{
  "name": "账号名称",
  "cookie": "新cookie字符串（可选）",
  "description": "新描述（可选）",
  "testLogin": true
}
```

### 4. 删除账号
支持DELETE和POST两种方法：
```
DELETE /api/v1/account/delete
Content-Type: application/json

{
  "name": "账号名称"
}
```
或者
```
POST /api/v1/account/delete
Content-Type: application/json

{
  "name": "账号名称"
}
```

### 5. 测试账号Cookie
```
POST /api/v1/account/test
Content-Type: application/json

{
  "name": "账号名称"
}
// 或者
{
  "cookie": "cookie字符串"
}
```

### 6. 获取可用Cookie
```
POST /api/v1/account/get-cookie
Content-Type: application/json

{
  "name": "账号名称（可选）"
}
```

如果不指定name，系统会自动选择最近最少使用的账号。

## 账号选择策略

- 如果指定了账号名称，使用指定账号
- 如果没有指定账号名称，自动选择 `lastUsed` 时间戳最小的账号（最近最少使用）
- 每次使用账号后，会更新该账号的 `lastUsed` 时间戳

## 兼容性

- 保持与原有 `get_cookie_dict()` 函数的兼容性
- 如果没有配置账号管理器，会回退到原有的cookie读取方式
- 支持传统的 config/cookie.json 和 config/cookie.txt 文件

## 使用示例

### 1. 启动服务器
```bash
python app.py --data-path ./my_data
```

### 2. 添加账号
```bash
curl -X POST http://localhost:3010/api/v1/account/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_account",
    "cookie": "your_cookie_here",
    "description": "测试账号"
  }'
```

### 3. 在代码中使用
```python
from utils.cookies import get_cookie_dict

# 获取指定账号的cookie
cookie_dict = get_cookie_dict(name="test_account")

# 获取自动选择的账号cookie
cookie_dict = get_cookie_dict()
```
