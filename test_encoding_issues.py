import execjs
import os

def test_encoding_issues():
    # Read the file and check for potential encoding issues
    with open('lib/js/douyin.js', 'rb') as f:
        raw_content = f.read()
    
    print(f"File size: {len(raw_content)} bytes")
    
    # Check for BOM
    if raw_content.startswith(b'\xef\xbb\xbf'):
        print("WARNING: File has UTF-8 BOM")
        raw_content = raw_content[3:]  # Remove BOM
    
    # Decode and check for problematic characters
    try:
        content = raw_content.decode('utf-8')
        print("File decoded successfully as UTF-8")
    except UnicodeDecodeError as e:
        print(f"UTF-8 decode error: {e}")
        return
    
    # Check for null bytes or other problematic characters
    if '\x00' in content:
        print("WARNING: File contains null bytes")
        content = content.replace('\x00', '')
    
    # Check for other control characters
    control_chars = []
    for i, char in enumerate(content):
        if ord(char) < 32 and char not in '\n\r\t':
            control_chars.append((i, ord(char)))
    
    if control_chars:
        print(f"WARNING: Found {len(control_chars)} control characters:")
        for pos, code in control_chars[:10]:  # Show first 10
            print(f"  Position {pos}: character code {code}")
    
    # Try to clean the content and test again
    print("\nTesting with cleaned content...")
    
    # Remove any problematic characters
    cleaned_content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
    
    try:
        ctx = execjs.compile(cleaned_content)
        print("Cleaned content compilation successful")
        
        # Test se function
        result = ctx.call('se', '123', 5, '0')
        print(f"SUCCESS: se function returned '{result}'")
        
        # Test other functions
        result2 = ctx.call('rc4_encrypt', 'test', 'key')
        print(f"SUCCESS: rc4_encrypt returned '{result2}'")
        
    except Exception as e:
        print(f"FAILED even with cleaned content: {e}")
        
        # Try a different approach - save cleaned content to a new file
        print("\nSaving cleaned content to new file...")
        with open('lib/js/douyin_cleaned.js', 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        # Test the new file
        try:
            with open('lib/js/douyin_cleaned.js', 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            ctx = execjs.compile(new_content)
            print("New cleaned file compilation successful")
            
            result = ctx.call('se', '123', 5, '0')
            print(f"SUCCESS: se function in cleaned file returned '{result}'")
            
        except Exception as e2:
            print(f"FAILED with new cleaned file: {e2}")

if __name__ == "__main__":
    test_encoding_issues()