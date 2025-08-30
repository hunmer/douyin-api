from flask import Blueprint, request, jsonify
from loguru import logger
import json
import base64
from utils.account_manager import AccountManager
from utils.cookies import test_cookie

account_bp = Blueprint('account', __name__)


def _parse_request_data():
    """安全解析请求数据，处理各种数据格式"""
    try:
        # 首先尝试标准的JSON解析
        data = request.get_json()
        if data is not None:
            # 确保返回的是字典类型
            if isinstance(data, dict):
                return data, None
            else:
                return None, '请求数据必须是JSON对象格式'
        
        # 检查是否有form数据
        if request.form:
            form_data = request.form.to_dict()
            if form_data:
                return form_data, None
        
        # 如果没有JSON和form数据，尝试解析原始数据
        try:
            raw_data = request.get_data(as_text=True)
            if not raw_data:
                return None, '请求数据不能为空'
            
            # 尝试解析JSON字符串
            data = json.loads(raw_data)
            if isinstance(data, dict):
                return data, None
            else:
                return None, '请求数据必须是JSON对象格式'
                
        except json.JSONDecodeError as e:
            return None, f'JSON格式错误: {str(e)}'
        except Exception as e:
            return None, f'解析请求数据失败: {str(e)}'
            
    except Exception as e:
        return None, f'获取请求数据失败: {str(e)}'


@account_bp.route('/list', methods=['GET'])
def list_accounts():
    """获取所有账号列表"""
    try:
        manager = AccountManager.get_instance()
        accounts = manager.get_all_accounts()
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'accounts': accounts,
                'total': len(accounts)
            }
        })
    except Exception as e:
        logger.error(f"获取账号列表失败: {e}")
        return jsonify({
            'code': 1,
            'message': f'获取账号列表失败: {str(e)}',
            'data': None
        }), 500


def _add_or_update_account(is_update=False):
    """添加或更新账号的公共逻辑"""
    try:
        # 安全解析请求数据
        data, error_msg = _parse_request_data()
        if error_msg:
            return jsonify({
                'code': 1,
                'message': error_msg,
                'data': None
            }), 400
            
        if not data:
            return jsonify({
                'code': 1,
                'message': '请求数据不能为空',
                'data': None
            }), 400
        
        name = data.get('name', '').strip()
        cookie = data.get('cookie', '') if data.get('cookie') else ''
        description = data.get('description', '').strip() if data.get('description') else None
        test_login = data.get('testLogin', True)  # 默认测试登录状态
        cookie = cookie.strip() if cookie else ''
        
        # 只处理base64格式的cookie
        if cookie:
            try:
                # 直接尝试base64解码
                decoded_cookie = base64.b64decode(cookie).decode('utf-8')
                logger.info("Cookie已从base64解码")
            except Exception as e:
                return jsonify({
                    'code': 1,
                    'message': 'Cookie必须是base64格式',
                    'data': None
                }), 400
        else:
            decoded_cookie = ''
        
        if not name:
            # 如果有cookie但没有name，给出更详细的提示
            if cookie:
                return jsonify({
                    'code': 1,
                    'message': '账号名称不能为空。请提供账号名称，例如：{"name": "我的账号", "cookie": "your_cookie_here"}',
                    'data': None
                }), 400
            else:
                return jsonify({
                    'code': 1,
                    'message': '账号名称不能为空',
                    'data': None
                }), 400
        
        # 如果是添加操作，cookie不能为空
        if not is_update and not cookie:
            return jsonify({
                'code': 1,
                'message': 'Cookie不能为空',
                'data': None
            }), 400
        
        # 测试cookie是否有效（如果提供了cookie）
        if cookie and test_login:
            # 使用解码后的cookie进行测试
            if not test_cookie(decoded_cookie):
                return jsonify({
                    'code': 1,
                    'message': 'Cookie无效或未登录',
                    'data': None
                }), 400
        
        manager = AccountManager.get_instance()
        
        if is_update:
            # 更新时保存原始base64格式cookie
            success = manager.update_account(name, cookie, description)
            action = '更新'
        else:
            # 添加时保存原始base64格式cookie
            success = manager.add_account(name, cookie, description)
            action = '添加'
        
        if success:
            return jsonify({
                'code': 0,
                'message': f'{action}账号成功',
                'data': {'name': name}
            })
        else:
            if is_update:
                return jsonify({
                    'code': 1,
                    'message': '账号不存在',
                    'data': None
                }), 404
            else:
                return jsonify({
                    'code': 1,
                    'message': '账号名称已存在',
                    'data': None
                }), 400
    
    except Exception as e:
        logger.error(f"{'更新' if is_update else '添加'}账号失败: {e}")
        return jsonify({
            'code': 1,
            'message': f"{'更新' if is_update else '添加'}账号失败: {str(e)}",
            'data': None
        }), 500


