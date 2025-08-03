import execjs
import os

def test_minimal_version():
    print("Testing minimal version of douyin.js...")
    
    try:
        # Read the minimal JavaScript file
        with open('lib/js/douyin_minimal.js', 'r', encoding='utf-8') as f:
            js_code = f.read()
        
        print("Compiling minimal JavaScript...")
        ctx = execjs.compile(js_code)
        print("Compilation successful!")
        
        # Test parameters
        test_params = "device_platform=webapp&aid=6383&channel=channel_pc_web"
        test_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Test individual functions
        print("\nTesting individual functions:")
        
        # Test se function
        se_result = ctx.call('se', '123', 5, '0')
        print(f"se('123', 5, '0') = '{se_result}'")
        
        # Test rc4_encrypt function
        rc4_result = ctx.call('rc4_encrypt', 'test', 'key')
        print(f"rc4_encrypt('test', 'key') = '{rc4_result}'")
        
        # Test generate_random_str function
        random_str = ctx.call('generate_random_str')
        print(f"generate_random_str() = '{random_str}'")
        
        # Test generate_rc4_bb_str function
        rc4_bb_str = ctx.call('generate_rc4_bb_str')
        print(f"generate_rc4_bb_str() = '{rc4_bb_str}'")
        
        # Test main sign functions
        print("\nTesting main sign functions:")
        
        # Test sign_datail function
        sign_result = ctx.call('sign_datail', test_params, test_ua)
        print(f"sign_datail result: {sign_result}")
        
        # Test sign_reply function
        reply_result = ctx.call('sign_reply', test_params, test_ua)
        print(f"sign_reply result: {reply_result}")
        
        # Test sign function
        basic_sign_result = ctx.call('sign', test_params, test_ua)
        print(f"sign result: {basic_sign_result}")
        
        print("\n✅ SUCCESS: All functions in minimal version are working!")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    test_minimal_version()