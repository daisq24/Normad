#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot Messages端点测试脚本
模拟Bot Framework Emulator发送的HTTP请求
"""

import requests
import json
import argparse
import uuid
import time
import sys
import datetime
import colorama
from colorama import Fore, Style

# 初始化colorama
colorama.init()

def test_bot_messages(base_url, app_id=None, app_password=None):
    """测试Bot Messages端点"""
    print(f"\n{Fore.CYAN}[1/1] {Fore.WHITE}测试Bot Messages端点...{Style.RESET_ALL}")
    print(f"目标: {base_url}/api/messages")
    
    # 创建Bot Framework活动
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    activity = {
        "type": "message",
        "id": str(uuid.uuid4()),
        "timestamp": timestamp,
        "channelId": "emulator",
        "serviceUrl": "https://test.com",
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
        "text": "我是数字游民，请为我推荐几个东南亚适合工作的城市",
        "entities": [],
        "locale": "zh-CN"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 模拟Bearer Token
    if app_id and app_password:
        auth_token = f"Bearer {app_id}.{app_password}"
        headers["Authorization"] = auth_token
        print(f"{Fore.CYAN}使用授权头: Bearer {app_id[:5]}...{app_password[:5]}...{Style.RESET_ALL}")
    
    try:
        print(f"{Fore.CYAN}发送活动:{Style.RESET_ALL}")
        print(json.dumps(activity, ensure_ascii=False, indent=2))
        
        response = requests.post(
            f"{base_url}/api/messages",
            headers=headers,
            json=activity,
            timeout=30
        )
        
        print(f"{Fore.CYAN}状态码: {response.status_code}{Style.RESET_ALL}")
        
        if response.status_code == 200 or response.status_code == 202:
            print(f"{Fore.GREEN}✓ 请求成功!{Style.RESET_ALL}")
            
            try:
                result = response.json()
                print(f"{Fore.YELLOW}响应内容:{Style.RESET_ALL}")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            except:
                print(f"{Fore.YELLOW}响应内容 (非JSON):{Style.RESET_ALL}")
                print(response.text[:300])
            
            return True
        else:
            print(f"{Fore.RED}✗ 请求失败!{Style.RESET_ALL}")
            try:
                result = response.json()
                print(f"{Fore.YELLOW}错误详情:{Style.RESET_ALL}")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            except:
                print(f"{Fore.YELLOW}响应内容:{Style.RESET_ALL}")
                print(response.text[:300])
            
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ 请求异常: {e}{Style.RESET_ALL}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Bot Messages端点测试工具')
    parser.add_argument('--url', default='https://nomadnavigator-app-c7f4hfcabmezadd7.eastus2-01.azurewebsites.net', help='Bot应用URL')
    parser.add_argument('--app-id', help='Bot App ID')
    parser.add_argument('--app-password', help='Bot App Password')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}        Bot Messages端点测试工具        {Style.RESET_ALL}")
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")
    print(f"{Fore.WHITE}目标应用: {args.url}{Style.RESET_ALL}")
    
    # 测试Bot Messages端点
    success = test_bot_messages(args.url, args.app_id, args.app_password)
    
    print(f"\n{Fore.CYAN}==============================================={Style.RESET_ALL}")
    if success:
        print(f"{Fore.GREEN}✓ 测试成功: Bot Messages端点正常响应{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ 测试失败: Bot Messages端点响应出错{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}可能的问题:{Style.RESET_ALL}")
        print(f"1. Bot应用未正确处理Bot Framework消息格式")
        print(f"2. Bot身份验证配置有误")
        print(f"3. 服务器连接问题")
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")

if __name__ == "__main__":
    main() 