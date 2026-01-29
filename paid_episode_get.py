import requests
import json
import os
import re
import time

# ================= 配置区域 =================
# 请将你 paid_episode.py 中的 headers 完整复制到这里
# 关键包含: cookie, referer, user-agent, x-secsdk-csrf-token 等
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=1, i",
    "referer": "https://www.douyin.com/user/MS4wLjABAAAACmSUqa6ZnHbY6NAlLzSMtwlwrB6rDGdpexV4gKRZG44?from_tab_name=main&modal_id=7593697878351121705&relation=0&vid=7593696686543883561",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "uifid": "5bdad390e71fd6e6e69e3cafe6018169c2447c8bc0b8484cc0f203a274f99fdbff9c06c0219079da48cbd8187cbf8bc3a8b74f3efe18593663c424beffd1e3df34093e2179baf5a387adbc955fc75a02335b01dba724eb814e91543e400689cf89a633062510bba56ab9961349afc670",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}
cookies = {
    "enter_pc_once": "1",
    "UIFID_TEMP": "29a1f63ec682dc0a0df227dd163e2b46e3a6390e403335fa4c2c6d1dc0ec5ffa3ff523d14be386f49616c8e74ea7da6fbcc51d28520e5243485cf5f536b1969fc856bd925eeab09c986ebaa2afb5581f4e1161b6a3a2dbe14e4ddd7cb5be188c0bfa941a08916c602fdb2deafd95f02e",
    "strategyABtestKey": "%221768377242.325%22",
    "volume_info": "%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D",
    "passport_csrf_token": "bdd691c9c3eba8a9f387813454166078",
    "passport_csrf_token_default": "bdd691c9c3eba8a9f387813454166078",
    "bd_ticket_guard_client_web_domain": "2",
    "ttwid": "1%7CEGOhVKZXz3HH80gYaKUu4yarOJRnPttUsQfXZM-lb8k%7C1768377244%7Cec1bf23ab04c90e3635b45ad77549e491d9bd458e9ff7db719c0685d89104a5a",
    "gulu_source_res": "eyJwX2luIjoiOWYxNmJiYTEwNTIwMTgyMzIwOGMyZWYyYzllN2RkYWE1YjRjNTgzYmI0ZDhkYzAwNWNlODQxZjgwNTU3MzA5ZCJ9",
    "passport_assist_user": "Cj0At-Xwt-f_ay3_B93FDmkPXlO_bB8_xIIadEqQvtNJpjLTc2m_7_yYqLtwi05sNs4FLfESvNpTlUbYc-ocGkoKPAAAAAAAAAAAAABP8_IgYtYAvwrgwJddANrD61P1jyz5meP7ezqIcp7scBvGGVsderiY-aY6HhMOJPbi5xCz8YYOGImv1lQgASIBA4UfUgY%3D",
    "n_mh": "Ld_2sVp0ll_u6mp6b_LurZQyiDFye8Ekksyi0O0RcOo",
    "sid_guard": "3839393373a4d82751f1d8395b18532b%7C1768377261%7C5184000%7CSun%2C+15-Mar-2026+07%3A54%3A21+GMT",
    "uid_tt": "fd7fc749aebdee437cc94c21b054671d",
    "uid_tt_ss": "fd7fc749aebdee437cc94c21b054671d",
    "sid_tt": "3839393373a4d82751f1d8395b18532b",
    "sessionid": "3839393373a4d82751f1d8395b18532b",
    "sessionid_ss": "3839393373a4d82751f1d8395b18532b",
    "session_tlb_tag": "sttt%7C10%7CODk5M3Ok2CdR8dg5WxhTK__________0aHnRjasT3F5NJbxfTw0Gb7EKh4ESVRfPqUzLMSy9wlw%3D",
    "is_staff_user": "false",
    "sid_ucp_v1": "1.0.0-KDliMzYzZWE2ODZmMzA5ZTllMmNlZTgzNjNjNzk5ZDhkNTQzNmFmOWIKHwjUr7jLlAMQrZedywYY7zEgDDCU57TgBTgHQPQHSAQaAmxmIiAzODM5MzkzMzczYTRkODI3NTFmMWQ4Mzk1YjE4NTMyYg",
    "ssid_ucp_v1": "1.0.0-KDliMzYzZWE2ODZmMzA5ZTllMmNlZTgzNjNjNzk5ZDhkNTQzNmFmOWIKHwjUr7jLlAMQrZedywYY7zEgDDCU57TgBTgHQPQHSAQaAmxmIiAzODM5MzkzMzczYTRkODI3NTFmMWQ4Mzk1YjE4NTMyYg",
    "_bd_ticket_crypt_cookie": "12c2c4b08c69693f5c36629048a73b55",
    "__security_mc_1_s_sdk_sign_data_key_web_protect": "127045a5-4456-8396",
    "__security_mc_1_s_sdk_cert_key": "c2c332b7-48cd-a64d",
    "__security_mc_1_s_sdk_crypt_sdk": "8d687099-4451-bf9f",
    "__security_server_data_status": "1",
    "login_time": "1768377261619",
    "publish_badge_show_info": "%220%2C0%2C0%2C1768377262116%22",
    "SelfTabRedDotControl": "%5B%7B%22id%22%3A%227527497677144885284%22%2C%22u%22%3A45%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227567976749988841510%22%2C%22u%22%3A60%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227580694402809464884%22%2C%22u%22%3A24%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227497910217544304659%22%2C%22u%22%3A42%2C%22c%22%3A0%7D%5D",
    "FOLLOW_NUMBER_YELLOW_POINT_INFO": "%22MS4wLjABAAAA9DM2tvtsNVtYa_L4LDfVa2_VPyRuz0-O-mKTeLlsHNs%2F1768406400000%2F0%2F1768377326986%2F0%22",
    "stream_player_status_params": "%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22",
    "sdk_source_info": "7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f2730343c3732313d32363d333234272927676c715a75776a716a666a69273f2763646976602778",
    "bit_env": "tSnOj5FUF12GmVpJ1Ge2Jn7ybeYYMd_05nztY39C-vD6G-rup6lxEoAstHblW6VpHi-FVNHJFCc9ceMK0mL-_thlGgMManVfJ-6H0rTJUC_jd71v4mjnNMefGxAhtEkj9_A-rdiRjejKa31XetPSpl7wMJzXjG2Oh64560ylqxDt7B1gkV6UI6arbIhU1DFpWPqlSy1g0dDNZA7oUKBL1mxqP-95xV_HPuKtnZoHdqgqCV2yUBNX-fxJVgznCRnjBUu88Y3CYuqy7skvB3zFJiR3Ytbmas3s0BbhbkTBsSNRXp8mr-a_SVPQvTt7xWJeRsyo361yYNgiVQMREqX2dbrjqEFWnoIR2uUQjtvuLPa231w8H2cBmvlrdXcOyPW9tuVu4SBaVqw-bQqYmi_s0Hbcwi6zXZS1VszG-3mHPPqx4_iiXwN5GsFeRENui0jm7MCg1iiB-um9luhK0IxnQW1TRW-RbKlTOxGRUDEZ0OIVquNTiLjPEGJFvXmj34nWO_pk6lWpFE9Q5UZBsxDN4nS7zrVuFaip3T6H4DxzKRU%3D",
    "passport_auth_mix_state": "z1uv1gv721seecpmof8b1w0kq7gu8ye2o6znc0sf66w3efp9",
    "IsDouyinActive": "true",
    "stream_recommend_feed_params": "%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A16%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A0%7D%22",
    "bd_ticket_guard_client_data": "eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTjFualVzRmZ1Wm9KWjdoWGU1ZjRabmZoVU1DV3E5VlZGT1NVNVVXeUlUSUovQTBobTM4K0V2WWFiSFd3UmpqbWVuWmxNNGlnRW5lTzdqUG1BKy9MNzQ9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D",
    "FOLLOW_LIVE_POINT_INFO": "%22MS4wLjABAAAA9DM2tvtsNVtYa_L4LDfVa2_VPyRuz0-O-mKTeLlsHNs%2F1768406400000%2F0%2F1768378528926%2F0%22",
    "home_can_add_dy_2_desktop": "%221%22",
    "biz_trace_id": "2aa70680",
    "odin_tt": "6195e651ae5201bd110b25cbad5fd195e75b8e9c639997ed1a60795a9aa2c3d1ac39e3cff6a565f3aa0c967f8bdcdc83f41869d709d0843adc8867c42879e12b",
    "bd_ticket_guard_client_data_v2": "eyJyZWVfcHVibGljX2tleSI6IkJOMW5qVXNGZnVab0paN2hYZTVmNFpuZmhVTUNXcTlWVkZPU1U1VVd5SVRJSi9BMGhtMzgrRXZZYWJIV3dSamptZW5abE00aWdFbmVPN2pQbUErL0w3ND0iLCJ0c19zaWduIjoidHMuMi5jZjA0NTJkNzlmZDEyMjE1NzJhZWExOTEzNzljNWZjODk1MDhkZmM0NTA5ZGZmNGIxMGI1ZGZkMmQ4ZTU3ZWQyYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJ0RkV6VDNGRkx2QzhXbStXUnI5Qit0WEd2SjNZdktDUmQ3cGhSQkFKQUZNPSIsInNlY190cyI6IiNiNVBjTW9HU0JaN0lJMDdFM256akdnWHNyWFhOQnFkSEkvMmUrZzV4NzJhVWZTUkppSzd0UFJ2VFk0T00ifQ%3D%3D"
}
params = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "sec_user_id": "MS4wLjABAAAACmSUqa6ZnHbY6NAlLzSMtwlwrB6rDGdpexV4gKRZG44",
    "max_cursor": "0",
    "locate_item_id": "7593696686543883561",
    "locate_query": "false",
    "show_live_replay_strategy": "1",
    "need_time_list": "1",
    "time_list_query": "0",
    "whale_cut_token": "",
    "cut_version": "1",
    "count": "18",
    "publish_video_strategy_type": "2",
    "from_user_page": "1",
    "update_version_code": "170400",
    "pc_client_type": "1",
    "pc_libra_divert": "Windows",
    "support_h265": "1",
    "support_dash": "0",
    "cpu_core_num": "8",
    "version_code": "290100",
    "version_name": "29.1.0",
    "cookie_enabled": "true",
    "screen_width": "1920",
    "screen_height": "1080",
    "browser_language": "zh-CN",
    "browser_platform": "Win32",
    "browser_name": "Chrome",
    "browser_version": "143.0.0.0",
    "browser_online": "true",
    "engine_name": "Blink",
    "engine_version": "143.0.0.0",
    "os_name": "Windows",
    "os_version": "10",
    "device_memory": "8",
    "platform": "PC",
    "downlink": "1.5",
    "effective_type": "3g",
    "round_trip_time": "300",
    "webid": "7595131801661720104",
    "uifid": "5bdad390e71fd6e6e69e3cafe6018169c2447c8bc0b8484cc0f203a274f99fdbff9c06c0219079da48cbd8187cbf8bc3a8b74f3efe18593663c424beffd1e3df34093e2179baf5a387adbc955fc75a02335b01dba724eb814e91543e400689cf89a633062510bba56ab9961349afc670",
    "verifyFp": "verify_mkdrgnxa_8iOAyUJl_Ub2R_4f2p_AHxO_6a0zIkGEKlvc",
    "fp": "verify_mkdrgnxa_8iOAyUJl_Ub2R_4f2p_AHxO_6a0zIkGEKlvc",
    "a_bogus": "Ov0jDqSLdd85edFSuCGDSrclSMgANP8yqFioWeFTHxKWc1zPdYPx/Ocpcoon4Qy06WBzkKIHzx0/bdVcTTXTZF9pwmkkuovSnUVcnWfL/qivbtt0DNjuCz0FFw0rUb4qa5VtiAhI2UtHgVxAiqdE/d5Jt/KCQbuBB3Oyk2YcE9sg1F6ADpcaPpSpOhGqlE==",
    "timestamp": "1768379444",
    "x-secsdk-web-signature": "11eadaccfc25f03db0e1866991eceb8b"
}
# 抓包请求中的 URL (通常是 /aweme/v1/web/mix/aweme/)
# 你可以从 paid_episode.py 的 response = requests.get(...) 中找到这个 URL
API_URL = "https://www.douyin.com/aweme/v1/web/mix/aweme/"

