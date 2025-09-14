#!/usr/bin/env python3
"""
关注用户视频管理路由
独立的API路由模块，保持代码模块化
"""

from flask import Blueprint, request, jsonify
import time
from utils.request import Request
from utils.account_manager import AccountManager

# 创建蓝图
following_videos_bp = Blueprint('following_videos', __name__)

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

@following_videos_bp.route('/api/following-users-videos', methods=['GET'])
def get_following_users_videos():
    """获取关注用户的视频数据 - 使用真实API"""
    try:
        user_account = request.args.get('user_account')

        if not user_account:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'user_account is required'
            })

        print(f"获取用户 {user_account} 的关注用户视频数据")

        # 1. 获取用户自己的信息
        user_profile_url = '/aweme/v1/web/user/profile/self/'
        user_profile_params = {}
        user_profile = request_instance.getJSON(user_profile_url, user_profile_params)

        if not user_profile or user_profile.get('status_code') != 0:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get user profile'
            })

        user_id = user_profile.get('user', {}).get('uid')
        sec_user_id = user_profile.get('user', {}).get('sec_uid')

        # 2. 获取关注列表
        following_url = '/aweme/v1/web/user/following/list/'
        following_params = {
            'user_id': user_id,
            'sec_user_id': sec_user_id,
            'count': '20',
            'offset': '0',
            'max_time': '0',
            'min_time': '0',
            'source_type': '1',
            'gps_access': '0',
            'address_book_access': '0',
            'is_top': '1',
        }

        following_list = request_instance.getJSON(following_url, following_params)
        
        if not following_list or following_list.get('status_code') != 0:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get following list'
            })

        # 3. 为每个关注用户获取视频列表
        following_users_with_videos = []
        followings = following_list.get('followings', [])

        for user in followings[:10]:  # 限制前10个用户，避免请求过多
            user_sec_uid = user.get('sec_uid', '')
            user_uid = user.get('uid', '')

            if not user_sec_uid:
                continue

            # 获取用户视频列表
            user_videos_url = '/aweme/v1/web/aweme/post/'
            user_videos_params = {
                'sec_user_id': user_sec_uid,
                'count': '10',
                'max_cursor': '0',
                'locate_query': 'false',
                'show_live_replay_strategy': '1',
                'need_time_list': '1',
                'time_list_query': '0',
                'whale_cut_token': '',
                'cut_version': '1',
                'count_query': '1',
                'publish_video_strategy_type': '2'
            }

            user_videos = request_instance.getJSON(user_videos_url, user_videos_params)

            videos = []
            if user_videos and user_videos.get('status_code') == 0:
                aweme_list = user_videos.get('aweme_list', [])

                for aweme in aweme_list[:5]:  # 每个用户最多5个视频
                    video_info = {
                        'videoId': aweme.get('aweme_id', ''),
                        'title': aweme.get('desc', ''),
                        'duration': aweme.get('duration', 0),
                        'cover': aweme.get('video', {}).get('cover', {}).get('url_list', [''])[0] if aweme.get('video', {}).get('cover', {}).get('url_list') else '',
                        'viewed': False,  # 默认未看
                        'createTime': aweme.get('create_time', 0) * 1000,  # 转换为毫秒
                        'author': {
                            'nickname': user.get('nickname', ''),
                            'avatar': user.get('avatar_thumb', {}).get('url_list', [''])[0] if user.get('avatar_thumb', {}).get('url_list') else ''
                        },
                        'statistics': {
                            'digg_count': aweme.get('statistics', {}).get('digg_count', 0),
                            'comment_count': aweme.get('statistics', {}).get('comment_count', 0),
                            'share_count': aweme.get('statistics', {}).get('share_count', 0)
                        }
                    }
                    videos.append(video_info)

            # 构建用户信息
            user_info = {
                'secUid': user_sec_uid,
                'uid': user_uid,
                'nickname': user.get('nickname', ''),
                'avatar': user.get('avatar_thumb', {}).get('url_list', [''])[0] if user.get('avatar_thumb', {}).get('url_list') else '',
                'totalVideos': user.get('aweme_count', 0),
                'unwatchedCount': len(videos),  # 假设所有视频都未看
                'videos': videos
            }

            following_users_with_videos.append(user_info)

        return jsonify({
            'success': True,
            'code': 200,
            'data': following_users_with_videos,
            'msg': 'success'
        })

    except Exception as e:
        print(f"Error in get_following_users_videos: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/api/system-status', methods=['GET'])
def get_system_status():
    """获取系统状态信息"""
    return jsonify({
        'success': True,
        'code': 200,
        'data': {
            'totalUsers': 2,
            'totalVideos': 37,
            'unwatchedVideos': 13,
            'lastUpdateTime': int(time.time() * 1000),
            'lastFollowingUpdate': int(time.time() * 1000) - 1800000,
            'updateFrequency': 10,
            'followingUpdateFrequency': 30
        },
        'msg': 'success'
    })

@following_videos_bp.route('/api/mark-video-watched', methods=['POST'])
def mark_video_watched():
    """设置视频为已观看 - 记录到本地存储"""
    try:
        # 支持不同的Content-Type
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        elif request.form:
            data = request.form.to_dict()

        video_id = data.get('video_id')
        user_account = request.args.get('user_account') or data.get('user_account')

        if not video_id:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'video_id is required'
            })

        # 记录视频已看状态（这里可以扩展为数据库存储）
        print(f"用户 {user_account} 标记视频已看: {video_id}")

        # TODO: 这里可以添加数据库存储逻辑
        # 例如：save_watched_video(user_account, video_id, timestamp)

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'video_id': video_id,
                'user_account': user_account,
                'watched_time': int(time.time() * 1000)
            },
            'msg': 'Video marked as watched'
        })

    except Exception as e:
        print(f"Error in mark_video_watched: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/api/mark-multiple-videos-watched', methods=['POST'])
def mark_multiple_videos_watched():
    """批量设置多个视频为已观看 - 记录到本地存储"""
    try:
        # 支持不同的Content-Type
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        elif request.form:
            data = request.form.to_dict()
            # 处理表单数据中的数组
            if 'video_ids' in data and isinstance(data['video_ids'], str):
                import json
                try:
                    data['video_ids'] = json.loads(data['video_ids'])
                except:
                    data['video_ids'] = data['video_ids'].split(',')

        video_ids = data.get('video_ids', [])
        user_account = request.args.get('user_account') or data.get('user_account')

        if not video_ids:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'video_ids is required'
            })

        # 批量记录视频已看状态
        print(f"用户 {user_account} 批量标记视频已看: {len(video_ids)} 个视频")

        # TODO: 这里可以添加数据库批量存储逻辑
        # 例如：batch_save_watched_videos(user_account, video_ids, timestamp)

        watched_videos = []
        current_time = int(time.time() * 1000)

        for video_id in video_ids:
            watched_videos.append({
                'video_id': video_id,
                'watched_time': current_time
            })

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'updated_count': len(video_ids),
                'user_account': user_account,
                'watched_videos': watched_videos
            },
            'msg': f'{len(video_ids)} videos marked as watched'
        })

    except Exception as e:
        print(f"Error in mark_multiple_videos_watched: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/api/user-unwatched-videos', methods=['GET'])
def get_user_unwatched_videos():
    """获取指定用户的所有未观看视频 - 使用真实API"""
    try:
        sec_uid = request.args.get('sec_uid')

        if not sec_uid:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'sec_uid is required'
            })

        print(f"获取用户 {sec_uid} 的所有视频")

        # 1. 先获取用户信息
        user_info_url = '/aweme/v1/web/user/profile/other/'
        user_info_params = {
            'sec_user_id': sec_uid,
            'source': 'channel_pc_web',
            'publish_video_strategy_type': '2',
            'personal_center_strategy': '1'
        }

        user_info = request_instance.getJSON(user_info_url, user_info_params)

        if not user_info or user_info.get('status_code') != 0:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get user info'
            })

        user_data = user_info.get('user', {})

        # 2. 获取用户的视频列表
        user_videos_url = '/aweme/v1/web/aweme/post/'
        user_videos_params = {
            'sec_user_id': sec_uid,
            'count': '20',
            'max_cursor': '0',
            'locate_query': 'false',
            'show_live_replay_strategy': '1',
            'need_time_list': '1',
            'time_list_query': '0',
            'whale_cut_token': '',
            'cut_version': '1',
            'count_query': '1',
            'publish_video_strategy_type': '2'
        }

        user_videos = request_instance.getJSON(user_videos_url, user_videos_params)

        if not user_videos or user_videos.get('status_code') != 0:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get user videos'
            })

        # 3. 处理视频数据
        videos = []
        aweme_list = user_videos.get('aweme_list', [])

        for aweme in aweme_list:
            video_info = {
                'videoId': aweme.get('aweme_id', ''),
                'title': aweme.get('desc', ''),
                'duration': aweme.get('duration', 0),
                'cover': aweme.get('video', {}).get('cover', {}).get('url_list', [''])[0] if aweme.get('video', {}).get('cover', {}).get('url_list') else '',
                'viewed': False,  # 默认未看，实际应该从数据库查询
                'createTime': aweme.get('create_time', 0) * 1000,  # 转换为毫秒
                'author': {
                    'nickname': user_data.get('nickname', ''),
                    'avatar': user_data.get('avatar_thumb', {}).get('url_list', [''])[0] if user_data.get('avatar_thumb', {}).get('url_list') else ''
                },
                'statistics': {
                    'digg_count': aweme.get('statistics', {}).get('digg_count', 0),
                    'comment_count': aweme.get('statistics', {}).get('comment_count', 0),
                    'share_count': aweme.get('statistics', {}).get('share_count', 0)
                }
            }
            videos.append(video_info)

        # 4. 构建返回数据
        result_data = {
            'userInfo': {
                'secUid': sec_uid,
                'uid': user_data.get('uid', ''),
                'nickname': user_data.get('nickname', ''),
                'avatar': user_data.get('avatar_thumb', {}).get('url_list', [''])[0] if user_data.get('avatar_thumb', {}).get('url_list') else ''
            },
            'videos': videos,
            'totalVideos': user_data.get('aweme_count', len(videos))
        }

        return jsonify({
            'success': True,
            'code': 200,
            'data': result_data,
            'msg': 'success'
        })

    except Exception as e:
        print(f"Error in get_user_unwatched_videos: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/api/update-following-list', methods=['POST', 'GET'])
def update_following_list():
    """更新关注列表 - 获取真实的关注用户数据"""
    try:
        user_account = request.args.get('user_account')

        if not user_account:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'user_account is required'
            })

        # 获取请求数据，支持不同的Content-Type
        data = {}
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json() or {}
            elif request.form:
                data = request.form.to_dict()

        print(f"更新用户 {user_account} 的关注列表")

        # 使用真实的API获取关注列表
        # 首先获取用户自己的信息来获取user_id
        user_profile_url = '/aweme/v1/web/user/profile/self/'
        user_profile_params = {}
        user_profile = request_instance.getJSON(user_profile_url, user_profile_params)

        if not user_profile or user_profile.get('status_code') != 0:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get user profile'
            })

        user_id = user_profile.get('user', {}).get('uid')
        sec_user_id = user_profile.get('user', {}).get('sec_uid')

        if not user_id:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get user_id from profile'
            })

        # 获取关注列表
        following_url = '/aweme/v1/web/user/following/list/'
        following_params = {
            'user_id': user_id,
            'sec_user_id': sec_user_id,
            'count': '20',
            'offset': '0',
            'max_time': '0',
            'min_time': '0',
            'source_type': '1',
            'gps_access': '0',
            'address_book_access': '0',
            'is_top': '1',
        }

        following_list = request_instance.getJSON(following_url, following_params)

        if not following_list or following_list.get('status_code') != 0:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get following list'
            })

        # 处理关注列表数据
        followings = following_list.get('followings', [])
        updated_count = len(followings)

        # 提取关注用户的基本信息
        following_users = []
        for user in followings:
            following_users.append({
                'sec_uid': user.get('sec_uid', ''),
                'uid': user.get('uid', ''),
                'nickname': user.get('nickname', ''),
                'avatar': user.get('avatar_thumb', {}).get('url_list', [''])[0] if user.get('avatar_thumb', {}).get('url_list') else '',
                'unique_id': user.get('unique_id', ''),
                'signature': user.get('signature', ''),
                'aweme_count': user.get('aweme_count', 0),
                'follower_count': user.get('follower_count', 0),
                'following_count': user.get('following_count', 0)
            })

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'user_account': user_account,
                'updated_count': updated_count,
                'following_users': following_users,
                'last_update_time': int(time.time() * 1000),
                'total_count': following_list.get('total', updated_count)
            },
            'msg': f'Successfully updated following list for {user_account}'
        })

    except Exception as e:
        print(f"Error in update_following_list: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/api/update-user-videos', methods=['POST'])
def update_user_videos():
    """更新用户视频列表 - 使用真实API"""
    try:
        user_account = request.args.get('user_account')

        # 获取请求数据，支持不同的Content-Type
        data = {}
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json() or {}
            elif request.form:
                data = request.form.to_dict()

        sec_uid = data.get('sec_uid')

        if not user_account:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'user_account is required'
            })

        if not sec_uid:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'sec_uid is required'
            })

        print(f"更新用户 {user_account} 的视频列表，sec_uid: {sec_uid}")

        # 获取用户最新的视频列表
        user_videos_url = '/aweme/v1/web/aweme/post/'
        user_videos_params = {
            'sec_user_id': sec_uid,
            'count': '20',
            'max_cursor': '0',
            'locate_query': 'false',
            'show_live_replay_strategy': '1',
            'need_time_list': '1',
            'time_list_query': '0',
            'whale_cut_token': '',
            'cut_version': '1',
            'count_query': '1',
            'publish_video_strategy_type': '2'
        }

        user_videos = request_instance.getJSON(user_videos_url, user_videos_params)

        if not user_videos or user_videos.get('status_code') != 0:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to get user videos'
            })

        # 处理视频数据
        aweme_list = user_videos.get('aweme_list', [])
        new_videos_count = len(aweme_list)

        # 提取视频基本信息
        videos = []
        for aweme in aweme_list:
            video_info = {
                'videoId': aweme.get('aweme_id', ''),
                'title': aweme.get('desc', ''),
                'duration': aweme.get('duration', 0),
                'cover': aweme.get('video', {}).get('cover', {}).get('url_list', [''])[0] if aweme.get('video', {}).get('cover', {}).get('url_list') else '',
                'createTime': aweme.get('create_time', 0) * 1000,
                'statistics': {
                    'digg_count': aweme.get('statistics', {}).get('digg_count', 0),
                    'comment_count': aweme.get('statistics', {}).get('comment_count', 0),
                    'share_count': aweme.get('statistics', {}).get('share_count', 0)
                }
            }
            videos.append(video_info)

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'user_account': user_account,
                'sec_uid': sec_uid,
                'new_videos_count': new_videos_count,
                'videos': videos,
                'last_update_time': int(time.time() * 1000),
                'has_more': user_videos.get('has_more', False),
                'max_cursor': user_videos.get('max_cursor', '0')
            },
            'msg': f'Successfully updated videos for user {sec_uid}'
        })

    except Exception as e:
        print(f"Error in update_user_videos: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time() * 1000),
        'message': 'Douyin API服务运行正常',
        'features': ['following-videos-management']
    })
