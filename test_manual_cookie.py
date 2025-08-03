#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试手动输入的cookie是否有效
"""

from lib.cookies import test_cookie, cookies_str_to_dict

def test_manual_cookie():
    print("由于Chrome的新版本加密机制，自动提取cookie失败。")
    print("请手动获取cookie并测试其有效性。")
    print("\n获取cookie的步骤：")
    print("1. 打开Chrome浏览器")
    print("2. 访问 https://www.douyin.com 并登录")
    print("3. 按F12打开开发者工具")
    print("4. 点击'网络'(Network)标签")
    print("5. 刷新页面")
    print("6. 找到任意一个请求，右键选择'复制' -> '复制为cURL'")
    print("7. 从cURL命令中提取cookie部分（-H 'cookie: ...'）")
    print("8. 或者在'应用程序'(Application)标签 -> 'Cookie' -> 'https://www.douyin.com' 中手动复制所有cookie")
    
    print("\n请输入cookie字符串（格式：name1=value1; name2=value2; ...）：")
    cookie_str = input().strip()
    
    if not cookie_str:
        print("未输入cookie，退出测试。")
        return
    
    try:
        cookie_dict = cookies_str_to_dict(cookie_str)
        print(f"\n解析到 {len(cookie_dict)} 个cookie项")
        
        # 测试cookie有效性
        if test_cookie(cookie_dict):
            print("✅ Cookie有效！正在保存到config/cookie.txt...")
            with open('config/cookie.txt', 'w', encoding='utf-8') as f:
                f.write(cookie_str)
            print("Cookie已保存，现在可以正常使用程序了。")
        else:
            print("❌ Cookie无效或已过期，请重新获取。")
            
    except Exception as e:
        print(f"❌ 处理cookie时出错：{e}")

if __name__ == '__main__':
    test_manual_cookie()