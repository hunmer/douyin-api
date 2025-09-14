#!/usr/bin/env python3
"""
关注用户视频管理API服务
集成到douyin-api项目中的完整实现

依赖安装：
pip install flask flask-cors requests schedule sqlite3 threading

使用方法：
1. 将此文件放入douyin-api项目的api目录
2. 在主应用中导入并注册蓝图
3. 运行数据库初始化
4. 启动定时任务
"""

from flask import Blueprint, request, jsonify
import json
import time
import threading
import schedule
import requests
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# 创建蓝图
following_videos_bp = Blueprint('following_videos', __name__, url_prefix='/api')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_PATH = 'data/following_videos.db'
DOUYIN_API_BASE = 'http://127.0.0.1:3010'

class FollowingVideosManager:
    """关注用户视频管理器"""
    
    def __init__(self):
        self.init_database()
        self.scheduler_running = False
    
    def init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS following_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sec_uid TEXT UNIQUE NOT NULL,
                uid TEXT,
                nickname TEXT,
                avatar TEXT,
                unique_id TEXT,
                signature TEXT,
                last_cursor TEXT DEFAULT '0',
                last_check_time INTEGER DEFAULT 0,
                total_videos INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0,
                follower_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # 创建视频表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                user_sec_uid TEXT NOT NULL,
                title TEXT,
                desc_text TEXT,
                duration INTEGER,
                cover_url TEXT,
                play_url TEXT,
                author_info TEXT,
                statistics TEXT,
                create_time INTEGER,
                viewed INTEGER DEFAULT 0,
                viewed_at INTEGER DEFAULT 0,
                added_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (user_sec_uid) REFERENCES following_users (sec_uid)
            )
        ''')
        
        # 创建系统状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                id INTEGER PRIMARY KEY DEFAULT 1,
                last_following_update INTEGER DEFAULT 0,
                last_videos_update INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0,
                total_videos INTEGER DEFAULT 0,
                unwatched_videos INTEGER DEFAULT 0,
                update_frequency_minutes INTEGER DEFAULT 10,
                following_update_frequency_minutes INTEGER DEFAULT 30
            )
        ''')
        
        # 插入默认系统状态
        cursor.execute('''
            INSERT OR IGNORE INTO system_status (id) VALUES (1)
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_user_sec_uid ON user_videos(user_sec_uid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_viewed ON user_videos(viewed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_create_time ON user_videos(create_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_last_check ON following_users(last_check_time)')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def get_db_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def call_douyin_api(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """调用抖音API"""
        try:
            url = f"{DOUYIN_API_BASE}{endpoint}"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"调用抖音API失败: {endpoint}, 错误: {e}")
            return None
    
    def update_following_list(self) -> bool:
        """更新关注列表"""
        try:
            logger.info("开始更新关注列表...")
            
            # 调用抖音API获取关注列表
            following_data = self.call_douyin_api('/aweme/v1/web/user/following/list/', {
                'count': 20,
                'max_cursor': 0,
                'min_cursor': 0
            })
            
            if not following_data or not following_data.get('followings'):
                logger.warning("获取关注列表失败或为空")
                return False
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            current_time = int(time.time())
            updated_count = 0
            
            for user in following_data['followings']:
                try:
                    # 插入或更新用户信息
                    cursor.execute('''
                        INSERT OR REPLACE INTO following_users 
                        (sec_uid, uid, nickname, avatar, unique_id, signature, 
                         following_count, follower_count, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user.get('sec_uid', ''),
                        user.get('uid', ''),
                        user.get('nickname', ''),
                        user.get('avatar_thumb', {}).get('url_list', [''])[0],
                        user.get('unique_id', ''),
                        user.get('signature', ''),
                        user.get('following_count', 0),
                        user.get('follower_count', 0),
                        current_time
                    ))
                    updated_count += 1
                except Exception as e:
                    logger.error(f"更新用户失败: {user.get('nickname', 'Unknown')}, 错误: {e}")
            
            # 更新系统状态
            cursor.execute('''
                UPDATE system_status 
                SET last_following_update = ?, total_users = ?
                WHERE id = 1
            ''', (current_time, updated_count))
            
            conn.commit()
            conn.close()
            
            logger.info(f"关注列表更新完成，更新了 {updated_count} 个用户")
            return True
            
        except Exception as e:
            logger.error(f"更新关注列表失败: {e}")
            return False
    
    def update_user_videos(self, sec_uid: str = None) -> bool:
        """更新用户视频"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 如果指定了用户，只更新该用户；否则更新所有用户
            if sec_uid:
                cursor.execute('''
                    SELECT sec_uid, nickname, last_cursor 
                    FROM following_users 
                    WHERE sec_uid = ? AND is_active = 1
                ''', (sec_uid,))
            else:
                cursor.execute('''
                    SELECT sec_uid, nickname, last_cursor 
                    FROM following_users 
                    WHERE is_active = 1
                    ORDER BY last_check_time ASC
                    LIMIT 5
                ''')
            
            users = cursor.fetchall()
            
            if not users:
                logger.info("没有需要更新的用户")
                return True
            
            current_time = int(time.time())
            total_new_videos = 0
            
            for user in users:
                try:
                    logger.info(f"更新用户视频: {user['nickname']}")
                    
                    # 调用抖音API获取用户视频
                    videos_data = self.call_douyin_api('/aweme/v1/web/aweme/post/', {
                        'sec_user_id': user['sec_uid'],
                        'count': 20,
                        'max_cursor': user['last_cursor'] or '0'
                    })
                    
                    if not videos_data or not videos_data.get('aweme_list'):
                        continue
                    
                    new_videos_count = 0
                    new_max_cursor = videos_data.get('max_cursor', user['last_cursor'])
                    
                    for video in videos_data['aweme_list']:
                        try:
                            # 检查视频是否已存在
                            cursor.execute('''
                                SELECT id FROM user_videos WHERE video_id = ?
                            ''', (video['aweme_id'],))
                            
                            if cursor.fetchone():
                                continue  # 视频已存在，跳过
                            
                            # 插入新视频
                            author_info = json.dumps({
                                'uid': video['author'].get('uid', ''),
                                'sec_uid': video['author'].get('sec_uid', ''),
                                'nickname': video['author'].get('nickname', ''),
                                'avatar': video['author'].get('avatar_168x168', {}).get('url_list', [''])[0]
                            })
                            
                            statistics = json.dumps({
                                'digg_count': video['statistics'].get('digg_count', 0),
                                'comment_count': video['statistics'].get('comment_count', 0),
                                'share_count': video['statistics'].get('share_count', 0),
                                'play_count': video['statistics'].get('play_count', 0)
                            })
                            
                            cursor.execute('''
                                INSERT INTO user_videos 
                                (video_id, user_sec_uid, title, desc_text, duration, 
                                 cover_url, author_info, statistics, create_time)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                video['aweme_id'],
                                user['sec_uid'],
                                video.get('desc', '')[:100],  # 限制标题长度
                                video.get('desc', ''),
                                video.get('duration', 0),
                                video.get('video', {}).get('cover', {}).get('url_list', [''])[0],
                                author_info,
                                statistics,
                                video.get('create_time', current_time)
                            ))
                            
                            new_videos_count += 1
                            total_new_videos += 1
                            
                        except Exception as e:
                            logger.error(f"插入视频失败: {video.get('aweme_id', 'Unknown')}, 错误: {e}")
                    
                    # 更新用户的last_cursor和last_check_time
                    cursor.execute('''
                        UPDATE following_users 
                        SET last_cursor = ?, last_check_time = ?, total_videos = total_videos + ?
                        WHERE sec_uid = ?
                    ''', (new_max_cursor, current_time, new_videos_count, user['sec_uid']))
                    
                    logger.info(f"用户 {user['nickname']} 新增 {new_videos_count} 个视频")
                    
                except Exception as e:
                    logger.error(f"更新用户 {user['nickname']} 的视频失败: {e}")
            
            # 更新系统状态
            cursor.execute('''
                UPDATE system_status 
                SET last_videos_update = ?, total_videos = total_videos + ?
                WHERE id = 1
            ''', (current_time, total_new_videos))
            
            conn.commit()
            conn.close()
            
            logger.info(f"视频更新完成，总共新增 {total_new_videos} 个视频")
            return True
            
        except Exception as e:
            logger.error(f"更新用户视频失败: {e}")
            return False
    
    def start_scheduler(self):
        """启动定时任务"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        
        # 每30分钟更新一次关注列表
        schedule.every(30).minutes.do(self.update_following_list)
        
        # 每10分钟更新一次用户视频
        schedule.every(10).minutes.do(self.update_user_videos)
        
        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("定时任务已启动")

