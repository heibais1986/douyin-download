# -*- encoding: utf-8 -*-
'''
@File    :   douyin.py
@Time    :   2024年07月16日 12:06:14 星期二
@Author  :   erma0
@Version :   1.0
@Link    :   https://github.com/erma0
@Desc    :   抖音爬虫
'''

import os
import re
from threading import Lock
from typing import List
from urllib.parse import parse_qs, quote, unquote, urlparse

import ujson as json
from loguru import logger

try:
    from .download import download
    from .request import Request
    from .util import quit, save_json, str_to_path, url_redirect
except ImportError:
    # 当作为独立模块运行时使用绝对导入
    from download import download
    from request import Request
    from util import quit, save_json, str_to_path, url_redirect


class Douyin(object):

    def __init__(self, target: str = '', limit: int = 0, type: str = 'post', down_path: str = '下载', cookie: str = '', proxy_url: str = ''):
        """
        初始化信息
        """
        self.target = target
        self.limit = limit
        self.type = type

        self.down_path = os.path.join('.', down_path)
        if not os.path.exists(self.down_path):
            os.makedirs(self.down_path)

        self.has_more = True
        self.results_old = []
        self.results = []
        self.lock = Lock()

        self.request = Request(cookie, proxy_url=proxy_url)

    def run(self):

        self.__get_target_info()

        if self.type in ['user', 'follow', 'fans']:
            self.get_awemes_list()
        # elif self.type in ['live']:
        #     pass
        elif self.type in ['post', 'like', 'favorite', 'search', 'music', 'hashtag', 'collection']:
            self.get_awemes_list()
        elif self.type in ['video', 'note']:
            # self.get_aweme()
            self.get_aweme_detail()
        else:  # 其他情况
            quit(f'获取目标类型错误, type: {self.type}')

    def __get_target_id(self):
        if self.target:  # 根据输入目标自动判断部分类型
            target = self.target.strip()
            hostname = urlparse(target).hostname
            # 输入链接
            if hostname and hostname.endswith('douyin.com'):
                if hostname == 'v.douyin.com':
                    target = url_redirect(target)
                *_, _type, id = unquote(urlparse(target).path.strip('/')).split('/')
                self.url = target
                # 自动识别 单个作品 搜索、音乐、合集
                if _type in ['video', 'note', 'music', 'hashtag', 'collection']:
                    self.type = _type
                    if self.type in ['video', 'note']:
                        self.url = f'https://www.douyin.com/note/{id}'
                elif _type == 'search':
                    id = unquote(id)
                    search_type = parse_qs(urlparse(target).query).get('type')
                    if search_type is None or search_type[0] in ['video', 'general']:
                        self.type = 'search'
                    else:
                        self.type = search_type[0]
            # 输入非链接
            else:
                id = target
                if self.type in ['search', 'user', 'live']:  # 搜索 视频 用户 直播间
                    self.url = f'https://www.douyin.com/search/{quote(id)}'
                    # if self.type == 'search':
                    #     self.url = f'{self.url}?type=video'
                    # else:
                    #     self.url = f'{self.url}?type={self.type}'
                # 数字ID: 单个作品id 音乐id 合集id
                elif self.type in ['video', 'note', 'music', 'hashtag', 'collection'] and id.isdigit():
                    if self.type in ['video', 'note']:
                        self.url = f'https://www.douyin.com/note/{id}'
                    self.url = f'https://www.douyin.com/{self.type}/{id}'
                # 用户uid
                elif self.type in ['post', 'like', 'favorite', 'follow', 'fans'] and id.startswith('MS4wLjABAAAA'):
                    self.url = f'https://www.douyin.com/user/{id}'
                else:  # 其他情况
                    quit(f'[{id}]目标输入错误，请检查参数')
        else:  # 未输入目标，直接采集本账号数据
            id = self.__get_self_uid()
            self.url = 'https://www.douyin.com/user/self'
        self.id = id

    def __get_target_info(self):
        self.__get_target_id()

        # 目标信息
        if self.type in ['search', 'user', 'live']:
            # 想要访问搜索界面 需要UA与cookie对应 后续api请求需要修改参数中的浏览器版本号
            # 直接跳过这一步
            self.title = self.id
        elif self.type in ['video', 'note']:
            # 通过api获取
            # 页面源码获取的结果存在部分无法下载的情况
            self.title = self.id
        elif self.type in ['post', 'like', 'favorite', 'follow', 'fans']:
            # 对于用户相关类型，直接通过API获取用户信息，不依赖页面解析
            try:
                self.get_user()
                self.title = self.info.get('nickname', self.id) if hasattr(self, 'info') and self.info else self.id
            except Exception as e:
                logger.warning(f"通过API获取用户信息失败，尝试页面解析: {e}")
                # 如果API失败，再尝试页面解析
                try:
                    text = self.request.getHTML(self.url)
                    pattern = r'self\.__pace_f\.push\(\[1,"\d:\[\S+?({[\s\S]*?})\]\\n"\]\)</script>'
                    render_data: str = re.findall(pattern, text)
                    if render_data:
                        render_data = render_data[-1].replace(
                            '\\"', '"').replace('\\\\', '\\')
                        self.render_data = json.loads(render_data)
                        self.info = self.render_data['user']['user']
                        self.title = self.info['nickname']
                    else:
                        # 如果页面解析也失败，使用默认值
                        logger.warning("页面解析也失败，使用默认用户信息")
                        self.title = self.id
                        self.info = {'nickname': self.id}
                except Exception as page_error:
                    logger.error(f"页面解析失败: {page_error}")
                    self.title = self.id
                    self.info = {'nickname': self.id}
        else:
            # 其他类型仍使用原有的页面解析方法
            text = self.request.getHTML(self.url)
            pattern = r'self\.__pace_f\.push\(\[1,"\d:\[\S+?({[\s\S]*?})\]\\n"\]\)</script>'
            render_data: str = re.findall(pattern, text)
            if render_data:
                render_data = render_data[-1].replace(
                    '\\"', '"').replace('\\\\', '\\')
                self.render_data = json.loads(render_data)
                if self.type == 'collection':
                    self.info = self.render_data['aweme']['detail']['mixInfo']
                    self.title = self.info['mixName']
                elif self.type == 'music':
                    self.info = self.render_data['musicDetail']
                    self.title = self.info['title']
                elif self.type == 'hashtag':
                    self.info = self.render_data['topicDetail']
                    self.title = self.info['chaName']
                else:  # 其他情况
                    raise Exception(f'获取目标信息请求失败, type: {self.type}')
            else:
                raise Exception(f'提取目标信息失败，可能是cookie无效。url: {self.url}')
        # 对于web_monitor调用，不再重复创建用户文件夹
        # 因为web_monitor已经创建了按日期和昵称组织的路径
        # 注释掉旧的用户文件夹创建逻辑
        # if not hasattr(self, '_skip_user_folder'):
        #     user_folder = str_to_path(f'{self.type}_{self.title}')
        #     self.down_path = os.path.normpath(os.path.join(self.down_path, user_folder))
        
        # 为web_monitor调用创建userinfo目录与下载目录同级来存放.json和.txt文件
        if hasattr(self, '_skip_user_folder'):
            # 获取下载目录的父目录（日期目录的父目录）
            parent_path = os.path.dirname(os.path.dirname(self.down_path))
            userinfo_path = os.path.join(parent_path, 'userinfo')
            os.makedirs(userinfo_path, exist_ok=True)
            self.aria2_conf = os.path.join(userinfo_path, f'{self.type}_{self.title}.txt')
            self.json_save_path = os.path.join(userinfo_path, f'{self.type}_{self.title}')
        else:
            self.aria2_conf = f'{self.down_path}.txt'
            self.json_save_path = self.down_path
        
        # 确保目录存在
        os.makedirs(self.down_path, exist_ok=True)
        # 增量采集，先取回旧数据
        if self.type == 'post':
            json_file_path = f'{self.json_save_path}.json'
            if os.path.exists(json_file_path) and not self.results_old:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    self.results_old = json.load(f)

    def __get_self_uid(self):
        url = 'https://www.douyin.com/user/self'
        text = self.request.getHTML(url)
        if text == '':
            quit(f'获取UID请求失败, url: {url}')
        pattern = r'secUid\\":\\"([-\w]+)\\"'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            quit(f'获取UID请求失败, url: {url}')

    def get_aweme(self):
        if self.render_data.get('aweme', None):
            render_data_ls = [self.render_data['aweme']['detail']]
            self.__append_awemes(render_data_ls)
            self.save()
        else:
            quit('作品详情获取失败，未获取到页面数据')

    def get_aweme_detail(self) -> tuple[dict, bool]:
        params = {"aweme_id": self.id}
        uri = '/aweme/v1/web/aweme/detail/'
        resp = self.request.getJSON(uri, params)
        aweme_detail = resp.get('aweme_detail', {})
        if aweme_detail:
            self.__append_awemes([aweme_detail])
            self.save()
        else:
            quit('作品详情获取失败')

    def get_user(self):
        params = {
            "publish_video_strategy_type": 2,
            "sec_user_id": self.id, 
            "personal_center_strategy": 1,
            "source": "channel_pc_web",
            "profile_other_record_enable": 1,
            "land_to": 1,
            "support_h265": 1,
            "support_dash": 1
        }
        
        # 首先尝试主要API
        resp = self.request.getJSON('/aweme/v1/web/user/profile/other/', params)
        logger.success(f"----------------主要API响应: {resp}")
        if resp and resp.get('user'):
            self.info = resp.get('user', {})
            logger.success(f"成功获取用户信息: {self.info.get('nickname', '未知用户')}")
        else:
            logger.warning("主要API失败，尝试备用方法")
            # 尝试备用API
            try:
                self.get_user_v2()
                if hasattr(self, 'info') and self.info:
                    logger.success(f"备用方法成功获取用户信息: {self.info.get('nickname', '未知用户')}")
                else:
                    raise Exception("备用方法也无法获取用户信息")
            except Exception as e:
                logger.error(f"所有获取用户信息的方法都失败: {e}")
                # 不再直接退出程序，而是抛出异常让上层处理
                raise Exception('无法获取用户信息，可能是Cookie失效或网络问题')
        
        # 设置下载路径
        if hasattr(self, 'info') and self.info:
            # 对于web_monitor调用，不再重复创建用户文件夹
            # 注释掉旧的用户文件夹创建逻辑
            # if not hasattr(self, '_skip_user_folder'):
            #     user_folder = str_to_path(f"{self.info['nickname']}_{self.id}")
            #     self.down_path = os.path.normpath(os.path.join(self.down_path, user_folder))
            
            # 为web_monitor调用创建userinfo目录与下载目录同级来存放.json和.txt文件
            if hasattr(self, '_skip_user_folder'):
                # 获取下载目录的父目录（日期目录的父目录）
                parent_path = os.path.dirname(os.path.dirname(self.down_path))
                userinfo_path = os.path.join(parent_path, 'userinfo')
                os.makedirs(userinfo_path, exist_ok=True)
                self.aria2_conf = os.path.join(userinfo_path, f'{self.type}_{self.info["nickname"]}.txt')
                self.json_save_path = os.path.join(userinfo_path, f'{self.type}_{self.info["nickname"]}')
            else:
                self.aria2_conf = f'{self.down_path}.txt'
                self.json_save_path = self.down_path
            
            # 确保目录存在
            os.makedirs(self.down_path, exist_ok=True)
            
            json_file_path = f'{self.json_save_path}.json'
            if os.path.exists(json_file_path) and not self.results_old:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    self.results_old = json.load(f)

    def get_user_v2(self):
        # 使用备用API获取用户信息
        params = {
            'sec_uid': self.id,
            'device_platform': 'webapp',
            'aid': '6383'
        }
        
        try:
            resp = self.request.getJSON('/web/api/v2/user/info/', params)
            if resp and resp.get('user_info'):
                self.info = resp['user_info']
                logger.info(f"备用API成功获取用户信息: {self.info.get('nickname', '未知用户')}")
            else:
                # 尝试另一个备用方法
                logger.warning("备用API也失败，尝试第三种方法")
                resp = self.request.getJSON('/aweme/v1/web/im/user/info/', {'sec_user_id': self.id})
                if resp and resp.get('user'):
                    self.info = resp['user']
                    logger.info(f"第三种方法成功获取用户信息: {self.info.get('nickname', '未知用户')}")
                else:
                    raise Exception("所有备用方法都失败")
        except Exception as e:
            logger.error(f"get_user_v2失败: {e}")
            raise Exception(f'备用方法获取用户信息失败: {e}')

    def get_awemes_list(self):
        max_cursor = 0
        logid = ''
        retry = 0
        max_retry = 10
        data = {}
        while self.has_more:
            try:
                # ['post', 'like', 'favorite', 'search', 'music','hashtag', 'collection']
                if self.type == 'post':
                    uri = '/aweme/v1/web/aweme/post/'
                    params = {"publish_video_strategy_type": 2, "max_cursor": max_cursor, "locate_query": False,
                              'show_live_replay_strategy': 1, 'need_time_list': 0, 'time_list_query': 0, 'whale_cut_token': '', 'count': 5, "sec_user_id": self.id
                              }
                elif self.type == 'like':
                    uri = '/aweme/v1/web/aweme/favorite/'
                    params = {"publish_video_strategy_type": 2, "max_cursor": max_cursor,
                              'cut_version': 1, 'count': 18, "sec_user_id": self.id}
                elif self.type == 'favorite':
                    uri = '/aweme/v1/web/aweme/listcollection/'
                    params = {"publish_video_strategy_type": 2}
                    data = {"cursor": max_cursor, 'count': 18}
                elif self.type == 'music':
                    uri = '/aweme/v1/web/music/aweme/'
                    params = {"cursor": max_cursor,
                              'count': 18, "music_id": self.id}
                elif self.type == 'hashtag':
                    uri = '/aweme/v1/web/challenge/aweme/'
                    params = {"cursor": max_cursor, "sort_type": 1,  # 0综合 1最热 2最新
                              'count': 18, "ch_id": self.id}
                elif self.type == 'collection':
                    uri = '/aweme/v1/web/mix/aweme/'
                    params = {"cursor": max_cursor,
                              'count': 18, "mix_id": self.id}
                elif self.type == 'search':
                    uri = '/aweme/v1/web/search/item/'  # 视频
                    params = {
                        "search_id": logid,
                        "search_channel": "aweme_video_web",
                        "search_source": "tab_search",
                        "query_correct_type": 1,
                        "from_group_id": "",
                        "is_filter_search": 1,
                        "list_type": "single",
                        "need_filter_settings": 1,
                        "offset": max_cursor,
                        "sort_type": 1,  # 排序 综合 1最多点赞 2最新
                        "enable_history": 1,
                        "search_range": 0,  # 搜索范围  不限
                        "publish_time": 0,  # 发布时间  不限
                        "filter_duration": '',  # 时长 不限 0-1  1-5  5-10000
                        'count': 18,
                        "keyword": unquote(self.id)
                    }
                elif self.type == 'user':
                    uri = '/aweme/v1/web/discover/search/'  # 用户
                    params = {
                        'count': 10,
                        "from_group_id": "",
                        "is_filter_search": 0,
                        "keyword": quote(self.id),
                        "list_type": "single",
                        "need_filter_settings": 0,
                        "offset": max_cursor,
                        "search_id": logid,
                        "query_correct_type": 1,
                        "search_channel": "aweme_user_web",
                        "search_source": "tab_search"
                    }
                elif self.type == 'live':
                    uri = '/aweme/v1/web/discover/search/'
                    params = {}
                elif self.type == 'follow':
                    uri = '/aweme/v1/web/user/following/list/'
                    params = {
                        "address_book_access": 0,
                        "count": 20,
                        "gps_access": 0,
                        "is_top": 1,
                        "max_time": max_cursor,
                        "min_time": 0,
                        "offset": 0,
                        'source_type': 1,
                        "sec_user_id": self.id
                    }
                elif self.type == 'fans':
                    uri = '/aweme/v1/web/user/follower/list/'
                    params = {
                        "address_book_access": 0,
                        "count": 20,
                        "gps_access": 0,
                        "is_top": 1,
                        "max_time": max_cursor,
                        "min_time": 0,
                        "offset": 0,
                        'source_type': 3,
                        "sec_user_id": self.id
                    }

                resp = self.request.getJSON(uri, params, data)
                for name in ['max_cursor', 'cursor', 'min_time']:
                    max_cursor = resp.get(name, 0)
                    if max_cursor:
                        break
                if not logid:
                    logid = resp['log_pb']['impr_id']
                self.has_more = resp.get('has_more', 0)
                for name in ['aweme_list', 'user_list', 'data', 'followings', 'followers']:
                    items_list = resp.get(name, [])
                    if items_list:
                        break
            except:
                retry += 1
                logger.error(f'采集请求出错... 进行第{retry}次重试')
                continue
            finally:
                # 重试max_retry次
                if retry >= max_retry:
                    self.has_more = False

            if items_list:
                retry = 0
                if self.type in ['post', 'like', 'favorite', 'search', 'music', 'hashtag', 'collection']:
                    self.__append_awemes(items_list)
                elif self.type in ['user', 'live', 'follow', 'fans']:
                    self.__append_users(items_list)
                else:
                    quit(f'类型错误，type：{self.type}')
            elif self.has_more:
                retry += 1
                logger.error(f'采集未完成，但请求结果为空... 进行第{retry}次重试')
            else:
                # logger.info('未采集到结果')
                pass
        self.save()

    def __append_awemes(self, awemes_list: List[dict]):
        with self.lock:  # 加锁避免意外冲突
            if self.limit == 0 or len(self.results) < self.limit:
                for item in awemes_list:
                    # =====兼容搜索=====
                    if item.get('aweme_info'):
                        item = item['aweme_info']
                    # =====限制数量=====
                    if self.limit > 0 and len(self.results) >= self.limit:
                        self.has_more = False
                        logger.info(f'已达到限制采集数量： {len(self.results)}')
                        return
                    # =====增量采集=====
                    _time = item.get('create_time', item.get('createTime'))
                    if self.results_old:
                        old = self.results_old[0]['time']
                        if _time <= old:  # 如果当前作品时间早于上次采集的最新作品时间，直接退出
                            _is_top = item.get(
                                'is_top', item.get('tag', {}).get('isTop'))
                            if _is_top:  # 置顶作品，不重复保存
                                continue
                            if self.has_more:
                                self.has_more = False
                            logger.success(f'增量采集完成，上次运行结果：{old}')
                            return
                    # =====保存结果=====
                    # _type = item.get('media_type', item.get('media_type'))  # 2 图集 4 视频
                    _type = item.get('aweme_type', item.get('awemeType'))
                    aweme: dict = item.get('statistics', item.get('stats', {}))
                    for i in [
                            'playCount', 'downloadCount', 'forwardCount', 'collectCount', "digest", "exposure_count",
                            "live_watch_count", "play_count", "download_count", "forward_count", "lose_count",
                            "lose_comment_count"
                    ]:
                        if not aweme.get(i):
                            aweme.pop(i, '')
                    if _type <= 66 or _type in [69, 107]:  # 视频 77西瓜视频
                        play_addr = item['video'].get('play_addr')
                        if play_addr:
                            download_addr = play_addr['url_list'][-1]
                        else:
                            # download_addr = f"https:{item['video']['playApi']}"
                            download_addr: str = item['download']['urlList'][-1]
                            download_addr = download_addr.replace(
                                'watermark=1', 'watermark=0')
                        aweme['download_addr'] = download_addr
                    elif _type == 68:  # 图文
                        aweme['download_addr'] = [images.get('url_list', images.get(
                            'urlList'))[-1] for images in item['images']]
                    elif _type == 101:  # 直播
                        continue
                    else:  # 其他类型作品
                        aweme['download_addr'] = '其他类型作品'
                        logger.info('其他类型作品：type', _type)
                        save_json(_type, item)  # 保存未区分的类型
                        continue
                    aweme.pop('aweme_id', '')
                    aweme['id'] = item.get('aweme_id', item.get('awemeId'))
                    aweme['time'] = _time
                    aweme['type'] = _type
                    desc = str_to_path(item.get('desc'))
                    aweme['desc'] = desc
                    aweme['duration'] = item.get(
                        'duration', item['video'].get('duration'))
                    music: dict = item.get('music')
                    if music:
                        aweme['music_title'] = str_to_path(music['title'])
                        aweme['music_url'] = music.get(
                            'play_url', music.get('playUrl'))['uri']
                    cover = item['video'].get('cover')
                    if type(cover) is dict:
                        aweme['cover'] = cover['url_list'][-1]
                    else:
                        aweme['cover'] = f"https:{
                            item['video']['dynamicCover']}"
                    author = item.get('author', item.get('authorInfo'))
                    if author:
                        avatarThumb = author.get(
                            'avatar_thumb', author.get('avatarThumb'))
                        aweme['author_avatar'] = avatarThumb.get(
                            'url_list', avatarThumb.get('urlList'))[-1]
                        aweme['author_nickname'] = author.get('nickname')
                        aweme['author_uid'] = author.get(
                            'sec_uid', author.get('secUid'))
                    text_extra = item.get('text_extra', item.get('textExtra'))
                    if text_extra:
                        aweme['text_extra'] = [{
                            'tag_id': hashtag.get('hashtag_id', hashtag.get('hashtagId')),
                            'tag_name': hashtag.get('hashtag_name', hashtag.get('hashtagName'))
                        } for hashtag in text_extra]
                    # video_tag = item.get('video_tag', item.get('videoTag'))
                    # if video_tag:
                    #     aweme['video_tag'] = video_tag

                    if self.type == 'collection':
                        aweme['no'] = item['mix_info']['statis']['current_episode']
                    self.results.append(aweme)  # 用于保存信息

                logger.info(f'采集中，已采集到 {len(self.results)} 条结果')
            else:
                self.has_more = False
                logger.info(f'已达到限制采集数量： {len(self.results)}')

    def __append_users(self, user_list: List[dict]):
        with self.lock:  # 加锁避免意外冲突
            if self.limit == 0 or len(self.results) < self.limit:
                for item in user_list:
                    # =====兼容搜索=====
                    if item.get('user_info'):
                        item = item['user_info']
                    # =====限制数量=====
                    if self.limit > 0 and len(self.results) >= self.limit:
                        self.has_more = False
                        logger.info(f'已达到限制采集数量： {len(self.results)}')
                        return
                    user_info = {}
                    user_info['nickname'] = str_to_path(item['nickname'])
                    user_info['signature'] = str_to_path(item['signature'])
                    user_info['avatar'] = item['avatar_thumb']['url_list'][0]
                    for i in [
                            'sec_uid', 'uid', 'short_id', 'unique_id', 'unique_id_modify_time', 'aweme_count', 'favoriting_count',
                            'follower_count', 'following_count', 'constellation', 'create_time', 'enterprise_verify_reason',
                            'is_gov_media_vip', 'live_status', 'total_favorited', 'share_qrcode_uri'
                    ]:
                        if item.get(i):
                            user_info[i] = item[i]
                    room_id = item.get('room_id')
                    if room_id:  # 直播间信息
                        user_info['live_room_id'] = room_id
                        user_info['live_room_url'] = [
                            f'http://pull-flv-f26.douyincdn.com/media/stream-{
                                room_id}.flv',
                            f'http://pull-hls-f26.douyincdn.com/media/stream-{
                                room_id}.m3u8'
                        ]
                    musician: dict = item.get('original_musician')
                    if musician and musician.get('music_count'):  # 原创音乐人
                        user_info['original_musician'] = item['original_musician']
                    self.results.append(user_info)  # 用于保存信息
                logger.info(f'采集中，已采集到 {len(self.results)} 条结果')
            else:
                self.has_more = False
                logger.info(f'已达到限制采集数量： {len(self.results)}')

    def download_all(self):
        """
        采集完成后，统一下载已采集的结果
        """
        if self.type not in ['user', 'follow', 'fans', 'live']:
            download(self.down_path, self.aria2_conf)

    def get_awemes(self):
        """获取视频列表，用于监控器调用"""
        self.__get_target_info()
        self.get_awemes_list()
        return self.results

    def save(self):
        if self.results:
            logger.success(f'采集完成，本次共采集到 {len(self.results)} 条结果')
            # 确保aria2配置文件的目录存在
            aria2_dir = os.path.dirname(self.aria2_conf)
            if aria2_dir:
                os.makedirs(aria2_dir, exist_ok=True)
            # 保存下载配置文件
            _ = []
            with open(self.aria2_conf, 'w', encoding='utf-8') as f:
                # 保存主页链接
                if self.type in ['user', 'follow', 'fans', 'live']:
                    _ = [
                        f"https://www.douyin.com/user/{line.get('sec_uid', 'None')}\n" for line in self.results
                        if line.get('sec_uid', None)
                    ]
                # 保存作品下载配置
                else:
                    for line in self.results:  # 只下载本次采集结果
                        # 使用标题_发布时间作为文件名（可读格式）
                        timestamp = line['time']
                        if timestamp:
                            try:
                                from datetime import datetime
                                formatted_time = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d_%H-%M-%S')
                            except:
                                formatted_time = str(timestamp)
                        else:
                            formatted_time = 'unknown_time'

                        filename = f"{line['desc']}_{formatted_time}"
                        if self.type == 'collection':
                            filename = f'第{line['no']}集_{filename}'
                        if type(line["download_addr"]) is list:
                            if self.type == 'video':
                                down_path = self.down_path.replace(
                                    line["id"], filename)
                            else:
                                down_path = os.path.join(
                                    self.down_path, filename)
                            for index, addr in enumerate(line["download_addr"]):
                                _.append(f'{addr}\n\tdir={down_path}\n\tout={
                                    line["id"]}_{index + 1}.jpeg\n')

                        elif type(line["download_addr"]) is str:
                            # # 提供UA和cookie
                            # _.append(
                            #     f'{line["download_addr"]}\n\tdir={self.down_path}\n\tout={filename}.mp4\n\tuser-agent={
                            #         self.request.HEADERS.get("User-Agent")}\n\theader="Cookie:{cookies_dict_to_str(self.request.COOKIES)}"\n')
                            # 提供UA和msToken
                            # _.append(
                            #     f'{line["download_addr"]}\n\tdir={self.down_path}\n\tout={filename}.mp4\n\tuser-agent={
                            #         self.request.HEADERS.get("User-Agent")}\n\theader="Cookie:msToken={self.request.get_ms_token()}"\n')
                            # 提供UA
                            # _.append(
                            #     f'{line["download_addr"]}\n\tdir={self.down_path}\n\tout={
                            #         filename}.mp4\n\tuser-agent={self.request.HEADERS.get("User-Agent")}\n')
                            # 正常下载
                            _.append(f'{line["download_addr"]}\n\tdir={
                                     self.down_path}\n\tout={filename}.mp4\n')
                        else:
                            logger.error("下载地址错误")
                f.writelines(_)

            if self.type == 'post':
                # 保存所有数据到文件，包括旧数据
                self.results.sort(key=lambda item: item['id'], reverse=True)
                self.results.extend(self.results_old)
            save_json(f'{self.json_save_path}.json', self.results)

        else:
            logger.info("本次采集结果为空")
