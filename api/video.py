from . import api
from flask import jsonify, request
from utils.request import Request

# 延迟初始化，避免启动时的重复日志输出
def get_request_instance():
    """获取Request实例，延迟初始化"""
    if not hasattr(get_request_instance, '_instance'):
        get_request_instance._instance = Request()
    return get_request_instance._instance

# 为了保持向后兼容，创建一个属性访问器
class RequestProxy:
    def __getattr__(self, name):
        return getattr(get_request_instance(), name)

request_instance = RequestProxy()
"""
@desc: 获取视频详细信息
@url: /aweme/v1/web/aweme/detail
@param: aweme_id
"""


@api.route('/aweme/detail/')
def get_detail():
    aweme_id = request.args.get('aweme_id')
    if not aweme_id:
        return jsonify({'error': 'Missing aweme_id parameter'}), 400
    params = {"aweme_id": aweme_id}
    url = '/aweme/v1/web/aweme/detail/'
    aweme_detail = request_instance.getJSON(url, params)  # 直接调用 getJSON 方法
    if aweme_detail:
        return jsonify(aweme_detail)
    else:
        api.logger.error('Failed to retrieve aweme detail for aweme_id: %s', aweme_id)
        return jsonify({'error': 'Failed to retrieve aweme detail; Check you Cookie!'}), 404


"""
@desc: 获取相关视频
@url：/aweme/related
@param: aweme_id
@param: count
@param: filterGids 第一次可以不传值，第二次传入 第一次请求的aweme_id ;
示例：filterGids: 7380308118061780287,7386945509082025225,
7386952050208247080,7379532523379903795,7379995831534947618,7360577857900350746,7391047134314908982,
7391866100910247207,7405446866906729782
@param： refresh_index  第一次：1 
"""


@api.route('/aweme/related/')
def get_related():
    aweme_id = request.args.get('aweme_id')
    count = request.args.get('count')
    filter_gids = request.args.get('filterGids')
    refresh_index = request.args.get('refresh_index')
    if not aweme_id:
        return jsonify({'error': 'Missing aweme_id parameter'}), 400
    params = {"aweme_id": aweme_id, "count": count, "filterGids": filter_gids,
              "awemePcRecRawData": '{"is_client":false}', "sub_channel_id": 0, "Seo-Flag": 0,
              "refresh_index": refresh_index
              }
    url = '/aweme/v1/web/aweme/related/'
    aweme_list = request_instance.getJSON(url, params)
    if aweme_list:
        return jsonify(aweme_list)


"""
@desc: 获取视频评论
@url: /aweme/v1/web/comment/list/
@param: cursor 0 第二次请求为上一个请求的请求count；第一次为0 5 第二次为5 20 第三次为25 25依次递增
@param: count 5
"""


@api.route('/comment/list/')
def get_comment_list():
    aweme_id = request.args.get('aweme_id')
    cursor = request.args.get('cursor')
    count = request.args.get('count')
    params = {
        "aweme_id": aweme_id,
        "cursor": cursor,
        "count": count
    }
    url = '/aweme/v1/web/comment/list/'
    comment_list = request_instance.getJSON(url, params)
    if comment_list:
        return jsonify(comment_list)
    else:
        api.logger.error('Failed to retrieve comment list for aweme_id: %s url: %s', aweme_id, url)
        return jsonify({'error': 'Failed to retrieve comment list; Check you Cookie!'}), 404


"""
@desc： 展开更多评论
@url： /aweme/v1/web/comment/list/reply/
@param: item_id 视频id
@param：comment_id 评论id
@param：cursor 0 3 13
@param： count 3 10 10
"""


@api.route('/comment/list/reply/')
def get_reply_list():
    item_id = request.args.get('item_id')  # 视频id
    comment_id = request.args.get('comment_id')
    cursor = request.args.get('cursor')
    count = request.args.get('count')
    params = {
        "item_id": item_id,
        "comment_id": comment_id,
        "cursor": cursor,
        "count": count
    }
    url = '/aweme/v1/web/comment/list/reply/'
    comment_list = request_instance.getJSON(url, params)
    if comment_list:
        return jsonify(comment_list)
    else:
        api.logger.error('Failed to retrieve comment list for aweme_id: %s url: %s', item_id, url)
        return jsonify({'error': 'Failed to retrieve comment list; Check you Cookie!'}), 404


"""
@desc: 获取首页瀑布流视频
@url: /aweme/v1/web/module/feed/
"""


@api.route('/module/feed/')
def get_module_feed():
    count = request.args.get('count')
    refresh_index = request.args.get('refresh_index')
    tag_id = request.args.get('tag_id')
    params = {'count': count,
              'video_type_select': '1',
              'module_id': '3003101',
              'filterGids': '',
              'presented_ids': '',
              'refer_id': '',
              'refer_type': '10',
              'tag_id': tag_id,
              "aweme_pc_rec_raw_data": '{"is_xigua_user":0,"is_client":false}',
              "refresh_index": refresh_index
              }
    url = '/aweme/v1/web/module/feed/'
    aweme_list = request_instance.getJSON(url, params)
    if aweme_list:
        return jsonify(aweme_list)


'''
@desc: 获取推荐页feed
@url: /aweme/v1/web/tab/feed/
'''


@api.route('/web/tab/feed/')
def get_tab_feed():
    count = request.args.get('count')
    refresh_index = request.args.get('refresh_index')
    params = {"count": count,
              'video_type_select': '1',
              "aweme_pc_rec_raw_data": '{"is_client":false,"ff_danmaku_status":1,"danmaku_switch_status":1,'
                                       '"is_auto_play":0,"is_full_screen":0,"is_full_webscreen":0,"is_mute":0,'
                                       '"is_speed":1,"is_visible":1,"related_recommend":1}',
              "refresh_index": refresh_index
              }
    url = '/aweme/v1/web/tab/feed/'
    aweme_list = request_instance.getJSON(url, params)
    if aweme_list:
        return jsonify(aweme_list)


"""
@desc: 用户点赞
@url: /aweme/v1/web/commit/item/digg/
@param: aweme_id 视频id 必须
@param: type 点赞类型 1 点赞 0 取消
@param： item_type 暂未知道含义 默认为0 
"""


@api.route('/commit/item/digg/')
def post_digg():
    aweme_id = request.args.get('aweme_id')
    digg_type = request.args.get('type')
    item_type = request.args.get('item_type')

    url = '/aweme/v1/web/commit/item/digg/'
    params = {

    }
    data = {
        'aweme_id': aweme_id,
        'type': digg_type,
        'item_type': item_type
    }
    commit_digg = request_instance.getJSON(url, params, data)
    if commit_digg:
        return jsonify(commit_digg)
    else:
        return jsonify({'error': 'Failed to retrieve  collection_list; Check you Cookie and Referer!'}), 403
