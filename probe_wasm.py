import pywasm
import sys

# ==========================================
# 1. 兼容性修复 (解决 AttributeError)
# ==========================================
def get_memory_instance(min_pages):
    # 尝试不同的实例化方式，适应不同版本的 pywasm
    if hasattr(pywasm, 'Memory'):
        # 最新版 pywasm: Memory(limits)
        if hasattr(pywasm, 'Limits'):
            return pywasm.Memory(pywasm.Limits(min_pages, None))
        return pywasm.Memory(min_pages)
    
    # 旧版或 runtime 下的 Memory
    if hasattr(pywasm, 'runtime') and hasattr(pywasm.runtime, 'Memory'):
        return pywasm.runtime.Memory(min_pages)
        
    raise Exception("无法初始化 Memory，请尝试: pip install --upgrade pywasm")

def get_table_instance(min_size):
    if hasattr(pywasm, 'Table'):
        if hasattr(pywasm, 'Limits'):
            return pywasm.Table(pywasm.FunctionType([], []), pywasm.Limits(min_size, None))
        return pywasm.Table(min_size)
    if hasattr(pywasm, 'runtime') and hasattr(pywasm.runtime, 'Table'):
        return pywasm.runtime.Table(min_size)
    # 如果都失败，返回 None (有些版本允许 Table 为空)
    return None

# ==========================================
# 2. 构造模拟环境 (Mock Imports)
# ==========================================
# 既然我们不知道 a-q 具体是干嘛的，就全部用空函数顶替
# 只要 WASM 不崩溃，我们就能通过
def _stub(*args):
    return 0

# 根据之前的分析，WASM 需要模块 'a'
imports = {
    'a': {
        'a': _stub, 'b': _stub, 'c': _stub, 'd': _stub, 'e': _stub,
        'f': _stub, 'g': _stub, 'h': _stub, 'i': _stub, 'j': _stub,
        'k': _stub, 'l': _stub, 'm': _stub, 'n': _stub, 'o': _stub,
        'p': _stub, 'q': _stub,
        'memory': get_memory_instance(2048),
        'table': get_table_instance(1247) 
    }
}

# 修正 table (如果上面返回 None)
if imports['a']['table'] is None:
    # 尝试手动构造一个模拟对象
    class MockTable:
        def __init__(self, size): self.size = size
    imports['a']['table'] = MockTable(1247)

# ==========================================
# 3. 核心探测逻辑
# ==========================================
def probe_exports():
    print(f"[+] 正在加载 decoder.wasm ...")
    try:
        runtime = pywasm.load('./decoder.wasm', imports)
    except Exception as e:
        print(f"[-] 加载/实例化失败: {e}")
        print("    建议尝试: pip install wasmtime (它是更标准的库)")
        return

    print("[+] 实例化成功！开始寻找 malloc 和 解密函数...\n")

    # 这是之前分析出的导出函数列表 (混淆后的名字)
    candidates = ['r', 's', 't', 'u', 'v', 'w', 'x', 'y']
    
    malloc_func = None
    decrypt_func_candidates = []

    print(f"{'函数名':<6} | {'测试参数(1024)':<15} | {'返回结果':<15} | {'推测用途'}")
    print("-" * 60)

    for name in candidates:
        try:
            # 1. 猜测它是 malloc：尝试分配 1024 字节
            # malloc(size) -> pointer (int)
            res = runtime.exec(name, [1024])
            
            tag = ""
            # 如果返回一个像内存地址的大整数 (如 5243880)，很可能是 malloc
            if isinstance(res, int) and res > 10000: 
                tag = "✅ 疑似 malloc"
                malloc_func = name
            elif res == 0:
                tag = "可能是 free 或失败"
            
            print(f"{name:<6} | {'Success':<15} | {str(res):<15} | {tag}")

        except Exception as e:
            # 如果报错，说明参数不对
            # 解密函数通常需要 3 个参数：(src_ptr, len, dst_ptr) 或 2 个参数
            msg = str(e)
            if "argument" in msg or "signature" in msg:
                print(f"{name:<6} | {'Args Mismatch':<15} | {'N/A':<15} | 🎯 疑似核心函数 (参数不匹配)")
                decrypt_func_candidates.append(name)
            else:
                print(f"{name:<6} | {msg[:15]:<15} | {'N/A':<15} |")

    print("\n" + "="*30)
    print("🕵️‍♂️ 探测结论:")
    
    if malloc_func:
        print(f"1. 内存分配函数 (malloc) 是: '{malloc_func}'")
    else:
        print("1. 未找到 malloc，请手动检查输出中返回大整数的函数。")

    if decrypt_func_candidates:
        print(f"2. 解密函数 可能是: {decrypt_func_candidates}")
        print("   (通常是排在前面的导出函数，如 'r' 或 's'，且需要多个参数)")
    
    print("\n下一步：")
    print("如果确定了 malloc (例如 't') 和解密函数 (例如 'r')，")
    print("我们就可以写出最终的 Python 解密脚本了。")

if __name__ == "__main__":
    probe_exports()