# 这里的 mix_id 需要从你的 url 参数或 json (mix_info -> mix_id) 中找到
# 根据你提供的 json，mix_id 是 "7593552018594072617"
MIX_ID = "7593552018594072617"

# 保存路径
SAVE_DIR = "抖音短剧下载"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# ================= 工具函数 =================

def sanitize_filename(filename):
    """清洗文件名，去除非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def download_video(url, title):
    """下载文件流"""
    filepath = os.path.join(SAVE_DIR, f"{title}.mp4")
    if os.path.exists(filepath):
        print(f"[-] {title} 已存在，跳过")
        return

    print(f"[⬇️] 正在下载: {title} ...")
    try:
        # 下载时也带上 Headers，防止被拦截
        with requests.get(url, headers=HEADERS, cookies=cookies, stream=True, timeout=60) as r:
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        f.write(chunk)
                print(f"    √ 下载完成")
            else:
                print(f"    x 下载失败 (状态码: {r.status_code})")
    except Exception as e:
        print(f"    x 下载出错: {e}")

def main():
    url = "https://www.douyin.com/aweme/v1/web/mix/aweme/"
    cursor = 0
    count = 20
    has_more = True
    page = 1

    print(f"开始解析合集: {MIX_ID}")

    while has_more:
        print(f"\n--- 正在获取第 {page} 页 (Cursor: {cursor}) ---")
        
        # 构造请求参数 (参考 paid_mix.py)
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "mix_id": MIX_ID,
            "cursor": cursor,
            "count": count
        }

        try:
            resp = requests.get(url, headers=HEADERS, cookies=cookies, params=params)
            data = resp.json()
        except Exception as e:
            print(f"请求失败: {e}")
            break

        # 检查列表
        aweme_list = data.get("aweme_list", [])
        if not aweme_list:
            print("未获取到视频列表，可能是 Cookie 过期或签名参数缺失。")
            print("建议：复制浏览器中该请求的完整 curl 或 URL 参数重试。")
            break

        for item in aweme_list:
            # 1. 提取基础信息
            desc = item.get("desc", "").strip()
            video_info = item.get("video", {})
            duration = video_info.get("duration", 0)
            
            # 2. 提取集数 (从 series_play_info 中获取)
            # 你的 json 显示结构为: item['series_play_info']['item_title_prefix']['text'] -> "第3集"
            episode_str = ""
            series_play_info = item.get("series_play_info", {})
            if series_play_info:
                prefix = series_play_info.get("item_title_prefix", {}).get("text", "")
                if prefix:
                    episode_str = f"[{prefix}]"
            
            # 如果没找到集数，用列表索引兜底
            if not episode_str:
                episode_str = f"[未知集]"

            # 3. 构造文件名
            title = sanitize_filename(f"{episode_str} {desc}")
            
            # 4. 权限检查 (核心逻辑)
            # 你的 json 显示: item['charge_info']['has_paid'] = true
            has_paid = item.get("charge_info", {}).get("has_paid", False)
            rights_text = item.get("charge_info", {}).get("has_right_text", "")
            
            # 标记是否付费集
            is_paid_episode = False
            paid_episodes = item.get("series_info", {}).get("paid_episodes", [])
            current_ep_idx = series_play_info.get("series_aweme_index", 0)
            
            if paid_episodes and current_ep_idx in paid_episodes:
                is_paid_episode = True

            print(f"[*] 解析: {title} | 时长: {duration/1000:.1f}s | 状态: {rights_text}")

            # 5. 提取最高画质链接
            # 优先从 bit_rate 列表里找，通常第一个就是最高清
            download_url = ""
            bit_rates = video_info.get("bit_rate", [])
            if bit_rates:
                download_url = bit_rates[0].get("play_addr", {}).get("url_list", [])[0]
            else:
                # 兜底
                download_url = video_info.get("play_addr", {}).get("url_list", [])[0]

            # 6. 安全校验
            if is_paid_episode and not has_paid:
                print(f"    [!] 警告: 这是付费集且未检测到购买权限，跳过下载。")
                continue
            
            if duration < 30000 and is_paid_episode:
                # 如果是付费集，但时长小于30秒，极有可能是试看片段
                print(f"    [!] 警告: 时长异常 ({duration}ms)，疑似试看片段，跳过。")
                continue

            # 执行下载
            download_video(download_url, title)

        # 翻页逻辑
        has_more = data.get("has_more", 0) == 1
        cursor = data.get("max_cursor", 0)
        page += 1
        
        # 避免请求过快
        time.sleep(2)

    print("\n所有下载任务结束。")

if __name__ == "__main__":
    main()