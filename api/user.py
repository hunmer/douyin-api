from utils.request import Request
from utils.account_manager import AccountManager
from . import api
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
@desc: 获取用户个人的信息
@url: '/aweme/v1/web/user/profile/self/'
'''


@api.route('/user/profile/self/')
def get_user_info_self():
    url = '/aweme/v1/web/user/profile/self/'
    params = {

    }
    user_info = request_instance.getJSON(url, params)
    if user_info:
        return jsonify(user_info)
    else:
        return jsonify({'error': 'Failed to retrieve userinfo; Check you Cookie and Referer!'}), 403


"""
@desc: 获取其他用户信息
@url: /aweme/v1/web/user/profile/other/
"""


@api.route('/user/profile/other/')
def get_user_info():
    sec_user_id = request.args.get('sec_user_id')
    url = '/aweme/v1/web/user/profile/other/'
    params = {
        'sec_user_id': sec_user_id,
        'source': 'channel_pc_web',
        'publish_video_strategy_type': '2',
        'personal_center_strategy': '1'
    }
    user_info = request_instance.getJSON(url, params)
    if user_info:
        return jsonify(user_info)
    else:
        return jsonify({'error': 'Failed to retrieve userinfo; Check you Cookie and Referer!'}), 403


"""
@desc: 获取用户作品列表
@url：/aweme/v1/web/aweme/post/
@param: forward_end_cursor 上一个接口的max_cursor 
@param: sec_user_id 用户id
@param: max_cursor 游标
@param: count 每页数量
@param: locate_item_id 视频id
@param: need_time_list 是否需要时间列表 0 | 1
@param: locate_query 是否定位 默认 false
"""


@api.route('/aweme/post/')
def get_user_post():
    sec_user_id = request.args.get('sec_user_id')
    count = request.args.get('count')
    max_cursor = request.args.get('max_cursor')
    locate_item_id = request.args.get('locate_item_id')
    need_time_list = request.args.get('need_time_list')
    locate_query = request.args.get('locate_query')
    forward_end_cursor = request.args.get('forward_end_cursor')
    url = '/aweme/v1/web/aweme/post/'
    params = {
        'sec_user_id': sec_user_id,
        'count': count,
        'max_cursor': max_cursor,
        'locate_item_id': locate_item_id,
        'locate_query': locate_query,
        'show_live_replay_strategy': '1',
        'need_time_list': need_time_list,
        'time_list_query': '0',
        'publish_video_strategy_type': '2'
    }
    if forward_end_cursor:
        params["forward_end_cursor"] = forward_end_cursor

    post_list = request_instance.getJSON(url, params)
    if post_list:
        return jsonify(post_list)
    else:
        return jsonify({'error': 'Failed to retrieve post_list; Check you Cookie and Referer!'}), 403


"""
@desc: 获取用户喜欢的列表
@url: /aweme/v1/web/aweme/favorite/
"""


@api.route('/aweme/favorite/')
def get_user_favorite():
    sec_user_id = request.args.get('sec_user_id')
    count = request.args.get('count')
    min_cursor = request.args.get('min_cursor')
    max_cursor = request.args.get('max_cursor')
    url = '/aweme/v1/web/aweme/favorite/'
    params = {
        'sec_user_id': sec_user_id,
        'count': count,
        'max_cursor': max_cursor,
        'min_cursor': min_cursor,
        'publish_video_strategy_type': '2'
    }
    favorite_list = request_instance.getJSON(url, params)
    if favorite_list:
        return jsonify(favorite_list)
    else:
        return jsonify({'error': 'Failed to retrieve favorite_list; Check you Cookie and Referer!'}), 403


"""
@desc: 获取用户收藏视频列表
@url： /aweme/v1/web/aweme/listcollection/
"""


@api.route('/aweme/listcollection/')
def get_list_collection():
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/aweme/listcollection/'
    params = {

    }
    data = {
        'count': count,
        'cursor': cursor
    }
    collection_list = request_instance.getJSON(url, params, data)
    if collection_list:
        return jsonify(collection_list)
    else:
        return jsonify({'error': 'Failed to retrieve  collection_list; Check you Cookie and Referer!'}), 403


"""
@desc: 收藏的音乐
@url: /aweme/v1/web/music/listcollection/
@param: cursor 0
@param: count 18
"""


@api.route('/music/listcollection/')
def get_list_collection_music():
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/music/listcollection/'
    params = {
        'count': count,
        'cursor': cursor
    }
    music_list = request_instance.getJSON(url, params)
    if music_list:
        return jsonify(music_list)
    else:
        return jsonify({'error': 'Failed to retrieve  music_list; Check you Cookie and Referer!'}), 404


"""
@desc: 收藏夹
@url: /aweme/v1/web/collects/list/
@param: cursor 0
@param: count 18
"""


@api.route('/collects/list/')
def get_list_collects():
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/collects/list/'
    params = {
        'count': count,
        'cursor': cursor
    }
    collects_list = request_instance.getJSON(url, params)
    if collects_list:
        return jsonify(collects_list)
    else:
        return jsonify({'error': 'Failed to retrieve  collects_list; Check you Cookie and Referer!'}), 404


"""
@desc: 收藏夹视频信息
@url: /aweme/v1/web/collects/video/list/
@param: cursor 0
@param: count 18
"""


@api.route('/collects/video/list/')
def get_list_collects_video():
    collects_id = request.args.get('collects_id')
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/collects/video/list/'
    params = {
        'collects_id': collects_id,
        'count': count,
        'cursor': cursor
    }
    collects_video_list = request_instance.getJSON(url, params)
    if collects_video_list:
        return jsonify(collects_video_list)
    else:
        return jsonify({'error': 'Failed to retrieve  collects_video_list; Check you Cookie and Referer!'}), 404


"""
@desc: 收藏的合集
@url: /aweme/v1/web/mix/listcollection/
"""


@api.route('/mix/listcollection/')
def get_list_collection_mix():
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/mix/listcollection/'
    params = {
        'count': count,
        'cursor': cursor
    }
    mix_list = request_instance.getJSON(url, params)
    if mix_list:
        return jsonify(mix_list)
    else:
        return jsonify({'error': 'Failed to retrieve  mix_list; Check you Cookie and Referer!'}), 404


"""
@desc: 收藏的短剧
@url: /aweme/v1/web/series/collections
"""


@api.route('/series/collections/')
def get_list_collection_series():
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/series/collections'
    params = {
        'count': count,
        'cursor': cursor
    }
    series_list = request_instance.getJSON(url, params)
    if series_list:
        return jsonify(series_list)
    else:
        return jsonify({'error': 'Failed to retrieve  series_list; Check you Cookie and Referer!'}), 404


"""
@desc: 用户创建的合集
@url: /aweme/v1/web/mix/list/
@param: sec_user_id 用户sec_id
@param: count 数量
@param：cursor 游标
"""


@api.route('/mix/list/')
def get_mix_list():
    sec_user_id = request.args.get('sec_user_id')
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/mix/list/'
    params = {
        'sec_user_id': sec_user_id,
        'count': count,
        'cursor': cursor,
        'req_from': 'channel_pc_web'
    }
    mix_list = request_instance.getJSON(url, params)
    if mix_list:
        return jsonify(mix_list)
    else:
        return jsonify({'error': 'Failed to retrieve  mix_list; Check you Cookie and Referer!'}), 403


"""
@desc: 合集的详细信息
@url: /aweme/v1/web/mix/aweme/
"""


@api.route('/mix/aweme/')
def get_mix_list_detail():
    mix_id = request.args.get('mix_id')
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/mix/aweme/'
    params = {
        'mix_id': mix_id,
        'count': count,
        'cursor': cursor,
    }
    mix_list_detail = request_instance.getJSON(url, params)
    if mix_list_detail:
        return jsonify(mix_list_detail)
    else:
        return jsonify({'error': 'Failed to retrieve  mix_list_detail; Check you Cookie and Referer!'}), 403


"""
@desc: 获取用户观看历史列表
@url: /aweme/v1/web/history/read/
"""


@api.route('/history/read/')
def get_history_read():
    count = request.args.get('count')
    max_cursor = request.args.get('max_cursor')

    url = '/aweme/v1/web/history/read/'
    params = {
        'count': count,
        'max_cursor': max_cursor
    }
    history_read = request_instance.getJSON(url, params)
    if history_read:
        return jsonify(history_read)
    else:
        return jsonify({'error': 'Failed to retrieve  history_read; Check you Cookie and Referer!'}), 403


"""
@desc:获取用户的观看的影视综记录
@url: /aweme/v1/web/lvideo/query/history/
"""


@api.route('/lvideo/query/history/')
def get_lvideo_history_read():
    count = request.args.get('count')
    cursor = request.args.get('cursor')

    url = '/aweme/v1/web/lvideo/query/history/'
    params = {
        'count': count,
        'cursor': cursor
    }
    lvideo_history = request_instance.getJSON(url, params)
    if lvideo_history:
        return jsonify(lvideo_history)
    else:
        return jsonify({'error': 'Failed to retrieve  history_read; Check you Cookie and Referer!'}), 403


"""
@desc: 获取用户观看的直播记录
@url:/webcast/feed/
"""


@api.route('/webcast/feed/')
def get_webcast_history_read():
    max_time = request.args.get('max_time')

    url = '/webcast/feed/'
    params = {
        'max_time': max_time,
        'live_id': 1,
        'source_key': 'drawer_hot_live_history',
        'need_map': 1
    }
    webcast_history = request_instance.getJSON(url, params)
    if webcast_history:
        return jsonify(webcast_history)
    else:
        return jsonify({'error': 'Failed to retrieve  history_read; Check you Cookie and Referer!'}), 403


"""
@desc: 上传历史记录
@url: /aweme/v1/web/history/write/
@param: aweme_id
@param: author_id(不是sec_id)
@method: post
"""

"""
@desc: 获取用户关系列表
@url：/aweme/v1/web/im/spotlight/relation/
"""


@api.route('/im/spotlight/relation/')
def get_relation():
    count = request.args.get('count')
    min_time = request.args.get('min_time')
    max_time = request.args.get('max_time')  # 当前的时间戳
    url = '/aweme/v1/web/im/spotlight/relation/'
    params = {
        'count': count,
        'max_time': max_time,
        'min_time': min_time,
        'need_remove_share_panel': 'true',
        'need_sorted_info': 'true',
        'with_fstatus': '1'
    }
    relation = request_instance.getJSON(url, params)
    if relation:
        return jsonify(relation)
    else:
        return jsonify({'error': 'Failed to retrieve relation; Check you Cookie and Referer!'}), 403


"""
@desc: 获取用户关注列表
@url: /aweme/v1/web/user/following/list/
@param: source_type 1最近关注 3最早关注 4 综合排序
"""


@api.route('/user/following/list/')
def get_user_following():
    user_id = request.args.get('user_id')
    sec_user_id = request.args.get('sec_user_id')
    count = request.args.get('count')
    source_type = request.args.get('source_type')
    offset = request.args.get('offset')
    min_time = request.args.get('min_time')
    max_time = request.args.get('max_time')
    url = '/aweme/v1/web/user/following/list/'
    params = {
        'user_id': user_id,
        'sec_user_id': sec_user_id,
        'count': count,
        'offset': offset,
        'max_time': max_time,
        'min_time': min_time,
        'source_type': source_type,
        'gps_access': '0',
        'address_book_access': '0',
        'is_top': '1',
    }
    following_list = request_instance.getJSON(url, params)
    if following_list:
        return jsonify(following_list)
    else:
        return jsonify({'error': 'Failed to retrieve following_list; Check you Cookie and Referer!'}), 403


"""
@desc: 获取粉丝列表
@url: /aweme/v1/web/user/follower/list/
"""


@api.route('/user/follower/list/')
def get_user_follower():
    user_id = request.args.get('user_id')
    sec_user_id = request.args.get('sec_user_id')
    count = request.args.get('count')
    source_type = request.args.get('source_type')
    offset = request.args.get('offset')
    min_time = request.args.get('min_time')
    max_time = request.args.get('max_time')
    url = '/aweme/v1/web/user/follower/list/'
    params = {
        'user_id': user_id,
        'sec_user_id': sec_user_id,
        'count': count,
        'offset': offset,
        'max_time': max_time,
        'min_time': min_time,
        'source_type': source_type,
        'gps_access': '0',
        'address_book_access': '0',
        'is_top': '1',
    }
    follower_list = request_instance.getJSON(url, params)
    if follower_list:
        return jsonify(follower_list)
    else:
        return jsonify({'error': 'Failed to retrieve follower_list; Check you Cookie and Referer!'}), 403


"""
@desc: 用户主页搜索
@url: /aweme/v1/web/home/search/item/
@param: search_channel= aweme_favorite_video | aweme_collect_video | aweme_viewed_video | aweme_personal_home_video
"""


@api.route('/home/search/item/')
def get_search_item():
    search_channel = request.args.get('search_channel')
    keyword = request.args.get('keyword')
    from_user = request.args.get('from_user')
    count = request.args.get('count')
    offset = request.args.get('offset')
    url = '/aweme/v1/web/home/search/item/'
    params = {
        'search_channel': search_channel,
        'search_source': 'normal_search',
        'from_user': from_user,
        'count': count,
        'offset': offset,
        'search_scene': 'douyin_search',
        'sort_type': '0',
        'publish_time': '0',
        'is_filter_search': '0',
        'query_correct_type': '1',
        'keyword': keyword,
        'search_id': ''
    }
    search_item = request_instance.getJSON(url, params)
    if search_item:
        return jsonify(search_item)
    else:
        return jsonify({'error': 'Failed to retrieve search_item; Check you Cookie and Referer!'}), 404


'''
@desc: 添加收藏
@url: /aweme/v1/web/aweme/collect/
@method: post
@data： action: 1
@data： aweme_id: 7422146115929247036
@data： aweme_type: 0
'''

'''
@desc: 添加收藏到特定的收藏夹
@url: /aweme/v1/web/collects/video/move/
@method: post
@params： collects_name: 草
@params： item_ids: 7422146115929247036
@params：item_type: 2
@params： move_collects_list: 7417883349374637865
@params：to_collects_id: 7417883349374637865
'''

'''
@desc: 用户关注的人的视频
@url: /aweme/v1/web/follow/feed/
@param: cursor  开始为0 下一次为接口返回的cursor
@param： level 1
@param： count 默认20
@param： pull_type 18
@param: refresh_type 18
@param: aweme_ids 默认为空
@param: room_ids 默认为空
'''


@api.route('/follow/feed/')
def get_follow_feed():
    cursor = request.args.get('cursor')
    level = request.args.get('level')
    count = request.args.get('count')
    pull_type = request.args.get('pull_type')
    refresh_type = request.args.get('refresh_type')
    aweme_ids = request.args.get('aweme_ids')
    room_ids = request.args.get('room_ids')
    url = '/aweme/v1/web/user/follower/list/'
    params = {
        'cursor': cursor,
        'level': level,
        'count': count,
        'pull_type': pull_type,
        'refresh_type': refresh_type,
        'aweme_ids': aweme_ids,
        'room_ids': room_ids,
    }
    follower_list = request_instance.getJSON(url, params)
    if follower_list:
        return jsonify(follower_list)
    else:
        return jsonify({'error': 'Failed to retrieve follower_list; Check you Cookie and Referer!'}), 403
