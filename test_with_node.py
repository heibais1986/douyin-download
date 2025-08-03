import execjs
import os

def test_with_node():
    # Check if Node.js is available
    try:
        # Force use Node.js runtime
        os.environ['EXECJS_RUNTIME'] = 'Node'
        
        with open('lib/js/douyin.js', 'r', encoding='utf-8') as f:
            js_code = f.read()
        
        print("Testing with Node.js runtime...")
        ctx = execjs.compile(js_code)
        print("Compilation successful with Node.js!")
        
        # Test parameters
        test_params = "device_platform=webapp&aid=6383&channel=channel_pc_web"
        test_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Test sign_datail function
        result = ctx.call('sign_datail', test_params, test_ua)
        print(f"sign_datail result: {result}")
        print("SUCCESS: JavaScript functions are working with Node.js!")
        
    except Exception as e:
        print(f"Node.js test failed: {e}")
        
        # Fallback to default runtime
        print("\nFalling back to default runtime...")
        if 'EXECJS_RUNTIME' in os.environ:
            del os.environ['EXECJS_RUNTIME']
        
        try:
            ctx = execjs.compile(js_code)
            print("Compilation successful with default runtime!")
            
            result = ctx.call('sign_datail', test_params, test_ua)
            print(f"sign_datail result: {result}")
            print("SUCCESS: JavaScript functions are working with default runtime!")
            
        except Exception as e2:
            print(f"Default runtime also failed: {e2}")

if __name__ == "__main__":
    test_with_node()