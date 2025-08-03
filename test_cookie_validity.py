#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie有效性测试工具
用于验证获取的cookies是否有效
"""

import requests
import json
from pathlib import Path

def load_cookies():
    """
    加载cookie文件
    """
    cookie_file = Path("config/cookie.txt")
    
    if not cookie_file.exists():
        print("❌ Cookie文件不存在，请先运行 auto_cookie.py 获取cookies")
        return None
    
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookie_text = f.read().strip()
        
        if not cookie_text:
            print("❌ Cookie文件为空")
            return None
        
        # 解析cookies
        cookies = {}
        for item in cookie_text.split('; '):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key] = value
        
        print(f"✅ 成功加载 {len(cookies)} 个cookies")
        return cookies
        
    except Exception as e:
        print(f"❌ 读取cookie文件失败: {e}")
        return None

def test_douyin_api(cookies):
    """
    测试抖音API访问
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.douyin.com/',
        'Accept': 'application/json, text/plain, */*',
    }
    
    # 测试用户信息API
    test_urls = [
        {
            'name': '用户信息API',
            'url': 'https://www.douyin.com/aweme/v1/web/aweme/post/',
            'params': {
                'device_platform': 'webapp',
                'aid': '6383',
                'channel': 'channel_pc_web',
                'sec_user_id': 'MS4wLjABAAAAXZI6LYdc99Uzm9OtYfEeIF2AvXiGAkEP_8P-R6Ln587GkxSJPLgBOv0v3FSphRWO',
                'max_cursor': '0',
                'locate_query': 'false',
                'show_live_replay_strategy': '1',
                'count': '10'
            }
        },
        {
            'name': '基础页面',
            'url': 'https://www.douyin.com/',
            'params': {}
        }
    ]
    
    results = []
    
    for test in test_urls:
        print(f"\n🔍 测试 {test['name']}...")
        
        try:
            response = requests.get(
                test['url'],
                params=test['params'],
                headers=headers,
                cookies=cookies,
                timeout=10
            )
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应大小: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # 检查响应内容
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if 'aweme_list' in data:
                            print(f"   ✅ 成功获取数据，包含 {len(data.get('aweme_list', []))} 条记录")
                            results.append(True)
                        elif 'status_code' in data:
                            print(f"   ⚠️  API返回状态码: {data['status_code']}")
                            if data['status_code'] == 0:
                                results.append(True)
                            else:
                                results.append(False)
                        else:
                            print(f"   ⚠️  响应格式异常")
                            results.append(False)
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON解析失败")
                        results.append(False)
                else:
                    # HTML响应
                    content = response.text
                    if 'douyin' in content.lower() and len(content) > 1000:
                        print(f"   ✅ 页面加载成功")
                        results.append(True)
                    else:
                        print(f"   ⚠️  页面内容异常")
                        results.append(False)
            else:
                print(f"   ❌ 请求失败")
                results.append(False)
                
        except requests.RequestException as e:
            print(f"   ❌ 网络错误: {e}")
            results.append(False)
        except Exception as e:
            print(f"   ❌ 未知错误: {e}")
            results.append(False)
    
    return results

def check_important_cookies(cookies):
    """
    检查重要的cookie字段
    """
    important_fields = {
        'sessionid': '会话ID',
        'sid_guard': '会话保护',
        'uid_tt': '用户ID',
        'sid_tt': '会话令牌',
        'passport_csrf_token': 'CSRF令牌'
    }
    
    print("\n🔍 检查重要Cookie字段:")
    
    found_count = 0
    for field, description in important_fields.items():
        if field in cookies:
            value = cookies[field]
            print(f"   ✅ {description} ({field}): {value[:20]}...")
            found_count += 1
        else:
            print(f"   ❌ 缺少 {description} ({field})")
    
    print(f"\n📊 重要字段完整度: {found_count}/{len(important_fields)} ({found_count/len(important_fields)*100:.1f}%)")
    
    return found_count >= 3  # 至少需要3个重要字段

def main():
    """
    主函数
    """
    print("=== Cookie有效性测试工具 ===")
    print("此工具将验证获取的cookies是否有效\n")
    
    # 加载cookies
    cookies = load_cookies()
    if not cookies:
        return
    
    # 检查重要字段
    has_important_fields = check_important_cookies(cookies)
    
    # 测试API访问
    print("\n" + "="*50)
    print("开始API测试...")
    
    test_results = test_douyin_api(cookies)
    
    # 总结结果
    print("\n" + "="*50)
    print("📋 测试结果总结:")
    
    success_count = sum(test_results)
    total_tests = len(test_results)
    
    print(f"   API测试通过: {success_count}/{total_tests}")
    print(f"   重要字段检查: {'通过' if has_important_fields else '失败'}")
    
    if success_count >= total_tests // 2 and has_important_fields:
        print("\n🎉 Cookie验证成功！可以正常使用程序")
        print("\n💡 建议测试命令:")
        print("   python cli.py -u <用户链接> -t post -l 5")
    elif success_count > 0:
        print("\n⚠️  Cookie部分有效，可能需要重新登录")
        print("\n💡 建议:")
        print("   1. 重新运行 auto_cookie.py")
        print("   2. 确保在浏览器中完全登录")
        print("   3. 检查网络连接")
    else:
        print("\n❌ Cookie无效，请重新获取")
        print("\n💡 解决方案:")
        print("   1. 运行 auto_cookie.py 重新获取")
        print("   2. 确保抖音账号正常登录")
        print("   3. 检查是否被限制访问")

if __name__ == "__main__":
    main()