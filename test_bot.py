#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot测试脚本 - 用于测试Bot服务是否正常工作
"""

import requests
import json
import sys
import time
import argparse

def test_health(base_url):
    """测试健康端点"""
    url = f"{base_url}/api/health"
    print(f"测试健康端点: {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_diagnostic(base_url):
    """测试诊断端点"""
    url = f"{base_url}/api/diagnostic"
    print(f"\n测试诊断端点: {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Bot配置:")
            for key, value in data.get('config', {}).items():
                print(f"  {key}: {value}")
        else:
            print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_direct_line_token(base_url, secret):
    """测试DirectLine令牌生成"""
    url = f"{base_url}/api/directline/tokens/generate"
    print(f"\n测试DirectLine令牌生成: {url}")
    
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        body = {
            'secret': secret
        }
        response = requests.post(url, headers=headers, json=body)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            expires_in = data.get('expires_in')
            print(f"令牌: {token[:10]}... (已省略)")
            print(f"过期时间: {expires_in} 秒")
            return token
        else:
            print(f"响应: {response.text}")
            return None
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_send_message(base_url, token, conversation_id=None):
    """测试发送消息"""
    if not token:
        print("未提供令牌，无法发送消息")
        return None
    
    # 如果没有会话ID，创建一个新会话
    if not conversation_id:
        print("\n创建新会话...")
        url = "https://directline.botframework.com/v3/directline/conversations"
        headers = {
            'Authorization': f'Bearer {token}'
        }
        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 201:
                data = response.json()
                conversation_id = data.get('conversationId')
                print(f"会话ID: {conversation_id}")
            else:
                print(f"创建会话失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"创建会话时出错: {e}")
            return None
    
    # 发送消息
    print(f"\n发送消息到会话 {conversation_id}...")
    url = f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    user_id = f"user-{int(time.time())}"
    message = {
        'type': 'message',
        'from': {
            'id': user_id
        },
        'text': '你好，这是一条测试消息'
    }
    
    try:
        response = requests.post(url, headers=headers, json=message)
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print("消息发送成功")
            print(f"响应: {response.json()}")
            return conversation_id
        else:
            print(f"发送消息失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"发送消息时出错: {e}")
        return None

def test_get_messages(token, conversation_id):
    """测试获取消息"""
    if not token or not conversation_id:
        print("未提供令牌或会话ID，无法获取消息")
        return
    
    print(f"\n等待响应...")
    url = f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # 等待几秒，确保Bot有时间处理并响应
    time.sleep(3)
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            activities = data.get('activities', [])
            print(f"收到 {len(activities)} 条活动")
            
            for i, activity in enumerate(activities):
                activity_type = activity.get('type')
                from_id = activity.get('from', {}).get('id', 'unknown')
                text = activity.get('text', '')
                print(f"\n活动 {i+1}:")
                print(f"  类型: {activity_type}")
                print(f"  发送者: {from_id}")
                print(f"  内容: {text}")
        else:
            print(f"获取消息失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"获取消息时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description='Bot服务测试工具')
    parser.add_argument('--url', default='http://localhost:3978', help='Bot服务基础URL')
    parser.add_argument('--secret', help='DirectLine密钥')
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    secret = args.secret
    
    # 运行测试
    print("开始测试Bot服务...\n")
    
    # 测试健康端点
    if not test_health(base_url):
        print("健康检查失败，停止测试")
        return 1
    
    # 测试诊断端点
    test_diagnostic(base_url)
    
    # 如果提供了密钥，测试DirectLine功能
    if secret:
        token = test_direct_line_token(base_url, secret)
        if token:
            conversation_id = test_send_message(base_url, token)
            if conversation_id:
                test_get_messages(token, conversation_id)
    else:
        print("\n未提供DirectLine密钥，跳过消息测试")
        print("可以使用 --secret 参数提供DirectLine密钥")
    
    print("\n测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 