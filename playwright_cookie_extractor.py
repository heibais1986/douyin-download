#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright自动化Cookie获取工具
用于自动打开浏览器，获取抖音cookies并保存到文件
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright
import time

class PlaywrightCookieExtractor:
    def __init__(self, headless=False, timeout=300):
        """
        初始化Playwright Cookie提取器
        
        Args:
            headless (bool): 是否无头模式运行
            timeout (int): 等待用户登录的超时时间（秒）
        """
        self.headless = headless
        self.timeout = timeout
        self.cookie_file = Path("config/cookie.txt")
        self.cookie_json_file = Path("config/cookie.json")
        
    async def extract_cookies(self, url="https://www.douyin.com"):
        """
        提取指定网站的cookies
        
        Args:
            url (str): 目标网站URL
            
        Returns:
            bool: 是否成功获取cookies
        """
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            try:
                # 创建新的浏览器上下文
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                # 创建新页面
                page = await context.new_page()
                
                print(f"正在打开 {url}...")
                await page.goto(url, wait_until='networkidle')
                
                print("\n=== 重要提示 ===")
                print("1. 浏览器已打开，请在浏览器中完成登录")
                print("2. 登录完成后，请在此终端按 Enter 键继续")
                print("3. 如果需要取消，请按 Ctrl+C")
                print(f"4. 等待超时时间：{self.timeout}秒")
                print("================\n")
                
                # 等待用户输入或超时
                start_time = time.time()
                while True:
                    try:
                        # 非阻塞检查用户输入
                        import select
                        import sys
                        
                        if sys.platform == 'win32':
                            # Windows系统使用不同的方法
                            import msvcrt
                            if msvcrt.kbhit():
                                key = msvcrt.getch()
                                if key == b'\r':  # Enter键
                                    break
                        else:
                            # Unix/Linux系统
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                input()
                                break
                        
                        # 检查超时
                        if time.time() - start_time > self.timeout:
                            print(f"\n等待超时（{self.timeout}秒），正在获取当前cookies...")
                            break
                            
                        await asyncio.sleep(0.5)
                        
                    except KeyboardInterrupt:
                        print("\n用户取消操作")
                        return False
                
                # 获取cookies
                print("正在获取cookies...")
                cookies = await context.cookies()
                
                if not cookies:
                    print("警告：未获取到任何cookies")
                    return False
                
                # 保存cookies
                success = await self._save_cookies(cookies)
                
                if success:
                    print(f"\n✅ 成功获取并保存了 {len(cookies)} 个cookies")
                    print(f"Cookie文件保存位置：")
                    print(f"  - 文本格式: {self.cookie_file.absolute()}")
                    print(f"  - JSON格式: {self.cookie_json_file.absolute()}")
                    
                    # 验证cookies
                    await self._verify_cookies(page)
                    
                return success
                
            except Exception as e:
                print(f"获取cookies时发生错误: {e}")
                return False
            finally:
                await browser.close()
    
    async def _save_cookies(self, cookies):
        """
        保存cookies到文件
        
        Args:
            cookies (list): cookies列表
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            self.cookie_file.parent.mkdir(exist_ok=True)
            
            # 保存为文本格式（用于现有程序）
            cookie_strings = []
            for cookie in cookies:
                cookie_str = f"{cookie['name']}={cookie['value']}"
                cookie_strings.append(cookie_str)
            
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                f.write('; '.join(cookie_strings))
            
            # 保存为JSON格式（完整信息）
            with open(self.cookie_json_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存cookies失败: {e}")
            return False
    
    async def _verify_cookies(self, page):
        """
        验证cookies是否有效
        
        Args:
            page: Playwright页面对象
        """
        try:
            # 检查是否已登录（通过查找用户相关元素）
            await page.wait_for_timeout(2000)  # 等待页面加载
            
            # 尝试查找登录状态指示器
            login_indicators = [
                '[data-e2e="user-info"]',  # 用户信息
                '.avatar',  # 头像
                '[data-e2e="profile-avatar"]',  # 个人头像
                '.login-button'  # 登录按钮（如果存在说明未登录）
            ]
            
            is_logged_in = False
            for selector in login_indicators[:3]:  # 前3个是登录状态指示器
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_logged_in = True
                        break
                except:
                    continue
            
            # 检查是否有登录按钮（表示未登录）
            try:
                login_button = await page.query_selector('.login-button')
                if login_button:
                    is_logged_in = False
            except:
                pass
            
            if is_logged_in:
                print("✅ Cookie验证成功：检测到已登录状态")
            else:
                print("⚠️  Cookie验证警告：可能未完全登录，请检查登录状态")
                
        except Exception as e:
            print(f"验证cookies时出现错误: {e}")

def main():
    """
    主函数
    """
    print("=== Playwright自动化Cookie获取工具 ===")
    print("此工具将帮助您自动获取抖音网站的cookies")
    print()
    
    # 询问用户是否使用有头模式
    while True:
        choice = input("是否显示浏览器窗口？(y/n，默认y): ").strip().lower()
        if choice in ['', 'y', 'yes']:
            headless = False
            break
        elif choice in ['n', 'no']:
            headless = True
            break
        else:
            print("请输入 y 或 n")
    
    # 询问超时时间
    while True:
        timeout_input = input("设置等待登录的超时时间（秒，默认300）: ").strip()
        if timeout_input == '':
            timeout = 300
            break
        try:
            timeout = int(timeout_input)
            if timeout > 0:
                break
            else:
                print("请输入正数")
        except ValueError:
            print("请输入有效的数字")
    
    # 创建提取器并运行
    extractor = PlaywrightCookieExtractor(headless=headless, timeout=timeout)
    
    try:
        success = asyncio.run(extractor.extract_cookies())
        
        if success:
            print("\n🎉 Cookie获取完成！")
            print("现在您可以使用以下命令测试：")
            print("python cli.py -u https://www.douyin.com/user/MS4wLjABAAAA... -t post")
        else:
            print("\n❌ Cookie获取失败，请重试")
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"\n程序运行出错: {e}")

if __name__ == "__main__":
    main()