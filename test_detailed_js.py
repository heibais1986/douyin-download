#!/usr/bin/env python3
import execjs
import os

def test_js_detailed():
    print("=== 详细测试JavaScript语法 ===\n")
    
    filepath = os.path.dirname(__file__)
    js_file = os.path.join(filepath, 'lib/js/douyin.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 测试不同的JavaScript引擎
    engines = ['Node', 'V8', 'JScript']
    
    for engine in engines:
        try:
            print(f"尝试使用 {engine} 引擎...")
            runtime = execjs.get(engine)
            if runtime.is_available():
                print(f"{engine} 引擎可用")
                try:
                    ctx = runtime.compile(content)
                    print(f"{engine} 编译成功")
                    
                    # 测试函数调用
                    test_params = "device_platform=webapp&aid=6383&count=5"
                    test_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    
                    result = ctx.call('sign_datail', test_params, test_ua)
                    print(f"{engine} 函数调用成功: {result[:50]}...")
                    return True
                    
                except Exception as e:
                    print(f"{engine} 编译或执行失败: {e}")
            else:
                print(f"{engine} 引擎不可用")
        except Exception as e:
            print(f"{engine} 引擎错误: {e}")
        print()
    
    # 如果所有引擎都失败，尝试分段测试
    print("所有引擎都失败，开始分段测试...")
    
    # 测试基本的JavaScript语法
    basic_tests = [
        "var a = 1;",
        "function test() { return 1; }",
        "var arr = [1, 2, 3];",
        "var obj = {a: 1, b: 2};",
        "String.fromCharCode(65);"
    ]
    
    for i, test_code in enumerate(basic_tests):
        try:
            execjs.compile(test_code)
            print(f"基本测试 {i+1} 通过: {test_code}")
        except Exception as e:
            print(f"基本测试 {i+1} 失败: {test_code} - {e}")
    
    return False

if __name__ == '__main__':
    test_js_detailed()