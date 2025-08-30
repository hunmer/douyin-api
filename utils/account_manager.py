import os
import time
import ujson as json
from typing import Dict, List, Optional
from loguru import logger
from utils.util import save_json


class AccountManager:
    """账号管理器，管理多个douyin账号的cookies"""
    
    _instance = None
    _data_path = None
    
    def __init__(self, data_path: str = 'data'):
        self.data_path = data_path
        self.cookies_file = os.path.join(data_path, 'cookies.json')
        self._ensure_data_dir()
        self._load_cookies()
    
    @classmethod
    def initialize(cls, data_path: str = 'data'):
        """初始化单例实例"""
        cls._instance = cls(data_path)
        cls._data_path = data_path
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'AccountManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(cls._data_path or 'data')
        return cls._instance
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(self.data_path, exist_ok=True)
    
    def _load_cookies(self):
        """从文件加载cookies数据"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
                logger.info(f"加载了 {len(self.accounts)} 个账号")
            except Exception as e:
                logger.error(f"加载cookies文件失败: {e}")
                self.accounts = []
        else:
            self.accounts = []
            self._save_cookies()
            logger.info("未找到cookies文件，创建空的账号列表")
    
    def _save_cookies(self):
        """保存cookies数据到文件"""
        try:
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=2)
            logger.info("账号数据保存成功")
        except Exception as e:
            logger.error(f"保存cookies文件失败: {e}")
    
    def add_account(self, name: str, cookie: str, description: str = '') -> bool:
        """添加新账号"""
        # 检查账号名是否已存在
        if self.get_account_by_name(name):
            logger.warning(f"账号名 '{name}' 已存在")
            return False
        
        account = {
            'name': name,
            'cookie': cookie,
            'description': description,
            'lastUsed': 0,  # 从未使用
            'createTime': int(time.time()),
            'updateTime': int(time.time())
        }
        
        self.accounts.append(account)
        self._save_cookies()
        logger.success(f"添加账号 '{name}' 成功")
        return True
    
    def update_account(self, name: str, cookie: str = None, description: str = None) -> bool:
        """更新账号信息"""
        account = self.get_account_by_name(name)
        if not account:
            logger.warning(f"账号 '{name}' 不存在")
            return False
        
        if cookie is not None:
            account['cookie'] = cookie
        if description is not None:
            account['description'] = description
        
        account['updateTime'] = int(time.time())
        self._save_cookies()
        logger.success(f"更新账号 '{name}' 成功")
        return True
    
    def delete_account(self, name: str) -> bool:
        """删除账号"""
        for i, account in enumerate(self.accounts):
            if account['name'] == name:
                del self.accounts[i]
                self._save_cookies()
                logger.success(f"删除账号 '{name}' 成功")
                return True
        
        logger.warning(f"账号 '{name}' 不存在")
        return False
    
    def get_account_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取账号"""
        for account in self.accounts:
            if account['name'] == name:
                return account
        return None
    
    def get_all_accounts(self) -> List[Dict]:
        """获取所有账号列表（不包含cookie详细信息）"""
        return [{
            'name': account['name'],
            'description': account.get('description', ''),
            'lastUsed': account['lastUsed'],
            'createTime': account['createTime'],
            'updateTime': account['updateTime']
        } for account in self.accounts]
    
    def get_cookie(self, name: str = None) -> Optional[str]:
        """获取cookie
        
        Args:
            name: 账号名称，如果不指定则使用最近最少使用的账号
            
        Returns:
            cookie字符串，如果没有可用账号则返回None
        """
        if not self.accounts:
            logger.warning("没有可用的账号")
            return None
        
        if name:
            # 指定账号名
            account = self.get_account_by_name(name)
            if not account:
                logger.warning(f"账号 '{name}' 不存在")
                return None
        else:
            # 选择最近最少使用的账号（lastUsed最小的）
            account = min(self.accounts, key=lambda x: x['lastUsed'])
            logger.info(f"自动选择账号: {account['name']}")
        
        # 更新使用时间
        account['lastUsed'] = int(time.time())
        self._save_cookies()
        
        return account['cookie']
    
    def get_cookie_dict(self, name: str = None) -> Optional[Dict]:
        """获取cookie字典格式
        
        Args:
            name: 账号名称，如果不指定则使用最近最少使用的账号
            
        Returns:
            cookie字典，如果没有可用账号则返回None
        """
        cookie_str = self.get_cookie(name)
        if not cookie_str:
            return None
        
        return self._cookies_str_to_dict(cookie_str)
    
    def _cookies_str_to_dict(self, cookie_string: str) -> dict:
        """将cookie字符串转换为字典"""
        cookies = cookie_string.strip().split('; ')
        cookie_dict = {}
        for cookie in cookies:
            if cookie == '' or cookie == 'douyin.com':
                continue
            try:
                key, value = cookie.split('=', 1)
                cookie_dict[key] = value
            except ValueError:
                logger.warning(f"无效的cookie格式: {cookie}")
                continue
        return cookie_dict
