from . import api
from utils.request import Request
from utils.account_manager import AccountManager
from flask import request, jsonify

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

'''
@desc: 推荐页视频流
@url: /aweme/v1/web/tab/feed/
@param:
'''


@api.route('/tab/feed/')
def get_recommend():
    count = request.args.get('count')
    url = '/aweme/v1/web/tab/feed/'
    params = {
        'tag_id': '',
        'share_aweme_id': '',
        'live_insert_type': '',
        'count': count,
        'refresh_index': '2',
        'video_type_select': '1',
        'aweme_pc_rec_raw_data': '{"is_client":false,"ff_danmaku_status":1,"danmaku_switch_status":1,"is_auto_play":0,"is_full_screen":0,"is_full_webscreen":0,"is_mute":0,"is_speed":1,"is_visible":1,"related_recommend":1}'
    }
    recommend_list = request_instance.getJSON(url, params)
    if recommend_list:
        return jsonify(recommend_list)
    else:
        return jsonify({'error': 'Failed to retrieve recommend_list; Check you Cookie and Referer!'}), 403
