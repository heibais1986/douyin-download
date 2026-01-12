# -*- coding: utf-8 -*-
"""
客户端授权验证模块
"""

import requests
import json
import time
from .machine_code import generate_machine_code, validate_machine_code


class AuthClient:
    def __init__(self, server_url='https://dy.gta1.ggff.net'):
        self.server_url = server_url
        self.machine_code = None
        self.auth_token = None
        self.hardware_info = None

    def initialize(self):
        """初始化，生成机器码"""
        self.machine_code, self.hardware_info = generate_machine_code()

    def request_auth(self):
        """申请授权"""
        if not self.machine_code:
            self.initialize()

        payload = {
            'machine_code': self.machine_code,
            'hardware_info': self.hardware_info
        }

        try:
            response = requests.post(f'{self.server_url}/api/auth/request',
                                   json=payload, timeout=30)
            result = response.json()

            if response.status_code == 200:
                return True, result.get('message', '申请成功')
            else:
                return False, result.get('error', '申请失败')

        except Exception as e:
            return False, f'网络错误: {str(e)}'

    def verify_auth(self):
        """验证授权"""
        if not self.machine_code:
            self.initialize()

        # 如果本地有token，正常验证
        if self.auth_token:
            payload = {
                'machine_code': self.machine_code,
                'auth_token': self.auth_token
            }
        else:
            # 如果没有token，只发送机器码，让服务器检查状态
            payload = {
                'machine_code': self.machine_code
            }

        try:
            response = requests.post(f'{self.server_url}/api/auth/verify',
                                   json=payload, timeout=30)
            result = response.json()

            if response.status_code == 200 and result.get('valid'):
                # 如果服务器返回了token，保存到本地
                if result.get('auth_token') and not self.auth_token:
                    self.auth_token = result['auth_token']

                # 检查硬件一致性
                server_hw = result.get('hardware_info', {})
                valid_hw, hw_msg = validate_machine_code(self.machine_code, server_hw)
                if not valid_hw:
                    return False, f'硬件验证失败: {hw_msg}'

                return True, '验证成功'
            else:
                error = result.get('error', '验证失败')
                return False, error

        except Exception as e:
            return False, f'网络错误: {str(e)}'

    def set_auth_token(self, token):
        """设置授权令牌"""
        self.auth_token = token

    def get_machine_code(self):
        """获取机器码"""
        if not self.machine_code:
            self.initialize()
        return self.machine_code

    def get_auth_status(self):
        """获取授权状态"""
        if not self.auth_token:
            return '未授权', None

        valid, message = self.verify_auth()
        if valid:
            return '已授权', message
        else:
            return '授权无效', message


# 示例使用
if __name__ == "__main__":
    client = AuthClient()
    print(f"机器码: {client.get_machine_code()}")

    # 申请授权
    success, msg = client.request_auth()
    print(f"申请结果: {success} - {msg}")

    # 假设管理员给了令牌
    # client.set_auth_token('ADMIN_GIVEN_TOKEN')

    # 验证授权
    # valid, msg = client.verify_auth()
    # print(f"验证结果: {valid} - {msg}")