@account_bp.route('/add', methods=['POST'])
def add_account():
    """添加新账号"""
    return _add_or_update_account(is_update=False)


@account_bp.route('/update', methods=['POST'])
def update_account():
    """更新账号信息"""
    return _add_or_update_account(is_update=True)


@account_bp.route('/delete', methods=['POST'])
def delete_account():
    """删除账号"""
    try:
        # 安全解析请求数据
        data, error_msg = _parse_request_data()
        if error_msg:
            return jsonify({
                'code': 1,
                'message': error_msg,
                'data': None
            }), 400
            
        if not data:
            return jsonify({
                'code': 1,
                'message': '请求数据不能为空',
                'data': None
            }), 400
        
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({
                'code': 1,
                'message': '账号名称不能为空',
                'data': None
            }), 400
        
        manager = AccountManager.get_instance()
        success = manager.delete_account(name)
        
        if success:
            return jsonify({
                'code': 0,
                'message': '删除账号成功',
                'data': {'name': name}
            })
        else:
            return jsonify({
                'code': 1,
                'message': '账号不存在',
                'data': None
            }), 404
    
    except Exception as e:
        logger.error(f"删除账号失败: {e}")
        return jsonify({
            'code': 1,
            'message': f'删除账号失败: {str(e)}',
            'data': None
        }), 500


@account_bp.route('/test', methods=['POST'])
def test_account_cookie():
    """测试账号cookie是否有效"""
    try:
        # 安全解析请求数据
        data, error_msg = _parse_request_data()
        if error_msg:
            return jsonify({
                'code': 1,
                'message': error_msg,
                'data': None
            }), 400
            
        if not data:
            return jsonify({
                'code': 1,
                'message': '请求数据不能为空',
                'data': None
            }), 400
        
        name = data.get('name', '').strip()
        cookie = data.get('cookie', '') if data.get('cookie') else ''
        cookie = cookie.strip() if cookie else ''
        
        if name:
            # 通过账号名获取cookie
            manager = AccountManager.get_instance()
            account = manager.get_account_by_name(name)
            if not account:
                return jsonify({
                    'code': 1,
                    'message': '账号不存在',
                    'data': None
                }), 404
            # 从存储中获取base64格式的cookie并解码
            stored_cookie = account['cookie']
            try:
                decoded_cookie = base64.b64decode(stored_cookie).decode('utf-8')
            except Exception:
                return jsonify({
                    'code': 1,
                    'message': '存储的cookie格式错误',
                    'data': None
                }), 500
        elif cookie:
            # 直接提供的cookie，尝试base64解码
            try:
                decoded_cookie = base64.b64decode(cookie).decode('utf-8')
            except Exception:
                return jsonify({
                    'code': 1,
                    'message': 'Cookie必须是base64格式',
                    'data': None
                }), 400
        else:
            return jsonify({
                'code': 1,
                'message': '请提供账号名称或cookie',
                'data': None
            }), 400
        
        # 使用解码后的cookie进行测试
        is_valid = test_cookie(decoded_cookie)
        
        return jsonify({
            'code': 0,
            'message': 'Cookie测试完成',
            'data': {
                'valid': is_valid,
                'status': '已登录' if is_valid else '未登录'
            }
        })
    
    except Exception as e:
        logger.error(f"测试cookie失败: {e}")
        return jsonify({
            'code': 1,
            'message': f'测试cookie失败: {str(e)}',
            'data': None
        }), 500


@account_bp.route('/get-cookie', methods=['POST'])
def get_cookie():
    """获取可用的cookie"""
    try:
        # 安全解析请求数据（可选参数，允许为空）
        data, error_msg = _parse_request_data()
        if error_msg:
            # 对于get-cookie接口，如果解析失败，使用空字典作为默认值
            data = {}
        
        if not data:
            data = {}
            
        name = data.get('name', '').strip() if data.get('name') else None
        
        manager = AccountManager.get_instance()
        cookie = manager.get_cookie(name)
        
        if cookie:
            return jsonify({
                'code': 0,
                'message': '获取cookie成功',
                'data': {
                    'cookie': cookie,
                    'account': name or '自动选择'
                }
            })
        else:
            return jsonify({
                'code': 1,
                'message': '没有可用的账号',
                'data': None
            }), 404
    
    except Exception as e:
        logger.error(f"获取cookie失败: {e}")
        return jsonify({
            'code': 1,
            'message': f'获取cookie失败: {str(e)}',
            'data': None
        }), 500
