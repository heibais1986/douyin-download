import execjs

def test_js_line_by_line():
    with open('lib/js/douyin.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # Test compilation line by line
    accumulated_code = ""
    for i, line in enumerate(lines, 1):
        accumulated_code += line
        try:
            ctx = execjs.compile(accumulated_code)
            print(f"Line {i}: OK")
        except Exception as e:
            print(f"Line {i}: ERROR - {str(e)}")
            print(f"Problematic line: {line.strip()}")
            # Show context around the error
            start = max(0, i-3)
            end = min(len(lines), i+2)
            print("Context:")
            for j in range(start, end):
                marker = ">>> " if j == i-1 else "    "
                print(f"{marker}{j+1}: {lines[j].rstrip()}")
            break
    
    print("\nTesting individual functions...")
    
    # Test individual functions
    functions_to_test = [
        "function se(str, length, padChar) { str = String(str); while (str.length < length) { str = padChar + str; } return str; }",
        "function le(e, r) { return (e << (r %= 32) | e >>> 32 - r) >>> 0 }",
        "function de(e) { return 0 <= e && e < 16 ? 2043430169 : 16 <= e && e < 64 ? 2055708042 : void console['error']('invalid j for constant Tj') }",
        "function pe(e, r, t, n) { return 0 <= e && e < 16 ? (r ^ t ^ n) >>> 0 : 16 <= e && e < 64 ? (r & t | r & n | t & n) >>> 0 : (console['error']('invalid j for bool function FF'), 0) }",
        "function he(e, r, t, n) { return 0 <= e && e < 16 ? (r ^ t ^ n) >>> 0 : 16 <= e && e < 64 ? (r & t | ~r & n) >>> 0 : (console['error']('invalid j for bool function GG'), 0) }"
    ]
    
    for func in functions_to_test:
        try:
            ctx = execjs.compile(func)
            print(f"Function OK: {func[:50]}...")
        except Exception as e:
            print(f"Function ERROR: {func[:50]}... - {str(e)}")

if __name__ == "__main__":
    test_js_line_by_line()