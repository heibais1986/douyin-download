#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音Cookie自动获取工具
基于Playwright实现自动化浏览器操作
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def get_douyin_cookies(headless=False, wait_time=60, browser_type='chromium', executable_path=None, use_existing_session=False):
    """
    获取抖音cookies
    """
    async with async_playwright() as p:
        # 配置启动选项
        launch_options = {
            'headless': headless,
            'args': [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        }
        
        # 设置可执行文件路径
        if executable_path:
            launch_options['executable_path'] = executable_path
            
        # 检查是否需要使用现有会话
        use_persistent_context = False
        user_data_dir = None
        
        if use_existing_session and browser_type.lower() in ['chrome', 'edge']:
            import os
            if browser_type.lower() == 'chrome':
                user_data_dir = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
            elif browser_type.lower() == 'edge':
                user_data_dir = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data')
            
            if user_data_dir and os.path.exists(user_data_dir):
                # 使用临时配置文件目录，避免冲突
                temp_profile = os.path.join(user_data_dir, 'PlaywrightTemp')
                os.makedirs(temp_profile, exist_ok=True)
                user_data_dir = temp_profile
                use_persistent_context = True
                print(f"尝试使用浏览器用户数据以保持登录状态...")
            else:
                print(f"未找到{browser_type}用户数据目录，使用全新会话")
        
        # 选择浏览器引擎和启动方式
        if use_persistent_context:
            # 使用持久化上下文以保持登录状态
            if browser_type.lower() in ['chrome', 'chromium', 'edge']:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir,
                    headless=headless,
                    executable_path=executable_path,
                    args=launch_options['args']
                )
                browser = None  # 持久化上下文不需要单独的browser对象
            else:
                print(f"{browser_type}不支持持久化上下文，使用普通模式")
                use_persistent_context = False
        
        if not use_persistent_context:
            # 普通启动模式
            if browser_type.lower() in ['chrome', 'chromium']:
                browser = await p.chromium.launch(**launch_options)
            elif browser_type.lower() == 'firefox':
                # Firefox特定参数
                if 'args' in launch_options:
                    launch_options['args'] = [arg for arg in launch_options['args'] if not arg.startswith('--disable')]
                browser = await p.firefox.launch(**launch_options)
            elif browser_type.lower() == 'webkit':
                browser = await p.webkit.launch(**launch_options)
            elif browser_type.lower() == 'edge':
                # Edge使用Chromium引擎
                browser = await p.chromium.launch(**launch_options)
            else:
                print(f"不支持的浏览器类型: {browser_type}，使用默认Chromium")
                browser = await p.chromium.launch(**launch_options)
        
        try:
            # 创建浏览器上下文（如果不是持久化上下文）
            if not use_persistent_context:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
            
            # 创建页面
            page = await context.new_page()
            
            # 访问抖音
            print("正在访问抖音...")
            try:
                await page.goto('https://www.douyin.com/', wait_until='domcontentloaded', timeout=60000)
            except Exception as e:
                print(f"页面加载超时，尝试继续: {e}")
                # 如果超时，尝试直接访问页面
                await page.goto('https://www.douyin.com/', timeout=60000)
            
            # 等待用户登录
            print(f"\n请在浏览器中登录抖音账号")
            print(f"等待 {wait_time} 秒...")
            print("登录完成后程序将自动获取cookies\n")
            
            # 检查浏览器是否关闭
            start_time = asyncio.get_event_loop().time()
            while True:
                try:
                    # 检查页面是否仍然可用
                    await page.evaluate('document.title')
                    
                    current_time = asyncio.get_event_loop().time()
                    if current_time - start_time >= wait_time:
                        break
                    
                    await asyncio.sleep(1)
                except Exception:
                    print("检测到浏览器已关闭，停止等待")
                    return False
            
            # 获取cookies
            print("正在获取cookies...")
            cookies = await context.cookies()
            
            # 过滤抖音相关cookies
            douyin_cookies = []
            for cookie in cookies:
                if 'douyin.com' in cookie.get('domain', '') or 'douyinpic.com' in cookie.get('domain', ''):
                    douyin_cookies.append(cookie)
            
            if not douyin_cookies:
                print("未获取到抖音cookies，请确认已正确登录")
                return False
            
            # 确保config目录存在
            config_dir = Path('config')
            config_dir.mkdir(exist_ok=True)
            
            # 保存cookies
            cookie_file = config_dir / 'cookie.txt'
            cookie_json_file = config_dir / 'cookie.json'
            
            # 保存为文本格式（用于程序读取）
            cookie_text = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in douyin_cookies])
            with open(cookie_file, 'w', encoding='utf-8') as f:
                f.write(cookie_text)
            
            # 保存完整JSON格式
            with open(cookie_json_file, 'w', encoding='utf-8') as f:
                json.dump(douyin_cookies, f, indent=2, ensure_ascii=False)
            
            print(f"\n成功获取并保存了 {len(douyin_cookies)} 个cookies")
            print(f"保存位置:")
            print(f"   文本格式: {cookie_file.absolute()}")
            print(f"   JSON格式: {cookie_json_file.absolute()}")
            
            # 简单验证
            important_cookies = ['sessionid', 'sid_guard', 'uid_tt', 'sid_tt']
            found_important = []
            for cookie in douyin_cookies:
                if cookie['name'] in important_cookies:
                    found_important.append(cookie['name'])
            
            if found_important:
                print(f"检测到重要cookies: {', '.join(found_important)}")
                print("Cookie获取成功，可以开始使用程序了！")
            else:
                print("未检测到关键登录cookies，可能需要重新登录")
            
            return True
            
        except Exception as e:
            print(f"获取cookies时发生错误: {e}")
            return False
        finally:
            if use_persistent_context:
                await context.close()
            else:
                await browser.close()