# 创建管理器实例
manager = FollowingVideosManager()

@following_videos_bp.route('/local-users', methods=['GET'])
def get_local_users():
    """获取所有本地用户列表"""
    try:
        conn = manager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sec_uid, uid, nickname, avatar, unique_id, signature,
                   last_cursor, last_check_time, total_videos, 
                   following_count, follower_count
            FROM following_users
            WHERE is_active = 1
            ORDER BY last_check_time DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'secUid': row['sec_uid'],
                'uid': row['uid'],
                'nickname': row['nickname'],
                'avatar': row['avatar'],
                'uniqueId': row['unique_id'],
                'signature': row['signature'],
                'lastCursor': row['last_cursor'],
                'lastCheckTime': row['last_check_time'],
                'totalVideos': row['total_videos'],
                'followingCount': row['following_count'],
                'followerCount': row['follower_count']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'code': 200,
            'data': users,
            'msg': 'success'
        })
        
    except Exception as e:
        logger.error(f"获取本地用户列表失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': [],
            'msg': str(e)
        })

@following_videos_bp.route('/following-users-videos', methods=['GET'])
def get_following_users_videos():
    """获取关注用户的视频数据（过滤掉看过的，只展示前三个）"""
    try:
        conn = manager.get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有用户及其未看视频数量
        cursor.execute('''
            SELECT u.sec_uid, u.uid, u.nickname, u.avatar, u.total_videos,
                   COUNT(CASE WHEN v.viewed = 0 THEN 1 END) as unwatched_count
            FROM following_users u
            LEFT JOIN user_videos v ON u.sec_uid = v.user_sec_uid
            WHERE u.is_active = 1
            GROUP BY u.sec_uid
            HAVING unwatched_count > 0 OR u.total_videos > 0
            ORDER BY unwatched_count DESC, u.last_check_time DESC
        ''')
        
        users_data = []
        for user_row in cursor.fetchall():
            # 获取该用户的前3个未看视频
            cursor.execute('''
                SELECT video_id, title, desc_text, duration, cover_url, 
                       author_info, statistics, viewed, create_time
                FROM user_videos
                WHERE user_sec_uid = ? AND viewed = 0
                ORDER BY create_time DESC
                LIMIT 3
            ''', (user_row['sec_uid'],))
            
            videos = []
            for video_row in cursor.fetchall():
                try:
                    author_info = json.loads(video_row['author_info'] or '{}')
                    statistics = json.loads(video_row['statistics'] or '{}')
                    
                    videos.append({
                        'videoId': video_row['video_id'],
                        'title': video_row['title'] or video_row['desc_text'] or '无标题',
                        'duration': video_row['duration'] or 0,
                        'cover': video_row['cover_url'] or '',
                        'viewed': bool(video_row['viewed']),
                        'createTime': video_row['create_time'],
                        'author': author_info,
                        'statistics': statistics
                    })
                except Exception as e:
                    logger.error(f"解析视频数据失败: {e}")
                    continue
            
            users_data.append({
                'secUid': user_row['sec_uid'],
                'uid': user_row['uid'],
                'nickname': user_row['nickname'],
                'avatar': user_row['avatar'],
                'totalVideos': user_row['total_videos'],
                'unwatchedCount': user_row['unwatched_count'],
                'videos': videos
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'code': 200,
            'data': users_data,
            'msg': 'success'
        })
        
    except Exception as e:
        logger.error(f"获取关注用户视频失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': [],
            'msg': str(e)
        })

