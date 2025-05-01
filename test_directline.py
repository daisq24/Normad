#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DirectLine配置测试脚本
"""

import requests
import json
import sys
import time
import argparse

def test_directline_token(url, secret):
    """测试DirectLine令牌生成"""
    print(f"\n测试DirectLine令牌生成: {url}/api/directline/tokens/generate")
    
    try:
        user_id = f'dl-test-user-{int(time.time())}'
        
        headers = {
            'Content-Type': 'application/json'
        }
        body = {
            'secret': secret,
            'user_id': user_id
        }
        
        print(f"请求参数: {json.dumps(body, indent=2)}")
        
        response = requests.post(
            f"{url}/api/directline/tokens/generate",
            headers=headers, 
            json=body
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2)}")
            return data.get('token')
        else:
            print(f"响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"请求出错: {e}")
        return None

def test_directline_conversation(token):
    """测试创建DirectLine会话"""
    if not token:
        print("未获取到令牌，无法创建会话")
        return None
        
    print("\n测试创建会话")
    
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(
            "https://directline.botframework.com/v3/directline/conversations",
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            conversation_id = data.get('conversationId')
            print(f"会话ID: {conversation_id}")
            return conversation_id
        else:
            print(f"创建会话失败: {response.text}")
            return None
    except Exception as e:
        print(f"创建会话出错: {e}")
        return None

def test_send_message(token, conversation_id):
    """测试发送消息"""
    if not token or not conversation_id:
        print("缺少令牌或会话ID，无法发送消息")
        return False
        
    print("\n测试发送消息")
    
    try:
        user_id = f'dl-test-user-{int(time.time())}'
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        message = {
            'type': 'message',
            'from': {
                'id': user_id
            },
            'text': '你好，这是一条测试消息'
        }
        
        print(f"发送消息: {json.dumps(message, indent=2)}")
        
        response = requests.post(
            f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities",
            headers=headers,
            json=message
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print(f"消息已发送: {response.text}")
            return True
        else:
            print(f"发送消息失败: {response.text}")
            return False
    except Exception as e:
        print(f"发送消息出错: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='DirectLine配置测试工具')
    parser.add_argument('--url', default='http://localhost:3978', help='应用URL')
    parser.add_argument('--secret', required=True, help='DirectLine密钥')
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    secret = args.secret
    
    # 测试DirectLine令牌生成
    token = test_directline_token(base_url, secret)
    
    if token:
        # 测试创建会话
        conversation_id = test_directline_conversation(token)
        
        if conversation_id:
            # 测试发送消息
            test_send_message(token, conversation_id)
    
    print("\n测试完成")

if __name__ == "__main__":
    main() 