import argparse
import os
from flask import Flask
from api import api as api_blueprint
from api.account_api import account_bp
from flask_cors import CORS
from utils.account_manager import AccountManager

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/aweme/v1/web')
app.register_blueprint(account_bp, url_prefix='/api/v1/account')

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
    
    app.run(host='0.0.0.0', port=3010)
