import execjs

def test_minimal_functions():
    # Test very basic JavaScript functions
    basic_js = """
    function test1() {
        return "hello";
    }
    
    function test2(a, b) {
        return a + b;
    }
    
    function test3() {
        var obj = {"key": "value"};
        return obj.key;
    }
    
    function test4() {
        var arr = [1, 2, 3];
        return arr[0];
    }
    """
    
    try:
        print("Testing basic JavaScript...")
        ctx = execjs.compile(basic_js)
        
        result1 = ctx.call('test1')
        print(f"test1: {result1}")
        
        result2 = ctx.call('test2', 5, 3)
        print(f"test2: {result2}")
        
        result3 = ctx.call('test3')
        print(f"test3: {result3}")
        
        result4 = ctx.call('test4')
        print(f"test4: {result4}")
        
        print("All basic tests passed!")
        
    except Exception as e:
        print(f"Basic test failed: {e}")
        return
    
    # Test rc4_encrypt function alone
    rc4_js = """
    function rc4_encrypt(plaintext, key) {
        var s = [];
        for (var i = 0; i < 256; i++) {
            s[i] = i;
        }
        var j = 0;
        for (var i = 0; i < 256; i++) {
            j = (j + s[i] + key.charCodeAt(i % key.length)) % 256;
            var temp = s[i];
            s[i] = s[j];
            s[j] = temp;
        }

        var i = 0;
        var j = 0;
        var cipher = [];
        for (var k = 0; k < plaintext.length; k++) {
            i = (i + 1) % 256;
            j = (j + s[i]) % 256;
            var temp = s[i];
            s[i] = s[j];
            s[j] = temp;
            var t = (s[i] + s[j]) % 256;
            cipher.push(String.fromCharCode(s[t] ^ plaintext.charCodeAt(k)));
        }
        return cipher.join('');
    }
    """
    
    try:
        print("\nTesting rc4_encrypt function...")
        ctx = execjs.compile(rc4_js)
        result = ctx.call('rc4_encrypt', 'test', 'key')
        print(f"rc4_encrypt result: {result}")
        print("rc4_encrypt test passed!")
        
    except Exception as e:
        print(f"rc4_encrypt test failed: {e}")

if __name__ == "__main__":
    test_minimal_functions()