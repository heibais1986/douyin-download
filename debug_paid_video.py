#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
付费视频下载调试程序
用于分析付费视频的下载API和流程
"""

import os
import sys
import json
import time
from urllib.parse import urlparse, parse_qs

# 添加lib路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from lib.request import Request
from lib.util import save_json
from loguru import logger

class PaidVideoDebugger:
    def __init__(self, cookie_file='cookie.txt'):
        """初始化付费视频调试器"""
        self.cookie_file = cookie_file
        self.cookie = self.load_cookie()
        self.request = Request(cookie=self.cookie)

        # 目标视频信息
        self.user_id = 'MS4wLjABAAAACmSUqa6ZnHbY6NAlLzSMtwlwrB6rDGdpexV4gKRZG44'
        self.modal_id = '7593697878351121705'
        self.video_id = '7593696686543883561'

    def load_cookie(self):
        """加载cookie文件"""
        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookie_content = f.read().strip()
                logger.info(f"成功加载cookie文件，长度: {len(cookie_content)}")
                return cookie_content
        except Exception as e:
            logger.error(f"加载cookie文件失败: {e}")
            return ''

    def get_video_detail(self):
        """获取视频详情"""
        logger.info("=== 获取视频详情 ===")
        params = {"aweme_id": self.video_id}

        try:
            resp = self.request.getJSON('/aweme/v1/web/aweme/detail/', params)
            logger.info(f"视频详情API响应: {json.dumps(resp, ensure_ascii=False, indent=2)}")

            if resp and resp.get('aweme_detail'):
                aweme = resp['aweme_detail']
                logger.success(f"成功获取视频详情: {aweme.get('desc', '无描述')}")

                # 分析视频信息
                self.analyze_video_info(aweme)
                return aweme
            else:
                logger.error("获取视频详情失败")
                return None

        except Exception as e:
            logger.error(f"获取视频详情异常: {e}")
            return None

    def analyze_video_info(self, aweme):
        """分析视频信息"""
        logger.info("=== 分析视频信息 ===")

        # 基本信息
        logger.info(f"视频ID: {aweme.get('aweme_id')}")
        logger.info(f"描述: {aweme.get('desc')}")
        logger.info(f"创建时间: {aweme.get('create_time')}")
        logger.info(f"视频类型: {aweme.get('aweme_type')}")

        # 视频播放信息
        video = aweme.get('video', {})
        logger.info(f"视频信息: {json.dumps(video, ensure_ascii=False, indent=2)}")

        # 播放地址
        play_addr = video.get('play_addr', {})
        if play_addr:
            logger.info(f"播放地址URL列表: {play_addr.get('url_list', [])}")

        # 下载地址
        download_addr = video.get('download_addr', {})
        if download_addr:
            logger.info(f"下载地址: {json.dumps(download_addr, ensure_ascii=False)}")

        # 检查是否有付费相关字段
        if aweme.get('is_paid_content'):
            logger.warning("这是一个付费内容视频")

        # 检查商品信息
        goods_info = aweme.get('anchor_info', {}).get('goods_info', {})
        if goods_info:
            logger.info(f"商品信息: {json.dumps(goods_info, ensure_ascii=False)}")

        # 检查音乐信息
        music = aweme.get('music', {})
        if music:
            logger.info(f"音乐信息: {music.get('title', '无标题')}")

    def check_user_permissions(self):
        """检查用户权限"""
        logger.info("=== 检查用户权限 ===")

        params = {
            "publish_video_strategy_type": 2,
            "sec_user_id": self.user_id,
            "personal_center_strategy": 1,
            "source": "channel_pc_web",
            "profile_other_record_enable": 1,
            "land_to": 1,
            "support_h265": 1,
            "support_dash": 1
        }

        try:
            resp = self.request.getJSON('/aweme/v1/web/user/profile/other/', params)
            if resp and resp.get('user'):
                user_info = resp['user']
                logger.success(f"用户权限检查成功: {user_info.get('nickname', '未知用户')}")
                logger.info(f"用户付费状态: {user_info.get('paid_content_info', {})}")
                return user_info
            else:
                logger.error("用户权限检查失败")
                return None
        except Exception as e:
            logger.error(f"用户权限检查异常: {e}")
            return None

    def get_video_feed(self):
        """获取视频feed流"""
        logger.info("=== 获取视频Feed ===")

        params = {
            "publish_video_strategy_type": 2,
            "max_cursor": 0,
            "locate_query": False,
            'show_live_replay_strategy': 1,
            'need_time_list': 0,
            'time_list_query': 0,
            'whale_cut_token': '',
            'count': 5,
            "sec_user_id": self.user_id
        }

        try:
            resp = self.request.getJSON('/aweme/v1/web/aweme/post/', params)
            if resp and resp.get('aweme_list'):
                aweme_list = resp['aweme_list']
                logger.success(f"成功获取用户视频列表，数量: {len(aweme_list)}")

                # 查找目标视频
                target_video = None
                for aweme in aweme_list:
                    if aweme.get('aweme_id') == self.video_id:
                        target_video = aweme
                        break

                if target_video:
                    logger.success("在用户作品列表中找到目标视频")
                    self.analyze_video_info(target_video)
                    return target_video
                else:
                    logger.warning("在用户作品列表中未找到目标视频")
                    return None
            else:
                logger.error("获取视频feed失败")
                return None
        except Exception as e:
            logger.error(f"获取视频feed异常: {e}")
            return None

    def test_download_url(self, url):
        """测试下载URL"""
        logger.info(f"=== 测试下载URL: {url} ===")

        try:
            # 使用requests测试下载
            import requests
            headers = {
                'User-Agent': self.request.HEADERS.get('User-Agent'),
                'Referer': 'https://www.douyin.com/'
            }

            response = requests.head(url, headers=headers, cookies=self.request.COOKIES, timeout=10)
            logger.info(f"HEAD请求状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")

            if response.status_code == 200:
                logger.success("下载URL测试成功")
                return True
            else:
                logger.error(f"下载URL测试失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"测试下载URL异常: {e}")
            return False

    def debug_paid_video_flow(self):
        """调试付费视频下载流程"""
        logger.info("开始调试付费视频下载流程...")

        # 1. 检查用户权限
        user_info = self.check_user_permissions()
        if not user_info:
            logger.error("用户权限检查失败，无法继续")
            return

        # 2. 获取视频详情
        video_info = self.get_video_detail()
        if not video_info:
            logger.error("获取视频详情失败，尝试从feed获取")
            video_info = self.get_video_feed()

        if not video_info:
            logger.error("无法获取视频信息")
            return

        # 3. 分析下载地址
        video = video_info.get('video', {})
        play_addr = video.get('play_addr', {})
        download_addr = video.get('download_addr', {})

        # 尝试播放地址
        if play_addr and play_addr.get('url_list'):
            play_url = play_addr['url_list'][-1]
            logger.info(f"测试播放地址: {play_url}")
            self.test_download_url(play_url)

        # 尝试下载地址
        if download_addr and download_addr.get('url_list'):
            download_url = download_addr['url_list'][-1]
            logger.info(f"测试下载地址: {download_url}")
            self.test_download_url(download_url)

        # 4. 保存调试信息
        debug_info = {
            'user_info': user_info,
            'video_info': video_info,
            'timestamp': int(time.time())
        }
        save_json('paid_video_debug.json', debug_info)
        logger.success("调试信息已保存到 paid_video_debug.json")

def main():
    """主函数"""
    logger.info("=== 付费视频下载调试程序 ===")

    debugger = PaidVideoDebugger()

    if not debugger.cookie:
        logger.error("未找到有效的cookie，请确保cookie.txt文件存在")
        return

    debugger.debug_paid_video_flow()

if __name__ == "__main__":
    main()