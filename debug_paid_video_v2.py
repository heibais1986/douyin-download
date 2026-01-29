#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
付费视频下载调试程序 - 增强版
尝试多种方法获取付费视频信息
"""

import os
import sys
import json
import time
from urllib.parse import urlparse, parse_qs, quote

# 添加lib路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from lib.request import Request
from lib.util import save_json
from loguru import logger

class EnhancedPaidVideoDebugger:
    def __init__(self, cookie_file='cookie.txt'):
        self.cookie_file = cookie_file
        self.cookie = self.load_cookie()
        self.request = Request(cookie=self.cookie)

        # 目标视频信息
        self.user_id = 'MS4wLjABAAAACmSUqa6ZnHbY6NAlLzSMtwlwrB6rDGdpexV4gKRZG44'
        self.modal_id = '7593697878351121705'
        self.video_id = '7593696686543883561'

    def load_cookie(self):
        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookie_content = f.read().strip()
                logger.info(f"Cookie加载成功，长度: {len(cookie_content)}")
                return cookie_content
        except Exception as e:
            logger.error(f"加载cookie失败: {e}")
            return ''

    def test_basic_connectivity(self):
        """测试基本连接性"""
        logger.info("=== 测试基本连接性 ===")

        # 测试获取用户信息页面
        try:
            url = f'https://www.douyin.com/user/{self.user_id}'
            text = self.request.getHTML(url)
            if text and len(text) > 1000:
                logger.success(f"成功获取用户信息页面，长度: {len(text)}")
                # 检查是否有付费内容标识
                if '付费' in text or 'paid' in text.lower():
                    logger.info("页面包含付费内容标识")
                return True
            else:
                logger.error("获取用户信息页面失败")
                return False
        except Exception as e:
            logger.error(f"测试连接性异常: {e}")
            return False

    def get_video_page_directly(self):
        """直接获取视频页面源码"""
        logger.info("=== 直接获取视频页面源码 ===")

        try:
            # 构造视频页面URL
            video_url = f'https://www.douyin.com/video/{self.video_id}'
            logger.info(f"请求视频页面: {video_url}")

            text = self.request.getHTML(video_url)
            if text and len(text) > 1000:
                logger.success(f"成功获取视频页面，长度: {len(text)}")

                # 查找render_data
                pattern = r'self\.__pace_f\.push\(\[1,"[^"]*(\{[^}]*\})[^"]*"\]\)</script>'
                import re
                render_data_match = re.search(pattern, text)
                if render_data_match:
                    render_data_str = render_data_match.group(1)
                    logger.info("找到render_data")
                    try:
                        render_data = json.loads(render_data_str)
                        self.analyze_render_data(render_data)
                        return render_data
                    except json.JSONDecodeError as e:
                        logger.error(f"解析render_data失败: {e}")
                        return None
                else:
                    logger.warning("未找到render_data")
                    return None
            else:
                logger.error("获取视频页面失败")
                return None
        except Exception as e:
            logger.error(f"获取视频页面异常: {e}")
            return None

    def analyze_render_data(self, render_data):
        """分析render_data"""
        logger.info("=== 分析render_data ===")

        if 'aweme' in render_data and 'detail' in render_data['aweme']:
            aweme = render_data['aweme']['detail']
            logger.info(f"视频ID: {aweme.get('aweme_id')}")
            logger.info(f"描述: {aweme.get('desc')}")

            # 检查付费状态
            if aweme.get('is_paid_content'):
                logger.warning("这是付费内容！")

            # 视频信息
            video = aweme.get('video', {})
            logger.info(f"视频信息: {json.dumps(video, ensure_ascii=False, indent=2)}")

            # 播放地址
            play_addr = video.get('play_addr', {})
            if play_addr:
                logger.info("找到播放地址！")
                for url in play_addr.get('url_list', []):
                    logger.info(f"播放URL: {url}")

            # 下载地址
            download_addr = video.get('download_addr', {})
            if download_addr:
                logger.info("找到下载地址！")
                for url in download_addr.get('url_list', []):
                    logger.info(f"下载URL: {url}")

    def try_different_apis(self):
        """尝试不同的API端点"""
        logger.info("=== 尝试不同API端点 ===")

        apis_to_try = [
            {
                'name': '标准视频详情API',
                'uri': '/aweme/v1/web/aweme/detail/',
                'params': {"aweme_id": self.video_id}
            },
            {
                'name': '模态框视频详情API',
                'uri': '/aweme/v1/web/aweme/modal/detail/',
                'params': {"aweme_id": self.video_id, "modal_id": self.modal_id}
            },
            {
                'name': '付费内容API',
                'uri': '/aweme/v1/web/paid/content/detail/',
                'params': {"aweme_id": self.video_id}
            },
            {
                'name': '商品详情API',
                'uri': '/aweme/v1/web/goods/detail/',
                'params': {"goods_id": self.modal_id}  # 假设modal_id是商品ID
            }
        ]

        results = {}
        for api in apis_to_try:
            logger.info(f"尝试API: {api['name']}")
            try:
                resp = self.request.getJSON(api['uri'], api['params'])
                if resp and resp.get('status_code') == 0:
                    logger.success(f"{api['name']} 成功！")
                    results[api['name']] = resp
                    self.analyze_api_response(resp)
                else:
                    logger.warning(f"{api['name']} 失败: {resp}")
            except Exception as e:
                logger.error(f"{api['name']} 异常: {e}")

        return results

    def analyze_api_response(self, resp):
        """分析API响应"""
        logger.info("API响应分析:")

        # 检查是否有视频数据
        aweme_detail = resp.get('aweme_detail') or resp.get('aweme')
        if aweme_detail:
            video = aweme_detail.get('video', {})
            if video.get('play_addr'):
                logger.success("找到播放地址！")
                for url in video['play_addr'].get('url_list', []):
                    logger.info(f"播放URL: {url}")
                    self.test_download_url(url)

            if video.get('download_addr'):
                logger.success("找到下载地址！")
                for url in video['download_addr'].get('url_list', []):
                    logger.info(f"下载URL: {url}")
                    self.test_download_url(url)

    def test_download_url(self, url):
        """测试下载URL"""
        logger.info(f"测试下载URL: {url[:100]}...")

        try:
            import requests
            headers = {
                'User-Agent': self.request.HEADERS.get('User-Agent'),
                'Referer': 'https://www.douyin.com/'
            }

            response = requests.head(url, headers=headers, cookies=self.request.COOKIES, timeout=10, allow_redirects=True)
            logger.info(f"响应状态码: {response.status_code}")

            if response.status_code == 200:
                logger.success("下载URL测试成功")
                content_length = response.headers.get('Content-Length')
                if content_length:
                    logger.info(f"文件大小: {int(content_length) / 1024 / 1024:.2f} MB")
                return True
            elif response.status_code == 302:
                logger.info(f"重定向到: {response.headers.get('Location')}")
                return True
            else:
                logger.error(f"下载URL测试失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"测试下载URL异常: {e}")
            return False

    def debug_paid_video_comprehensive(self):
        """综合调试付费视频"""
        logger.info("=== 开始综合调试付费视频 ===")

        # 1. 测试基本连接性
        if not self.test_basic_connectivity():
            logger.error("基本连接性测试失败，可能网络或cookie问题")
            return

        # 2. 尝试直接获取页面
        page_data = self.get_video_page_directly()
        if page_data:
            logger.success("页面解析成功")
        else:
            logger.warning("页面解析失败，尝试API方法")

        # 3. 尝试不同API
        api_results = self.try_different_apis()

        # 4. 保存调试结果
        debug_info = {
            'timestamp': int(time.time()),
            'cookie_length': len(self.cookie),
            'page_data': page_data,
            'api_results': api_results
        }
        save_json('paid_video_debug_comprehensive.json', debug_info)
        logger.success("调试结果已保存到 paid_video_debug_comprehensive.json")

def main():
    logger.info("=== 付费视频增强调试程序 ===")

    debugger = EnhancedPaidVideoDebugger()

    if not debugger.cookie:
        logger.error("未找到有效cookie")
        return

    debugger.debug_paid_video_comprehensive()

if __name__ == "__main__":
    main()