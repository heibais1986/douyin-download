#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试监控器错误
"""

import os
import sys
sys.path.append('lib')

from lib.douyin import Douyin
from lib.request import Request
import traceback

def test_monitor_error():
    """
    测试监控器中出现的错误
    """
    # 从图片中看到的URL
    homepage_url = "https://www.douyin.com/user/MS4wLjABAAAAQ1ZW1lH4vd4kyXOdREHNPsYOgtMDMkQjCKUJxOFOlF8?from_tab_name=main&vid=7533911500218731814"
    
    print(f"[DEBUG] 测试URL: {homepage_url}")
    
    try:
        # 读取cookie
        cookie = ""
        cookie_file = "config/cookie.txt"
        if os.path.exists(cookie_file):
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie = f.read().strip()
        
        if not cookie:
            print("[WARNING] 未找到cookie文件或cookie为空")
            return
        
        print(f"[DEBUG] Cookie长度: {len(cookie)}")
        
        # 删除旧的JSON文件以避免增量采集
        old_json_pattern = './下载/post_*.json'
        import glob
        for old_file in glob.glob(old_json_pattern):
            try:
                os.remove(old_file)
                print(f"[DEBUG] 删除旧文件: {old_file}")
            except:
                pass
        
        # 创建Douyin实例
        douyin = Douyin(
            target=homepage_url,
            type='post',
            down_path='./下载',
            cookie=cookie
        )
        
        print(f"[DEBUG] Douyin实例创建成功")
        print(f"[DEBUG] 目标类型: {douyin.type}")
        print(f"[DEBUG] 下载路径: {douyin.down_path}")
        
        # 测试获取目标信息
        print(f"[DEBUG] 开始获取目标信息...")
        douyin._Douyin__get_target_info()
        print(f"[DEBUG] 目标信息获取成功")
        print(f"[DEBUG] 目标ID: {douyin.id}")
        print(f"[DEBUG] 标题: {douyin.title}")
        
        # 测试获取视频列表
        print(f"[DEBUG] 开始获取视频列表...")
        videos = douyin.get_awemes()
        
        if videos:
            print(f"[SUCCESS] 成功获取到 {len(videos)} 个视频")
            for i, video in enumerate(videos[:3]):  # 只显示前3个
                print(f"  视频{i+1}: {video.get('desc', '无标题')[:50]}")
        else:
            print(f"[WARNING] 未获取到任何视频")
            
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")
        print(f"[ERROR] 错误类型: {type(e).__name__}")
        print(f"[ERROR] 详细错误信息:")
        traceback.print_exc()
        
        # 检查是否是文件路径相关的错误
        if "No such file or directory" in str(e):
            print(f"[ERROR] 这是一个文件路径错误")
            print(f"[DEBUG] 当前工作目录: {os.getcwd()}")
            print(f"[DEBUG] 下载目录是否存在: {os.path.exists('./下载')}")
            
            # 检查相关文件和目录
            paths_to_check = [
                './下载',
                './config',
                './config/cookie.txt',
                './lib',
                './lib/douyin.py',
                './lib/request.py'
            ]
            
            for path in paths_to_check:
                exists = os.path.exists(path)
                print(f"[DEBUG] {path}: {'存在' if exists else '不存在'}")

if __name__ == "__main__":
    test_monitor_error()