import execjs
import os

def test_isolated_se():
    # Test se function in isolation
    se_only = """
    function se(str, length, padChar) {
        str = String(str);
        while (str.length < length) {
            str = padChar + str;
        }
        return str;
    }
    """
    
    try:
        print("Testing isolated se function...")
        ctx = execjs.compile(se_only)
        result = ctx.call('se', '123', 5, '0')
        print(f"SUCCESS: se function returned '{result}'")
    except Exception as e:
        print(f"FAILED: se function - {e}")
        return
    
    # Now test se function with the full douyin.js file
    print("\nTesting se function within full douyin.js...")
    
    with open('lib/js/douyin.js', 'r', encoding='utf-8') as f:
        js_code = f.read()
    
    try:
        ctx = execjs.compile(js_code)
        print("Full file compilation successful")
        
        # Try to call se function
        result = ctx.call('se', '123', 5, '0')
        print(f"SUCCESS: se function in full file returned '{result}'")
        
    except Exception as e:
        print(f"FAILED: se function in full file - {e}")
        
        # Let's try to find the problematic part by testing smaller chunks
        print("\nTesting file in chunks...")
        
        lines = js_code.split('\n')
        chunk_size = 50
        
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i+chunk_size])
            try:
                ctx = execjs.compile(chunk)
                print(f"Chunk {i//chunk_size + 1} (lines {i+1}-{min(i+chunk_size, len(lines))}): OK")
            except Exception as e:
                print(f"Chunk {i//chunk_size + 1} (lines {i+1}-{min(i+chunk_size, len(lines))}): FAILED - {e}")
                # Show the problematic chunk
                print("Problematic chunk:")
                for j, line in enumerate(lines[i:i+chunk_size], i+1):
                    print(f"{j}: {line}")
                break

if __name__ == "__main__":
    test_isolated_se()