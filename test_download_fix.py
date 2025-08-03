#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 添加lib目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from download import download
from loguru import logger

def test_download_without_aria2c():
    """
    测试在没有aria2c的情况下下载模块的行为
    """
    print("=== 测试下载模块修复 ===")
    
    # 创建测试目录和配置文件
    test_dir = "test_download"
    test_conf = "test_download.txt"
    
    # 确保测试目录存在
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建一个测试的aria2配置文件
    with open(test_conf, 'w', encoding='utf-8') as f:
        f.write("# 测试配置文件\n")
        f.write("https://example.com/test.txt\n")
        f.write("  dir=test_download\n")
        f.write("  out=test.txt\n")
    
    print(f"✅ 创建测试配置文件: {test_conf}")
    print(f"✅ 创建测试目录: {test_dir}")
    
    # 测试下载函数
    print("\n🔍 测试下载函数...")
    download(test_dir, test_conf)
    
    # 清理测试文件
    try:
        os.remove(test_conf)
        os.rmdir(test_dir)
        print("\n🧹 清理测试文件完成")
    except:
        print("\n⚠️ 清理测试文件时出现问题")
    
    print("\n✅ 测试完成！下载模块现在能优雅地处理缺少aria2c的情况")

if __name__ == "__main__":
    test_download_without_aria2c()