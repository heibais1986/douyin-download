#!/usr/bin/env python3
import execjs
import os

def test_minimal_js():
    print("=== 最小化JavaScript测试 ===\n")
    
    # 创建一个最简单的sign_datail函数
    minimal_js = """
    function sign_datail(params, userAgent) {
        return "test_result_" + params.length + "_" + userAgent.length;
    }
    """
    
    try:
        print("测试最小化JavaScript...")
        js_context = execjs.compile(minimal_js)
        print("最小化JavaScript编译成功")
        
        # 测试函数调用
        test_params = "device_platform=webapp&aid=6383&count=5"
        test_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        result = js_context.call('sign_datail', test_params, test_ua)
        print(f"最小化函数调用成功: {result}")
        
        # 现在尝试逐步添加原始代码的部分
        print("\n=== 测试原始JavaScript的各个部分 ===\n")
        
        # 读取原始文件
        filepath = os.path.dirname(__file__)
        js_file = os.path.join(filepath, 'lib/js/douyin.js')
        
        with open(js_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 尝试只编译，不调用函数
        print("尝试编译完整的原始JavaScript...")
        try:
            js_context_full = execjs.compile(original_content)
            print("完整JavaScript编译成功")
            
            # 现在尝试调用函数
            print("尝试调用原始sign_datail函数...")
            result_full = js_context_full.call('sign_datail', test_params, test_ua)
            print(f"原始函数调用成功: {result_full[:50]}...")
            
        except Exception as e:
            print(f"完整JavaScript处理失败: {e}")
            
            # 如果失败，尝试找出具体是哪个函数有问题
            print("\n尝试测试各个函数...")
            
            test_functions = [
                "sign_datail",
                "sign_reply", 
                "sign",
                "generate_random_str",
                "generate_rc4_bb_str"
            ]
            
            for func_name in test_functions:
                try:
                    if func_name == "sign_datail" or func_name == "sign_reply":
                        js_context_full.call(func_name, test_params, test_ua)
                        print(f"函数 {func_name} 调用成功")
                    elif func_name == "sign":
                        js_context_full.call(func_name, test_params, test_ua, [0, 1, 14])
                        print(f"函数 {func_name} 调用成功")
                    elif func_name == "generate_random_str":
                        js_context_full.call(func_name)
                        print(f"函数 {func_name} 调用成功")
                    elif func_name == "generate_rc4_bb_str":
                        js_context_full.call(func_name, test_params, test_ua, "test_env", "cus", [0, 1, 14])
                        print(f"函数 {func_name} 调用成功")
                except Exception as func_error:
                    print(f"函数 {func_name} 调用失败: {func_error}")
        
    except Exception as e:
        print(f"最小化测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_minimal_js()