import execjs
import os

def test_function_by_function():
    # Use Node.js if available
    try:
        os.environ['EXECJS_RUNTIME'] = 'Node'
    except:
        pass
    
    with open('lib/js/douyin.js', 'r', encoding='utf-8') as f:
        js_code = f.read()
    
    print("Compiling JavaScript...")
    ctx = execjs.compile(js_code)
    print("Compilation successful!")
    
    # Test functions one by one with minimal parameters
    functions_to_test = [
        ('se', ['123', 5, '0']),
        ('le', [123, 5]),
        ('de', [5]),
        ('pe', [5, 1, 2, 3]),
        ('he', [5, 1, 2, 3]),
        ('rc4_encrypt', ['test', 'key']),
        ('get_long_int', [0, 'teststring']),
        ('gener_random', [1000, [3, 45]]),
    ]
    
    for func_name, args in functions_to_test:
        try:
            print(f"\nTesting {func_name} with args {args}...")
            result = ctx.call(func_name, *args)
            print(f"SUCCESS: {func_name} returned {result}")
        except Exception as e:
            print(f"FAILED: {func_name} - {e}")
            # If this function fails, let's see what the error is
            if "缺少标识符" in str(e):
                print(f"  -> This function has a syntax issue when called")
            break
    
    # Test SM3 constructor
    try:
        print(f"\nTesting SM3 constructor...")
        result = ctx.eval('new SM3()')
        print(f"SUCCESS: SM3 constructor worked")
    except Exception as e:
        print(f"FAILED: SM3 constructor - {e}")
    
    # Test result_encrypt with minimal parameters
    try:
        print(f"\nTesting result_encrypt...")
        result = ctx.call('result_encrypt', 'test', 's0')
        print(f"SUCCESS: result_encrypt returned {result}")
    except Exception as e:
        print(f"FAILED: result_encrypt - {e}")
    
    # Test generate_random_str
    try:
        print(f"\nTesting generate_random_str...")
        result = ctx.call('generate_random_str')
        print(f"SUCCESS: generate_random_str returned {result}")
    except Exception as e:
        print(f"FAILED: generate_random_str - {e}")

if __name__ == "__main__":
    test_function_by_function()