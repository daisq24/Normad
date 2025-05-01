#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot Framework消息端点测试脚本
模拟Bot Framework发送的消息格式
"""

import requests
import json
import argparse
import uuid
import time

def test_bot_framework(base_url, app_id=None, app_password=None):
    """测试Bot Framework消息端点"""
    print(f"\n测试Bot Framework消息端点: {base_url}/api/messages")
    
    # 创建Bot Framework格式的活动
    activity = {
        "type": "message",
        "id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
        "channelId": "test",
        "serviceUrl": base_url,
        "conversation": {
            "id": f"conversation_{uuid.uuid4()}"
        },
        "from": {
            "id": "user1",
            "name": "Test User"
        },
        "recipient": {
            "id": app_id or "bot",
            "name": "Bot"
        },
        "text": "我是数字游民，请为我推荐几个东南亚城市",
        "replyToId": None,
        "entities": [],
        "channelData": {},
        "locale": "zh-CN"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 如果提供了App ID和密码，模拟Bearer Token (实际Token格式会更复杂)
    if app_id and app_password:
        auth_token = f"Bearer {app_id}.{app_password}"
        headers["Authorization"] = auth_token
        print(f"使用授权头: Bearer {app_id[:5]}...{app_password[:5]}...")
    
    try:
        print(f"发送活动: {json.dumps(activity, ensure_ascii=False, indent=2)}")
        response = requests.post(
            f"{base_url}/api/messages",
            headers=headers,
            json=activity,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        try:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except:
            print(f"响应内容: {response.text[:300]}...")
            
        return response.status_code == 200
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Bot Framework消息端点测试工具')
    parser.add_argument('--url', default='https://nomadnavigator-app-c7f4hfcabmezadd7.eastus2-01.azurewebsites.net', help='Bot应用URL')
    parser.add_argument('--app-id', help='Bot App ID')
    parser.add_argument('--app-password', help='Bot App Password')
    
    args = parser.parse_args()
    
    # 测试Bot Framework消息端点
    success = test_bot_framework(args.url, args.app_id, args.app_password)
    
    if success:
        print("\n✅ Bot Framework消息端点测试成功")
    else:
        print("\n❌ Bot Framework消息端点测试失败")
        print("可能的问题:")
        print("1. Bot应用未正确处理Bot Framework消息格式")
        print("2. Bot身份验证配置有误")
        print("3. 服务器连接问题")

if __name__ == "__main__":
    main() 