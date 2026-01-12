import subprocess
from functools import partial  # 锁定参数
import os

# 修改subprocess.Popen以隐藏窗口并设置编码
if os.name == 'nt':  # Windows系统
    subprocess.Popen = partial(subprocess.Popen, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
else:
    subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")

import execjs

# 使用Node.js但隐藏窗口运行
print("使用Node.js作为JavaScript运行时（隐藏窗口）")

if __name__ == "__main__":

    js_code = """
    function hello() {
        return "hello world";
    }
    """
    result = execjs.compile(js_code).call("hello")
    print(result)
