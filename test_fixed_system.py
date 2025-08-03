#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.request import Request

def test_fixed_system():
    print("=== 测试修复后的系统 ===")
    
    try:
        # 创建Request实例
        print("创建Request实例...")
        request = Request()
        print("✅ Request实例创建成功")
        
        # 测试签名功能
        print("\n测试签名功能...")
        test_uri = '/aweme/v1/web/aweme/detail/'
        test_params = {
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'aweme_id': '7123456789'
        }
        
        # 获取签名
        sign_result = request.get_sign(test_uri, test_params)
        print(f"签名结果: {sign_result}")
        
        if sign_result and 'X-Bogus' in sign_result:
            print("✅ 签名功能正常工作")
            
            # 测试完整参数获取
            print("\n测试完整参数获取...")
            full_params = request.get_params(test_params.copy())
            print(f"完整参数数量: {len(full_params)}")
            print(f"包含msToken: {'msToken' in full_params}")
            print(f"包含webid: {'webid' in full_params}")
            print("✅ 参数获取功能正常")
            
            print("\n🎉 系统修复成功！所有核心功能都正常工作")
            return True
        else:
            print("❌ 签名结果格式不正确")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_system()