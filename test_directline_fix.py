#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DirectLine令牌生成测试脚本 - 用于测试修复后的DirectLine配置
"""

import requests
import json
import argparse
import time

def test_directline_token(base_url, secret):
    """测试DirectLine令牌生成"""
    print(f"\n测试DirectLine令牌生成: {base_url}/api/directline/tokens/generate")
    
    # 确保用户ID格式正确（以dl_开头）
    user_id = f'dl_{int(time.time())}'
    print(f"使用用户ID: {user_id}")
    
    try:
        response = requests.post(
            f"{base_url}/api/directline/tokens/generate",
            headers={"Content-Type": "application/json"},
            json={
                "secret": secret,
                "user_id": user_id
            },
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功获取令牌: {data['token'][:10]}...{data['token'][-10:]}")
            print(f"有效期: {data['expires_in']}秒")
            return data['token']
        else:
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='DirectLine令牌生成测试工具')
    parser.add_argument('--url', default='http://localhost:5000', help='应用URL')
    parser.add_argument('--secret', required=True, help='DirectLine密钥')
    
    args = parser.parse_args()
    base_url = args.url
    secret = args.secret
    
    # 测试DirectLine令牌生成
    token = test_directline_token(base_url, secret)
    
    if token:
        print("\n✅ DirectLine令牌生成测试成功")
    else:
        print("\n❌ DirectLine令牌生成测试失败")

if __name__ == "__main__":
    main() 