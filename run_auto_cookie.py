#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化运行cookie获取脚本
"""

import asyncio
import sys
from auto_cookie import get_douyin_cookies, get_browser_options

def run_auto_cookie():
    """
    自动运行cookie获取程序
    """
    print("=== 自动化Cookie获取 ===")
    print("使用默认配置启动程序...\n")
    
    # 获取浏览器选项
    browsers, available_browsers = get_browser_options()
    
    # 使用默认配置
    default_browser = browsers['1'][0]  # 系统默认浏览器
    executable_path = None
    
    if default_browser in available_browsers:
        executable_path = available_browsers[default_browser]
    
    print(f"配置信息:")
    print(f"浏览器: {browsers['1'][1]}")
    if executable_path:
        print(f"路径: {executable_path}")
    print(f"模式: 显示浏览器")
    print(f"等待时间: 60秒")
    print(f"使用现有登录状态: 是\n")
    
    # 运行获取程序
    try:
        success = asyncio.run(get_douyin_cookies(
            headless=False,  # 显示浏览器
            wait_time=60,    # 等待60秒
            browser_type=default_browser,
            executable_path=executable_path,
            use_existing_session=True  # 使用现有登录状态
        ))
        
        if success:
            print("\n✅ Cookie获取完成！")
            print("现在可以使用以下命令测试:")
            print("python cli.py -u <抖音用户链接> -t post")
            print("\n示例:")
            print("python cli.py -u https://www.douyin.com/user/MS4wLjABAAAA... -t post")
        else:
            print("\n❌ 获取失败，请检查网络连接和登录状态后重试")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"\n💥 运行出错: {e}")
        print("请检查Playwright是否正确安装")

if __name__ == "__main__":
    run_auto_cookie()