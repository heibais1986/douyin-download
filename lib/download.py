import os
import sys
import subprocess

from loguru import logger


def download(path, aria2_conf):
    """
    命令行调用aria2c下载
    """
    if not os.path.exists(aria2_conf):
        logger.error('没有发现可下载的配置文件')
        return

    # 检查aria2c可执行文件是否存在（支持打包环境）
    possible_aria2c_paths = []

    # 1. 开发环境路径
    script_dir = os.path.dirname(os.path.dirname(__file__))
    possible_aria2c_paths.append(os.path.join(script_dir, 'aria2c'))

    # 2. 打包环境路径
    if getattr(sys, 'frozen', False):
        # PyInstaller环境
        if hasattr(sys, '_MEIPASS'):
            possible_aria2c_paths.append(os.path.join(sys._MEIPASS, 'aria2c'))

        # Nuitka环境 - 使用可执行文件目录
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        possible_aria2c_paths.append(os.path.join(exe_dir, 'aria2c'))

    # 添加.exe扩展名（Windows系统）
    if os.name == 'nt':  # Windows系统
        possible_aria2c_paths = [path + '.exe' for path in possible_aria2c_paths]

    # 尝试找到存在的aria2c路径
    aria2c_path = None
    for path in possible_aria2c_paths:
        if os.path.exists(path):
            aria2c_path = path
            logger.info(f"找到aria2c路径: {aria2c_path}")
            break

    if aria2c_path is None:
        logger.warning(f'未找到aria2c下载器，尝试的路径: {possible_aria2c_paths}')
        logger.info('请从 https://github.com/aria2/aria2/releases 下载aria2c并放置到项目根目录')
        logger.info(f'或者手动使用以下命令下载:')
        logger.info(f'aria2c -c --console-log-level warn -d "{path}" -i "{aria2_conf}"')
        return
    
    logger.info('开始下载')
    command = [
        aria2c_path,
        '-c', '--console-log-level', 'warn',
        '--check-certificate=false',  # 禁用SSL证书验证
        '--allow-overwrite=true',     # 允许覆盖已存在文件
        '-d', path, '-i', aria2_conf
    ]
    try:
        # 捕获输出以便调试
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.success('下载完成')
    except subprocess.CalledProcessError as e:
        logger.error(f'下载失败: {e}')
        # 输出aria2c的错误信息以便调试
        if e.stderr:
            logger.error(f'aria2c错误输出: {e.stderr}')
        if e.stdout:
            logger.error(f'aria2c标准输出: {e.stdout}')
        # 抛出异常让上层知道下载失败
        raise Exception(f'下载失败: {e}')
    except FileNotFoundError:
        logger.error(f'无法执行aria2c: {aria2c_path}')
        logger.info('请确保aria2c已正确安装并可执行')
        # 抛出异常让上层知道下载失败
        raise Exception(f'无法执行aria2c: {aria2c_path}')
