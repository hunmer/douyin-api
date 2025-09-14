from . import api
from utils.request import Request
from utils.account_manager import AccountManager
from flask import request, jsonify

"""
@desc: 通过房间id获取获取直播的推流
@param: room_id
@url: https://live.douyin.com/webcast/room/info_by_scene/
"""

# 延迟初始化，避免启动时的重复日志输出
def get_request_instance():
    """获取Request实例，延迟初始化"""
    if not hasattr(get_request_instance, '_instance'):
        get_request_instance._instance = Request()
    return get_request_instance._instance

def get_request_instance_for_account(account_name: str = None):
    """根据账号名获取Request实例"""
    account_manager = AccountManager.get_instance()
    cookie = account_manager.get_cookie(account_name)

    if cookie:
        # 使用指定账号的cookie创建Request实例
        return Request(cookie=cookie)
    else:
        # 回退到默认实例
        return get_request_instance()

# 为了保持向后兼容，创建一个属性访问器
class RequestProxy:
    def __getattr__(self, name):
        # 检查是否有user_account参数
        user_account = request.args.get('user_account') if request else None
        if user_account:
            # 使用指定账号的Request实例
            instance = get_request_instance_for_account(user_account)
        else:
            # 使用默认实例
            instance = get_request_instance()
        return getattr(instance, name)

request_instance = RequestProxy()


@api.route('/webcast/room/info_by_scene/')
def get_live_info_by_scene():
    room_id = request.args.get('room_id')
    if not room_id:
        return jsonify({'error': 'Missing room_id parameter'}), 400
    url = '/webcast/room/info_by_scene/'
    params = {
        'room_id': room_id,
        'live_id': '1',
        'scene': 'aweme_video_feed_pc',
        'region': 'cn'
    }
    aweme_detail = request_instance.getJSON(url, params, live=1)  # 直接调用 getJSON 方法
    if aweme_detail:
        return jsonify(aweme_detail)
    else:
        api.logger.error('Failed to retrieve aweme detail for aweme_id: %s', room_id)
        return jsonify({'error': 'Failed to retrieve aweme detail; Check you Cookie!'}), 404
