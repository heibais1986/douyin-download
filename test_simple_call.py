import execjs

def test_simple_call():
    try:
        # Read the JavaScript file
        with open('lib/js/douyin.js', 'r', encoding='utf-8') as f:
            js_code = f.read()
        
        print("Compiling JavaScript...")
        ctx = execjs.compile(js_code)
        print("Compilation successful!")
        
        # Test simple function calls
        print("\nTesting simple function calls...")
        
        # Test rc4_encrypt
        try:
            result = ctx.call('rc4_encrypt', 'test', 'key')
            print(f"rc4_encrypt test: SUCCESS - {result}")
        except Exception as e:
            print(f"rc4_encrypt test: FAILED - {e}")
        
        # Test se function
        try:
            result = ctx.call('se', '123', 5, '0')
            print(f"se test: SUCCESS - {result}")
        except Exception as e:
            print(f"se test: FAILED - {e}")
        
        # Test SM3 constructor
        try:
            result = ctx.eval('new SM3()')
            print(f"SM3 constructor test: SUCCESS")
        except Exception as e:
            print(f"SM3 constructor test: FAILED - {e}")
        
        # Test sign_datail with minimal parameters
        try:
            result = ctx.call('sign_datail', 'test_params', 'test_ua')
            print(f"sign_datail test: SUCCESS - {result}")
        except Exception as e:
            print(f"sign_datail test: FAILED - {e}")
            
    except Exception as e:
        print(f"Compilation failed: {e}")

if __name__ == "__main__":
    test_simple_call()