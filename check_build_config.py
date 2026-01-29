# -*- coding: utf-8 -*-
"""
快速检查脚本 - 验证Nuitka打包前的配置
"""

import os
import sys

def check_file(filepath, description):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory(dirpath, description):
    """检查目录是否存在"""
    exists = os.path.isdir(dirpath)
    status = "✅" if exists else "❌"
    if exists:
        file_count = len([f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))])
        print(f"{status} {description}: {dirpath} ({file_count} 个文件)")
    else:
        print(f"{status} {description}: {dirpath}")
    return exists

def main():
    print("=" * 70)
    print("Nuitka打包配置检查")
    print("=" * 70)
    
    all_ok = True
    
    print("\n【必需文件检查】")
    all_ok &= check_file("douyin_monitor.py", "主程序文件")
    all_ok &= check_file("static/image.png", "Cookie指南图片")
    all_ok &= check_file("aria2c.exe", "Aria2下载工具")
    all_ok &= check_file("COOKIE_GUIDE.md", "Cookie指南文档")
    
    print("\n【必需目录检查】")
    all_ok &= check_directory("lib/js", "JavaScript库目录")
    all_ok &= check_directory("static", "静态资源目录")
    all_ok &= check_directory("templates", "模板目录")
    
    print("\n【配置文件检查】")
    all_ok &= check_file(".github/workflows/build.yml", "GitHub Actions构建配置")
    
    # 检查build.yml内容
    if os.path.exists(".github/workflows/build.yml"):
        with open(".github/workflows/build.yml", 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\n【build.yml配置检查】")
        
        checks = [
            ("--include-data-dir=lib/js=lib/js", "lib/js目录包含"),
            ("--include-data-dir=static=static", "static目录包含"),
            ("--include-data-dir=templates=templates", "templates目录包含"),
            ("--include-data-file=static/image.png=image.png", "image.png文件包含（新增）"),
            ("--include-data-file=COOKIE_GUIDE.md=COOKIE_GUIDE.md", "COOKIE_GUIDE.md包含"),
            ("--include-data-file=aria2c.exe=aria2c.exe", "aria2c.exe包含"),
        ]
        
        for check_str, desc in checks:
            if check_str in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - 未找到配置")
                all_ok = False
    
    # 检查douyin_monitor.py中的修复
    print("\n【代码修复检查】")
    if os.path.exists("douyin_monitor.py"):
        with open("douyin_monitor.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("sys.executable", "Nuitka资源路径处理"),
            ("self.logger.info", "日志记录功能"),
            ("尝试查找image.png", "资源查找日志"),
        ]
        
        for check_str, desc in checks:
            if check_str in content:
                print(f"✅ {desc}")
            else:
                print(f"⚠️  {desc} - 可能未包含")
    
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ 所有检查通过！可以进行Nuitka打包了。")
        print("\n下一步：")
        print("  1. 本地测试: python test_nuitka_build.py")
        print("  2. 或提交代码并打tag触发GitHub Actions构建")
    else:
        print("❌ 某些检查未通过，请先修复问题。")
    print("=" * 70)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