def get_default_browser():
    """
    获取系统默认浏览器
    """
    import winreg
    try:
        # 读取注册表获取默认浏览器
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
            prog_id = winreg.QueryValueEx(key, "ProgId")[0]
        
        # 根据ProgId判断浏览器类型
        if 'Chrome' in prog_id:
            return 'chrome', 'Google Chrome (系统默认)'
        elif 'Edge' in prog_id or 'MSEdge' in prog_id:
            return 'edge', 'Microsoft Edge (系统默认)'
        elif 'Firefox' in prog_id:
            return 'firefox', 'Firefox (系统默认)'
        else:
            return 'chrome', f'{prog_id} (系统默认)'
    except:
        # 如果无法读取注册表，尝试其他方法
        return 'chrome', 'Chrome (推测默认)'

def get_browser_options():
    """
    获取可用的浏览器选项
    """
    # 获取系统默认浏览器
    default_type, default_name = get_default_browser()
    
    browsers = {
        '1': (default_type, default_name, None),
        '2': ('chromium', 'Chromium (Playwright内置)', None),
        '3': ('chrome', 'Google Chrome', None),
        '4': ('edge', 'Microsoft Edge', None),
        '5': ('firefox', 'Firefox', None),
        '6': ('custom', '自定义浏览器路径', None)
    }
    
    # 常见浏览器路径
    browser_paths = {
        'chrome': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'
        ],
        'edge': [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
        ],
        'firefox': [
            r'C:\Program Files\Mozilla Firefox\firefox.exe',
            r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
        ]
    }
    
    # 检测可用浏览器
    available_browsers = {}
    for browser, paths in browser_paths.items():
        for path in paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                available_browsers[browser] = expanded_path
                break
    
    return browsers, available_browsers

def main():
    """
    主函数
    """
    print("=== 抖音Cookie自动获取工具 ===")
    print("基于Playwright，支持多种浏览器\n")
    
    # 获取浏览器选项
    browsers, available_browsers = get_browser_options()
    
    # 设置参数
    print("配置选项:")
    
    # 浏览器选择
    print("\n选择浏览器:")
    for key, (browser_type, name, _) in browsers.items():
        status = ""
        if browser_type in available_browsers:
            status = " [已安装]"
        elif browser_type in ['chromium', 'custom']:
            status = " [内置]" if browser_type == 'chromium' else ""
        else:
            status = " [未安装]"
        print(f"{key}. {name}{status}")
    
    print("\n说明: [已安装]=已检测到 [内置]=Playwright内置 [未安装]=未检测到")
    
    browser_choice = input("\n请选择浏览器 (默认1): ").strip() or '1'
    
    browser_type = 'chromium'
    executable_path = None
    
    if browser_choice in browsers:
        selected_browser = browsers[browser_choice][0]
        if selected_browser == 'custom':
            custom_path = input("请输入浏览器可执行文件完整路径: ").strip()
            if custom_path and os.path.exists(custom_path):
                browser_type = 'chrome'  # 假设自定义路径是Chrome兼容的
                executable_path = custom_path
            else:
                print("路径无效，使用默认Chromium")
                browser_type = 'chromium'
        else:
            browser_type = selected_browser
            if selected_browser in available_browsers:
                executable_path = available_browsers[selected_browser]
    
    # 是否使用现有浏览器会话
    use_session = input("\n是否尝试使用现有浏览器登录状态? (Y/n): ").strip().lower()
    use_existing_session = use_session not in ['n', 'no']
    
    # 是否显示浏览器
    show_browser = input("是否显示浏览器窗口? (Y/n): ").strip().lower()
    headless = show_browser in ['n', 'no']
    
    # 等待时间
    wait_input = input("等待登录时间(秒，默认60): ").strip()
    try:
        wait_time = int(wait_input) if wait_input else 60
    except ValueError:
        wait_time = 60
    
    print(f"\n开始执行...")
    print(f"浏览器: {browser_type.title()}")
    if executable_path:
        print(f"路径: {executable_path}")
    print(f"模式: {'无头模式' if headless else '显示浏览器'}")
    print(f"等待时间: {wait_time}秒\n")
    
    # 运行获取程序
    try:
        success = asyncio.run(get_douyin_cookies(
            headless=headless, 
            wait_time=wait_time,
            browser_type=browser_type,
            executable_path=executable_path,
            use_existing_session=use_existing_session
        ))
        
        if success:
            print("\n完成！现在可以使用以下命令测试:")
            print("python cli.py -u <抖音用户链接> -t post")
            print("\n示例:")
            print("python cli.py -u https://www.douyin.com/user/MS4wLjABAAAA... -t post")
        else:
            print("\n获取失败，请检查网络连接和登录状态后重试")
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n程序异常: {e}")
        print("请检查Playwright是否正确安装")

if __name__ == "__main__":
    main()