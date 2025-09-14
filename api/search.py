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
@desc: 搜索
@url: /aweme/v1/web/general/search/single/
@param: keyword 关键词
@param: offset 游标
@param: count 默认 15
@param： filter_selected  {
  /**
   * 指定排序方式。
   * 0 - 综合排序
   * 1 - 最新发布
   * 3 - 最多点赞
   */
  sort_type?: 0 | 1 | 3

  /**
   * 指定发布时间的范围。
   * 0 - 不限
   * 1 - 一天内
   * 7 - 一周内
   * 180 - 半年内
   */
  public_time?: 0 | 1 | 7 | 180

  /**
   * 指定视频时长的筛选条件。
   * "" - 不限
   * "0-1" - 1分钟以下
   * "1-5" - 1-5分钟
   * "5-10000" - 5分钟以上
   */
  filter_duration?: '' | '0-1' | '1-5' | '5-10000'

  /**
   * 指定搜索范围。
   * "0" - 不限
   * "3" - 关注的人
   * "1" - 最近看过
   * "2" - 还未看过
   */
  search_range?: '0' | '3' | '1' | '2'

  /**
   * 指定内容类型。
   * "0" - 不限
   * "1" - 视频
   * "2" - 图文
   */
  content_type?: '0' | '1' | '2'
}
@param: is_filter_search = 1 | 0
@param: list_type= single | multi
'''


@api.route('/general/search/single/')
def get_search():
    keyword = request.args.get('keyword')
    offset = request.args.get('offset')
    count = request.args.get('count')
    filter_selected = request.args.get('filter_selected')
    is_filter_search = request.args.get('is_filter_search'),
    list_type = request.args.get('list_type')
    url = '/aweme/v1/web/general/search/single/'
    params = {
        'search_channel': 'aweme_general',
        'enable_history': 'enable_history',
        'keyword': keyword,
        'query_correct_type': '1',
        'offset': offset,
        'count': count,
        'need_filter_settings': 'need_filter_settings',
        'list_type': list_type
    }
    if is_filter_search == 1:
        params['filter_selected'] = filter_selected

    print(params)
    search_data = request_instance.getJSON(url, params)
    if search_data:
        return jsonify(search_data)
    else:
        return jsonify({'error': 'Failed to retrieve search_data; Check you Cookie and Referer!'}), 403


'''
@desc: 获取推荐词
@url: '/aweme/v1/web/api/suggest_words/'
@param: query 查询词
@param: count 数量
@param: from_group_id 从视频信息中获取
'''


@api.route('/api/suggest_words/')
def get_suggest_words():
    query = request.args.get('query')
    count = request.args.get('count')
    from_group_id = request.args.get('from_group_id')
    url = '/aweme/v1/web/api/suggest_words/'
    params = {
        'count': count,
        'business_id': '30068'
    }
    if from_group_id is not None and from_group_id != '':
        params['from_group_id'] = from_group_id
    if query is not None and query != '':
        params['query'] = query

    suggest_words = request_instance.getJSON(url, params)
    if suggest_words:
        return jsonify(suggest_words)
    else:
        return jsonify({'error': 'Failed to retrieve suggest_words; Check you Cookie and Referer!'}), 403
