import argparse
import os
from flask import Flask
from api import api as api_blueprint
from api.account_api import account_bp
from api.following_videos_routes import following_videos_bp
from flask_cors import CORS
from utils.account_manager import AccountManager

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/aweme/v1/web')
app.register_blueprint(account_bp, url_prefix='/api/v1/account')
app.register_blueprint(following_videos_bp)  # 注册关注用户视频管理蓝图

CORS(app, origins='*', supports_credentials=True)  # 解决跨域问题


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Douyin API Server')
    parser.add_argument('--data-path', type=str, default='data',
                       help='Data directory path for storing cookies and other data')
    args = parser.parse_args()

    # 初始化账号管理器
    AccountManager.initialize(args.data_path)

    print("🚀 Douyin API 服务已启动")
    print("📍 服务地址: http://localhost:3010")
    print("✨ 新功能: 关注用户视频管理")

    app.run(host='0.0.0.0', port=3010)
