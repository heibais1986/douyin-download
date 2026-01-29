# -*- encoding: utf-8 -*-
'''
@File    :   request.py
@Time    :   2024年07月15日
@Author  :   erma0
@Version :   1.1
@Link    :   https://github.com/ShilongLee/Crawler
@Desc    :   抖音sign
'''
import os
import time
import random
import re
from urllib.parse import quote

import requests
from loguru import logger

try:
    from .cookies import get_cookie_dict
    from .execjs_fix import execjs
except ImportError:
    # 当作为独立模块运行时使用绝对导入
    from cookies import get_cookie_dict
    from execjs_fix import execjs


class Request(object):

    HOST = 'https://www.douyin.com'
    PARAMS = {
        'device_platform': 'webapp',
        'aid': '6383',
        'channel': 'channel_pc_web',
        'publish_video_strategy_type': '2',
        'source': 'channel_pc_web',
        'personal_center_strategy': '1',
        'profile_other_record_enable': '1',
        'land_to': '1',
        'update_version_code': '170400',
        'pc_client_type': '1',
        'pc_libra_divert': 'Windows',
        'support_h265': '1',
        'support_dash': '1',
        'cpu_core_num': '8',
        'version_code': '170400',
        'version_name': '17.4.0',
        'cookie_enabled': 'true',
        'screen_width': '1920',
        'screen_height': '1080',
        'browser_language': 'zh-CN',
        'browser_platform': 'Win32',
        'browser_name': 'Chrome',
        'browser_version': '132.0.0.0',
        'browser_online': 'true',
        'engine_name': 'Blink',
        'engine_version': '132.0.0.0',
        'os_name': 'Windows',
        'os_version': '10',
        'device_memory': '8',
        'platform': 'PC',
        'downlink': '10',
        'effective_type': '4g',
        'round_trip_time': '100',
        'webid': '7513859400529511946',
        'uifid': 'e438e504399eecf9c2f65594851517a53fcd0a47c3feace6f386418d12bbc04df48e44884eb112db37fe72d5435d21b6da0e51b513a8cb2b57492a0995d24d772f6cfd3d1776b840aac469c3bdd9274a5f67289cc8fdef6814c7e117c0a032504fc0fd31a61a75788f2ca404226b0db6e3746e19a5c1bb329337a3502e5540f971d0f0c745c7015ee45edb56770785034669036d8896c8bfef34dfdc03af6852',
        'msToken': 'uGIyd_KgUAGjbJBiyk13cuMwGiS2smpcgDsocx3tgX6l4rNtiz7m2vkb877pQtHTDGgHVm--9n8eQt7kkEXK4_OhnD0rc8cRtnUKf2_rdui4rVWLta_OlKBunOA8FCle52dGsBL-ZgZDP2XXOVjnFNgeCqIMNuPYMqk_55dlUhBT',
        'verifyFp': 'verify_mirgbi90_b61T1WIC_kWGd_4IvP_BHWD_FQeiTEuA8hhI',
        'fp': 'verify_mirgbi90_b61T1WIC_kWGd_4IvP_BHWD_FQeiTEuA8hhI',
        'x-secsdk-web-signature': 'c8e0fe804acde75c18f4e1d30e314799',
    }
    HEADERS = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://www.douyin.com/user/MS4wLjABAAAAFFSebq0wtofl1v55ak14_sCqEotqFAnjBwz-6ZJ1J9Q?from_tab_name=main&vid=7530495662610238766',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'uifid': 'e438e504399eecf9c2f65594851517a53fcd0a47c3feace6f386418d12bbc04df48e44884eb112db37fe72d5435d21b6da0e51b513a8cb2b57492a0995d24d772f6cfd3d1776b840aac469c3bdd9274a5f67289cc8fdef6814c7e117c0a032504fc0fd31a61a75788f2ca404226b0db6e3746e19a5c1bb329337a3502e5540f971d0f0c745c7015ee45edb56770785034669036d8896c8bfef34dfdc03af6852',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }
    filepath = os.path.dirname(__file__)
    try:
        SIGN = execjs.compile(
            open(os.path.join(filepath, 'js/douyin_minimal.js'), 'r', encoding='utf-8').read())
    except Exception as e:
        # 如果JavaScript编译失败，使用备用方案
        logger.warning(f"JavaScript编译失败，使用备用签名方案: {e}")
        SIGN = None
    WEBID = ''

    def __init__(self, cookie='', UA='', proxy_url=''):
        self.COOKIES = get_cookie_dict(cookie)
        if UA:  # 如果需要访问搜索页面源码等内容，需要提供cookie对应的UA
            version = UA.split(' Chrome/')[1].split(' ')[0]
            _version = version.split('.')[0]
            self.HEADERS.update({
                "User-Agent": UA,  # 主要是这个
                "sec-ch-ua": f'"Chromium";v="{_version}", "Not(A:Brand";v="24", "Google Chrome";v="{_version}"',
            })
            self.PARAMS.update({
                "browser_version": version,
                "engine_version": version,  # 主要是这个
            })

        # 设置代理
        self.proxies = None
        if proxy_url:
            if proxy_url.startswith('http://'):
                https_url = proxy_url.replace('http://', 'https://')
                self.proxies = {'http': proxy_url, 'https': https_url}
            elif proxy_url.startswith('https://'):
                http_url = proxy_url.replace('https://', 'http://')
                self.proxies = {'http': http_url, 'https': proxy_url}
            elif proxy_url.startswith('socks5://'):
                self.proxies = {'http': proxy_url, 'https': proxy_url}
            elif ':' in proxy_url and not proxy_url.startswith(('http://', 'https://', 'socks5://')):
                # ip:port格式，尝试多种协议
                # 首先尝试socks5（最常用）
                self.proxies = {'http': f'socks5://{proxy_url}', 'https': f'socks5://{proxy_url}'}
                logger.info(f"使用SOCKS5代理: {proxy_url}")
            else:
                # 其他格式，默认为http
                self.proxies = {'http': f'http://{proxy_url}', 'https': f'https://{proxy_url}'}

        # 如果设置了代理，添加调试信息
        if self.proxies:
            logger.info(f"代理设置完成: HTTP={self.proxies.get('http', 'None')}, HTTPS={self.proxies.get('https', 'None')}")
        else:
            logger.info("未设置代理，使用直连模式")



    def get_params(self, params: dict) -> dict:
        params.update(self.PARAMS)
        params['msToken'] = self.get_ms_token()
        params['screen_width'] = self.COOKIES.get('dy_swidth', 2560)
        params['screen_height'] = self.COOKIES.get('dy_sheight', 1440)
        params['cpu_core_num'] = self.COOKIES.get('device_web_cpu_core', 12)
        params['device_memory'] = self.COOKIES.get('device_web_memory_size', 8)
        params['verifyFp'] = self.COOKIES.get('s_v_web_id', None)
        params['fp'] = self.COOKIES.get('s_v_web_id', None)
        params['webid'] = self.get_webid()
        # 添加uifid参数
        if 'uifid' not in params:
            params['uifid'] = self.HEADERS.get('uifid', '')
        return params

    def get_sign(self, uri: str, params: dict) -> str:
        """获取签名，使用嵌入式JS引擎"""
        if self.SIGN:
            try:
                query = '&'.join([f'{k}={quote(str(v))}' for k, v in params.items()])
                call_name = 'sign_datail'
                if 'reply' in uri:
                    call_name = 'sign_reply'
                return self.SIGN.call(call_name, query, self.HEADERS.get("user-agent"))
            except Exception as e:
                logger.warning(f"JavaScript签名失败: {e}，移除签名参数")
                return None
        else:
            logger.warning("JavaScript签名不可用，移除签名参数")
            return None

    def get_webid(self):
        import base64
        import re
        
        if not self.WEBID:
            # 首先尝试从cookie中的ttwid提取webid
            ttwid = self.COOKIES.get('ttwid', '')
            if ttwid and '|' in ttwid:
                # ttwid格式: 1|base64|timestamp|hash
                parts = ttwid.split('|')
                if len(parts) >= 2:
                    try:
                        decoded = base64.b64decode(parts[1] + '==').decode('utf-8')
                        # 从解码后的字符串中提取数字ID
                        match = re.search(r'(\d{19})', decoded)
                        if match:
                            self.WEBID = match.group(1)
                    except:
                        pass
            
            # 如果从cookie提取失败，尝试从页面获取
            if not self.WEBID:
                url = 'https://www.douyin.com/?recommend=1'
                text = self.getHTML(url)
                pattern = r'\\"user_unique_id\\":\\"(\d+)\\"'
                match = re.search(pattern, text)
                if match:
                    self.WEBID = match.group(1)
                    
            # 如果还是没有，使用固定值
            if not self.WEBID:
                self.WEBID = '7483171167227659830'
        return self.WEBID

    def get_ms_token(self, randomlength=120):
        """
        返回cookie中的msToken或随机字符串
        """
        ms_token = self.COOKIES.get('msToken', None)
        if not ms_token:
            ms_token = ''
            base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
            length = len(base_str) - 1
            for _ in range(randomlength):
                ms_token += base_str[random.randint(0, length)]
        return ms_token

    def getHTML(self, url) -> str:
        headers = self.HEADERS.copy()
        headers['sec-fetch-dest'] = 'document'
        response = requests.get(url, headers=headers, cookies=self.COOKIES, proxies=self.proxies)
        if response.status_code != 200 or response.text == '':
            logger.error(f'HTML请求失败, url: {url}, header: {headers}')
            return ''
        return response.text

    def getJSON(self, uri: str, params: dict, data: dict = None, max_retries: int = 3):
        import time
        import urllib.parse
        url = f'{self.HOST}{uri}'
        params = self.get_params(params)
        # 尝试获取签名，如果失败则不添加签名参数
        sign = self.get_sign(uri, params)  # 这里调用的是返回str的get_sign方法
        if sign:
            params["a_bogus"] = sign
        
        # 动态设置Referer
        headers = self.HEADERS.copy()
        if '/search/' in uri:
            headers['referer'] = 'https://www.douyin.com/search/'
        elif '/user/profile/other/' in uri:
            params['timestamp'] = str(int(time.time()))
            encoded_params_string = urllib.parse.urlencode(params)
            url1 = url + '?' + encoded_params_string 
            a_bogus = execjs.compile(open("8.动态url测试.js", 'r', encoding='utf-8').read()).call('get_a_bogus', url1)
            params['a_bogus'] = a_bogus
            headers['referer'] = f'https://www.douyin.com/user/{params.get("sec_user_id", "")}?from_tab_name=main'
        # 记录API调用详情
        # encoded_params_string = urllib.parse.urlencode(params)
        # url = url + '?' + encoded_params_string 
        logger.info(f'API调用: {uri}')
        logger.info(f'完整URL: {url}')
        logger.info(f'完整headers: {headers}')
        logger.info(f'完整params: {params}')
        logger.info(f'关键参数: sec_user_id={params.get("sec_user_id", "N/A")}, max_cursor={params.get("max_cursor", "N/A")}, count={params.get("count", "N/A")}')
        logger.info(f'请求方法: {"POST" if data else "GET"}')
        
        for attempt in range(max_retries):
            try:
                if data:
                    response = requests.post(
                        url, params=params, data=data, headers=headers, cookies=self.COOKIES, proxies=self.proxies, timeout=30)
                else:
                    response = requests.get(
                        url, params=params, headers=headers, cookies=self.COOKIES, proxies=self.proxies, timeout=30)
                
                # 记录响应状态
                logger.info(f'响应状态码: {response.status_code}, 响应大小: {len(response.text)} 字符')
                
                # 检查响应状态
                if response.status_code == 200 and response.text:
                    try:
                        json_data = response.json()
                        if json_data.get('status_code', 0) == 0:
                            # 记录成功响应的数据概要
                            if 'aweme_list' in json_data:
                                logger.info(f'成功获取视频列表，数量: {len(json_data.get("aweme_list", []))}')
                            elif 'user_list' in json_data:
                                logger.info(f'成功获取用户列表，数量: {len(json_data.get("user_list", []))}')
                            elif 'user' in json_data:
                                user_info = json_data.get('user', {})
                                logger.info(f'成功获取用户信息: {user_info.get("nickname", "未知")} (uid: {user_info.get("uid", "N/A")})')
                            else:
                                logger.info('API调用成功，返回数据结构未知')
                            return json_data
                        else:
                            logger.warning(f'API返回错误状态码: {json_data.get("status_code")}, 消息: {json_data.get("status_msg", "未知错误")}')
                    except ValueError:
                        logger.error(f'响应不是有效的JSON格式: {response.text[:200]}')
                
                # 如果是最后一次尝试，记录详细错误
                if attempt == max_retries - 1:
                    logger.error(
                        f'JSON请求失败：url: {url}, code: {response.status_code}, body: {response.text[:500]}')
                    if response.status_code == 200 and not response.text:
                        logger.error('响应为空，可能被反爬虫系统拦截')
                else:
                    logger.warning(f'请求失败，第{attempt + 1}次重试中...')
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f'网络请求异常: {e}')
                else:
                    logger.warning(f'网络异常，第{attempt + 1}次重试中...')
                    import time
                    time.sleep(2 ** attempt)
        
        # 所有重试都失败后，删除可能无效的cookie文件
        if os.path.exists('cookie.json'):
            os.remove('cookie.json')
        return {}


if __name__ == "__main__":
    r = Request()
    print(r.get_webid())
