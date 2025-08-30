
# Douyin API

## 简介
本项目提供了用于获取抖音平台用户及视频信息的API接口，方便开发者获取用户作品、收藏、喜欢、观看历史等数据。

**✨ 新功能：多账号管理**
- 支持管理多个抖音账号的cookies
- 自动选择最少使用的账号以均衡负载
- 提供HTTP API接口进行账号管理
- 支持指定账号进行API调用

## 安装依赖
请先确保你的环境已经安装了 `pip`，然后运行以下命令安装本项目所需的所有依赖项：

```shell
pip install -r requirements.txt
```

## 启动服务

### 基本启动
```shell
python app.py
```

### 指定数据目录
```shell
python app.py --data-path /path/to/your/data
```

- `--data-path`: 指定数据目录路径，用于存储cookies和其他数据文件，默认为 `data`

## 多账号管理

### 添加账号
```bash
curl -X POST http://localhost:3010/api/v1/account/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_account",
    "cookie": "your_cookie_string_here",
    "description": "我的抖音账号"
  }'
```

### 获取账号列表
```bash
curl http://localhost:3010/api/v1/account/list
```

### 在API调用中指定账号
```bash
curl "http://localhost:3010/aweme/v1/web/user/info?account_name=my_account&..."
```

详细的多账号管理文档请查看：[多账号管理文档](./docs/account-management.md)

## 接口文档
详细的接口文档已在 `docs` 文件夹中提供：

- [用户信息接口文档](./docs/user-api.md)
- [视频接口文档](./docs/video-api.md)
- [多账号管理文档](./docs/account-management.md)

## 使用方法

### 传统方式（向后兼容）
第一次运行会提示输入cookie，请从douyin网页复制cookie后输入。

### 推荐方式（多账号管理）
1. 启动服务：`python app.py --data-path ./my_data`
2. 通过API添加账号（见上面的示例）
3. 系统会自动选择可用的账号进行API调用

## 文件结构
```text
├── README.md         # 项目简介及使用说明
├── requirements.txt  # 项目依赖文件
├── docs              # 文档目录
│   ├── user-api.md   # 用户信息相关接口文档
│   └── video-api.md  # 视频相关接口文档
├── api               # 接口文件目录
│   └── ...           # 接口相关代码文件
├── utils             # 工具类目录
│   └── ...           # 工具类函数代码
├── tests             # 测试目录
│   └── ...           # 测试代码
├── config            # 配置文件目录
│   └── cookie.json   # 存储cookie的配置文件
├── app.py            # 启动文件

```

## 贡献
欢迎提交问题或贡献代码。