@following_videos_bp.route('/user-unwatched-videos', methods=['GET'])
def get_user_unwatched_videos():
    """获取指定用户的所有未观看视频"""
    try:
        sec_uid = request.args.get('sec_uid')
        if not sec_uid:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'sec_uid is required'
            })

        conn = manager.get_db_connection()
        cursor = conn.cursor()

        # 获取用户信息
        cursor.execute('''
            SELECT sec_uid, uid, nickname, avatar, total_videos
            FROM following_users
            WHERE sec_uid = ? AND is_active = 1
        ''', (sec_uid,))

        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({
                'success': False,
                'code': 404,
                'data': None,
                'msg': 'User not found'
            })

        # 获取用户的所有视频（包括已看和未看）
        cursor.execute('''
            SELECT video_id, title, desc_text, duration, cover_url,
                   author_info, statistics, viewed, create_time
            FROM user_videos
            WHERE user_sec_uid = ?
            ORDER BY create_time DESC
        ''', (sec_uid,))

        videos = []
        for video_row in cursor.fetchall():
            try:
                author_info = json.loads(video_row['author_info'] or '{}')
                statistics = json.loads(video_row['statistics'] or '{}')

                videos.append({
                    'videoId': video_row['video_id'],
                    'title': video_row['title'] or video_row['desc_text'] or '无标题',
                    'duration': video_row['duration'] or 0,
                    'cover': video_row['cover_url'] or '',
                    'viewed': bool(video_row['viewed']),
                    'createTime': video_row['create_time'],
                    'author': author_info,
                    'statistics': statistics
                })
            except Exception as e:
                logger.error(f"解析视频数据失败: {e}")
                continue

        conn.close()

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'userInfo': {
                    'secUid': user_row['sec_uid'],
                    'uid': user_row['uid'],
                    'nickname': user_row['nickname'],
                    'avatar': user_row['avatar']
                },
                'videos': videos,
                'totalVideos': user_row['total_videos']
            },
            'msg': 'success'
        })

    except Exception as e:
        logger.error(f"获取用户未看视频失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/mark-video-watched', methods=['POST'])
def mark_video_watched():
    """设置视频为已观看"""
    try:
        data = request.get_json()
        video_id = data.get('video_id')

        if not video_id:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'video_id is required'
            })

        conn = manager.get_db_connection()
        cursor = conn.cursor()

        current_time = int(time.time())
        cursor.execute('''
            UPDATE user_videos
            SET viewed = 1, viewed_at = ?
            WHERE video_id = ?
        ''', (current_time, video_id))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'success': False,
                'code': 404,
                'data': None,
                'msg': 'Video not found'
            })

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'code': 200,
            'data': None,
            'msg': 'Video marked as watched'
        })

    except Exception as e:
        logger.error(f"标记视频已看失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/mark-multiple-videos-watched', methods=['POST'])
def mark_multiple_videos_watched():
    """批量设置多个视频为已观看"""
    try:
        data = request.get_json()
        video_ids = data.get('video_ids', [])

        if not video_ids:
            return jsonify({
                'success': False,
                'code': 400,
                'data': None,
                'msg': 'video_ids is required'
            })

        conn = manager.get_db_connection()
        cursor = conn.cursor()

        current_time = int(time.time())
        placeholders = ','.join(['?' for _ in video_ids])
        cursor.execute(f'''
            UPDATE user_videos
            SET viewed = 1, viewed_at = ?
            WHERE video_id IN ({placeholders})
        ''', [current_time] + video_ids)

        updated_count = cursor.rowcount
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'code': 200,
            'data': {'updated_count': updated_count},
            'msg': f'{updated_count} videos marked as watched'
        })

    except Exception as e:
        logger.error(f"批量标记视频已看失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/update-following-list', methods=['POST'])
def update_following_list():
    """手动触发关注列表更新"""
    try:
        success = manager.update_following_list()

        if success:
            return jsonify({
                'success': True,
                'code': 200,
                'data': None,
                'msg': 'Following list updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to update following list'
            })

    except Exception as e:
        logger.error(f"手动更新关注列表失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/update-user-videos', methods=['POST'])
def update_user_videos():
    """手动触发用户视频更新"""
    try:
        data = request.get_json()
        sec_uid = data.get('sec_uid') if data else None

        success = manager.update_user_videos(sec_uid)

        if success:
            return jsonify({
                'success': True,
                'code': 200,
                'data': None,
                'msg': 'User videos updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'code': 500,
                'data': None,
                'msg': 'Failed to update user videos'
            })

    except Exception as e:
        logger.error(f"手动更新用户视频失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

@following_videos_bp.route('/system-status', methods=['GET'])
def get_system_status():
    """获取系统状态信息"""
    try:
        conn = manager.get_db_connection()
        cursor = conn.cursor()

        # 获取系统状态
        cursor.execute('''
            SELECT last_following_update, last_videos_update,
                   update_frequency_minutes, following_update_frequency_minutes
            FROM system_status WHERE id = 1
        ''')
        status_row = cursor.fetchone()

        # 获取实时统计信息
        cursor.execute('SELECT COUNT(*) as total_users FROM following_users WHERE is_active = 1')
        total_users = cursor.fetchone()['total_users']

        cursor.execute('SELECT COUNT(*) as total_videos FROM user_videos')
        total_videos = cursor.fetchone()['total_videos']

        cursor.execute('SELECT COUNT(*) as unwatched_videos FROM user_videos WHERE viewed = 0')
        unwatched_videos = cursor.fetchone()['unwatched_videos']

        conn.close()

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'totalUsers': total_users,
                'totalVideos': total_videos,
                'unwatchedVideos': unwatched_videos,
                'lastUpdateTime': (status_row['last_videos_update'] if status_row else 0) * 1000,
                'lastFollowingUpdate': (status_row['last_following_update'] if status_row else 0) * 1000,
                'updateFrequency': status_row['update_frequency_minutes'] if status_row else 10,
                'followingUpdateFrequency': status_row['following_update_frequency_minutes'] if status_row else 30
            },
            'msg': 'success'
        })

    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return jsonify({
            'success': False,
            'code': 500,
            'data': None,
            'msg': str(e)
        })

# 启动定时任务
def start_following_videos_service():
    """启动关注视频服务"""
    manager.start_scheduler()
    logger.info("关注用户视频管理服务已启动")
