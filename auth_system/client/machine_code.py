# -*- coding: utf-8 -*-
"""
机器码生成模块
生成基于硬件信息的唯一机器码
"""

import hashlib
import platform
import uuid
import psutil
import json


def get_system_info():
    """获取系统基本信息"""
    system_info = platform.uname()
    return {
        'system': system_info.system,
        'node': system_info.node,
        'release': system_info.release,
        'version': system_info.version,
        'machine': system_info.machine,
        'processor': system_info.processor
    }


def get_hardware_info():
    """获取硬件信息"""
    try:
        # CPU信息
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else None
        }
    except:
        cpu_info = {'error': '无法获取CPU信息'}

    try:
        # 内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available
        }
    except:
        memory_info = {'error': '无法获取内存信息'}

    try:
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'free': disk.free
        }
    except:
        disk_info = {'error': '无法获取磁盘信息'}

    # MAC地址
    mac_address = hex(uuid.getnode())

    return {
        'cpu': cpu_info,
        'memory': memory_info,
        'disk': disk_info,
        'mac_address': mac_address
    }


def generate_machine_code():
    """
    生成唯一机器码
    基于系统信息和硬件信息生成SHA256哈希
    """
    system_info = get_system_info()
    hardware_info = get_hardware_info()

    # 组合所有信息
    unique_string = json.dumps({
        'system': system_info,
        'hardware': hardware_info
    }, sort_keys=True)

    # 生成SHA256哈希并取前16位大写
    machine_code = hashlib.sha256(unique_string.encode()).hexdigest()[:16].upper()

    return machine_code, hardware_info


def validate_machine_code(machine_code, hardware_info):
    """
    验证机器码是否与当前硬件匹配
    用于检测是否更换了设备
    """
    current_code, current_hardware = generate_machine_code()

    if current_code != machine_code:
        return False, "机器码不匹配"

    # 检查关键硬件信息是否变化
    try:
        if current_hardware['cpu']['physical_cores'] != hardware_info['cpu']['physical_cores']:
            return False, "CPU核心数变化"
        if abs(current_hardware['memory']['total'] - hardware_info['memory']['total']) > 1024*1024*1024:  # 1GB容差
            return False, "内存容量变化"
    except:
        pass  # 如果无法比较，跳过

    return True, "验证通过"


if __name__ == "__main__":
    code, hw_info = generate_machine_code()
    print(f"机器码: {code}")
    print(f"硬件信息: {json.dumps(hw_info, indent=2, ensure_ascii=False)}")

    # 验证
    valid, msg = validate_machine_code(code, hw_info)
    print(f"验证结果: {valid} - {msg}")