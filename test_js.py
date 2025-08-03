#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from lib.execjs_fix import execjs

def test_js():
    print("=== 测试JavaScript执行 ===")
    
    try:
        # 加载JavaScript文件
        filepath = os.path.dirname(__file__)
        js_file = os.path.join(filepath, 'lib/js/douyin.js')
        
        print(f"JavaScript文件路径: {js_file}")
        print(f"文件是否存在: {os.path.exists(js_file)}")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
            
        print(f"JavaScript文件大小: {len(js_content)} 字符")
        
        # 编译JavaScript
        print("\n=== 编译JavaScript ===")
        js_context = execjs.compile(js_content)
        print("JavaScript编译成功")
        
        # 测试简单的函数调用
        print("\n=== 测试函数调用 ===")
        
        # 测试参数
        test_params = "device_platform=webapp&aid=6383&count=5"
        test_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        print(f"测试参数: {test_params}")
        print(f"测试UA: {test_ua}")
        
        # 调用sign_datail函数 (只需要2个参数: params, userAgent)
        result = js_context.call('sign_datail', test_params, test_ua)
        print(f"\n函数调用成功: {result}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_js()