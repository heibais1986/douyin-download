import os
import subprocess

from loguru import logger


def download(path, aria2_conf):
    """
    命令行调用aria2c下载
    """
    if not os.path.exists(aria2_conf):
        logger.error('没有发现可下载的配置文件')
        return
    
    # 检查aria2c可执行文件是否存在
    aria2c_path = os.path.join(os.path.dirname(__file__), '../aria2c')
    if os.name == 'nt':  # Windows系统
        aria2c_path += '.exe'
    
    if not os.path.exists(aria2c_path):
        logger.warning(f'未找到aria2c下载器: {aria2c_path}')
        logger.info('请从 https://github.com/aria2/aria2/releases 下载aria2c并放置到项目根目录')
        logger.info(f'或者手动使用以下命令下载:')
        logger.info(f'aria2c -c --console-log-level warn -d "{path}" -i "{aria2_conf}"')
        return
    
    logger.info('开始下载')
    command = [
        aria2c_path,
        '-c', '--console-log-level', 'warn', '-d', path, '-i', aria2_conf
    ]
    try:
        subprocess.run(command, check=True)
        logger.success('下载完成')
    except subprocess.CalledProcessError as e:
        logger.error(f'下载失败: {e}')
    except FileNotFoundError:
        logger.error(f'无法执行aria2c: {aria2c_path}')
        logger.info('请确保aria2c已正确安装并可执行')
