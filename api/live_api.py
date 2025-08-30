from . import api
from utils.request import Request
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

# 为了保持向后兼容，创建一个属性访问器
class RequestProxy:
    def __getattr__(self, name):
        return getattr(get_request_instance(), name)

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
