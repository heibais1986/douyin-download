#!/usr/bin/env python3
import execjs
import os

def test_js_by_lines():
    print("=== 逐行测试JavaScript语法 ===\n")
    
    filepath = os.path.dirname(__file__)
    js_file = os.path.join(filepath, 'lib/js/douyin.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    print(f"总行数: {total_lines}")
    
    # 二分查找错误位置
    test_ranges = [100, 150, 200, 250, 300, 350, 400, total_lines]
    
    for line_count in test_ranges:
        if line_count > total_lines:
            line_count = total_lines
            
        try:
            partial_js = ''.join(lines[:line_count])
            js_context = execjs.compile(partial_js)
            print(f"前{line_count}行编译成功")
        except Exception as e:
            print(f"前{line_count}行编译失败: {e}")
            
            # 如果这个范围失败了，测试前一个成功的范围到这个范围之间的具体行
            if line_count > 100:
                prev_success = test_ranges[test_ranges.index(line_count) - 1]
                print(f"错误在第{prev_success}行到第{line_count}行之间")
                
                # 逐行测试这个范围
                for test_line in range(prev_success + 1, min(line_count + 1, total_lines + 1)):
                    try:
                        test_js = ''.join(lines[:test_line])
                        execjs.compile(test_js)
                    except Exception as line_error:
                        print(f"第{test_line}行出现错误: {line_error}")
                        print(f"第{test_line}行内容: {lines[test_line-1].strip()}")
                        return
            break
    
    print("所有行都编译成功")

if __name__ == '__main__':
    test_js_by_lines()