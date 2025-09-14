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
@desc: 底部栏推荐词
@url: aweme/v1/web/seo/inner/link/
'''


@api.route('/seo/inner/link/')
def get_seo_link():
    url = '/aweme/v1/web/seo/inner/link/'
    params = {
        'channel': 'channel_pc_web'
    }
    seo_link = request_instance.getJSON(url, params)
    if seo_link:
        return jsonify(seo_link)
    else:
        return jsonify({'error': 'Failed to retrieve seo_link; Check you Cookie and Referer!'}), 403


'''
@desc: 获取表情列表
@url： '/aweme/v1/web/emoji/list'
'''


@api.route('/emoji/list/')
def get_emoji_list():
    url = '/aweme/v1/web/emoji/list'
    params = {
        'channel': 'channel_pc_web'
    }
    emoji_list = request_instance.getJSON(url, params)
    if emoji_list:
        return jsonify(emoji_list)
    else:
        return jsonify({'error': 'Failed to retrieve emoji_list; Check you Cookie and Referer!'}), 403


'''
@desc: 自定义的表情或者收藏的
@url: /aweme/v1/web/im/resources/emoticon/trending
'''


@api.route('/im/resources/emoticon/trending')
def get_emoticon_list():
    url = '/aweme/v1/web/im/resources/emoticon/trending'
    cursor = request.args.get('cursor')
    count = request.args.get('count')
    params = {
        'cursor': cursor,
        'count': count
    }
    emoticon_list = request_instance.getJSON(url, params)
    if emoticon_list:
        return jsonify(emoticon_list)
    else:
        return jsonify({'error': 'Failed to retrieve emoticon_list; Check you Cookie and Referer!'}), 403


'''
@desc: 搜索框热搜列表
@url: /aweme/v1/web/hot/search/list/
'''


@api.route('hot/search/list/')
def get_hot_list():
    url = '/aweme/v1/web/hot/search/list/'
    cursor = request.args.get('cursor')
    count = request.args.get('count')
    params = {
    }
    hot_list = request_instance.getJSON(url, params)
    if hot_list:
        return jsonify(hot_list)
    else:
        return jsonify({'error': 'Failed to retrieve emoticon_list; Check you Cookie and Referer!'}), 403


'''
@desc: 精选页标签
@url： /aweme/v1/web/home/channel/setting/
'''
@api.route('/home/channel/setting/')
def get_channel_setting():
    url = '/aweme/v1/web/home/channel/setting/'
    params = {
        'channel': 'channel_pc_web'
    }
    channel_setting = request_instance.getJSON(url, params)
    if channel_setting:
        return jsonify(channel_setting)
    else:
        return jsonify({'error': 'Failed to retrieve channel_setting; Check you Cookie and Referer!'}), 403