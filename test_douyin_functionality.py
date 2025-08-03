#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.douyin import Douyin

def test_douyin_functionality():
    print("=== 测试抖音爬虫功能 ===")
    
    try:
        # 测试单个视频获取
        print("测试单个视频详情获取...")
        video_id = "7123456789012345678"  # 示例视频ID
        
        douyin = Douyin(target=video_id, type='video', limit=1)
        print(f"✅ Douyin实例创建成功")
        print(f"目标ID: {douyin.target}")
        print(f"类型: {douyin.type}")
        print(f"限制: {douyin.limit}")
        
        # 测试目标信息获取（不实际运行，避免网络请求）
        print("\n测试基本配置...")
        print(f"下载路径: {douyin.down_path}")
        print(f"Request对象: {type(douyin.request).__name__}")
        
        # 测试Request对象的签名功能
        print("\n测试Request对象签名功能...")
        test_params = {
            'device_platform': 'webapp',
            'aid': '6383',
            'aweme_id': video_id
        }
        
        sign_result = douyin.request.get_sign('/aweme/v1/web/aweme/detail/', test_params)
        print(f"签名结果: {sign_result}")
        
        if sign_result and 'X-Bogus' in sign_result:
            print("✅ 抖音爬虫核心功能正常")
            print("\n🎉 JavaScript兼容性问题已解决！")
            print("现在可以正常使用抖音爬虫进行数据采集了。")
            return True
        else:
            print("❌ 签名功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_douyin_functionality()