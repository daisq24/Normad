#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DirectLine通道测试脚本
测试DirectLine通道的连接和消息发送功能
"""

import requests
import json
import argparse
import uuid
import time
import sys
import colorama
from colorama import Fore, Style

# 初始化colorama
colorama.init()

def generate_token(base_url, secret):
    """从应用服务生成DirectLine令牌"""
    print(f"\n{Fore.CYAN}[1/4] {Fore.WHITE}正在从服务获取DirectLine令牌...{Style.RESET_ALL}")
    
    user_id = f"dl_{int(time.time())}"
    
    payload = {
        "secret": secret,
        "user_id": user_id
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/directline/tokens/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"{Fore.CYAN}状态码: {response.status_code}{Style.RESET_ALL}")
        
        if response.status_code == 200:
            token_data = response.json()
            
            if "token" in token_data:
                token = token_data["token"]
                print(f"{Fore.GREEN}✓ 成功获取令牌！{Style.RESET_ALL}")
                print(f"用户ID: {user_id}")
                print(f"令牌过期时间: {token_data.get('expires_in', '未知')}秒")
                return token, user_id
            else:
                print(f"{Fore.RED}✗ 响应中未包含令牌！{Style.RESET_ALL}")
                print(f"响应内容: {json.dumps(token_data, ensure_ascii=False, indent=2)}")
                return None, user_id
        else:
            try:
                error_data = response.json()
                print(f"{Fore.RED}✗ 获取令牌失败！{Style.RESET_ALL}")
                print(f"错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"{Fore.RED}✗ 获取令牌失败！响应内容:{Style.RESET_ALL}")
                print(response.text)
            return None, user_id
    
    except Exception as e:
        print(f"{Fore.RED}✗ 请求异常: {e}{Style.RESET_ALL}")
        return None, user_id

def connect_to_directline(token):
    """连接到DirectLine服务"""
    print(f"\n{Fore.CYAN}[2/4] {Fore.WHITE}正在连接到DirectLine服务...{Style.RESET_ALL}")
    
    try:
        response = requests.post(
            "https://directline.botframework.com/v3/directline/conversations",
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )
        
        print(f"{Fore.CYAN}状态码: {response.status_code}{Style.RESET_ALL}")
        
        if response.status_code == 201:
            conversation_data = response.json()
            conversation_id = conversation_data.get("conversationId")
            
            if conversation_id:
                print(f"{Fore.GREEN}✓ 成功创建对话！{Style.RESET_ALL}")
                print(f"对话ID: {conversation_id}")
                return conversation_id
            else:
                print(f"{Fore.RED}✗ 响应中未包含对话ID！{Style.RESET_ALL}")
                print(f"响应内容: {json.dumps(conversation_data, ensure_ascii=False, indent=2)}")
                return None
        else:
            try:
                error_data = response.json()
                print(f"{Fore.RED}✗ 创建对话失败！{Style.RESET_ALL}")
                print(f"错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"{Fore.RED}✗ 创建对话失败！响应内容:{Style.RESET_ALL}")
                print(response.text)
            return None
    
    except Exception as e:
        print(f"{Fore.RED}✗ 请求异常: {e}{Style.RESET_ALL}")
        return None

def send_message(token, conversation_id, user_id):
    """发送测试消息到DirectLine"""
    print(f"\n{Fore.CYAN}[3/4] {Fore.WHITE}正在发送测试消息...{Style.RESET_ALL}")
    
    message_text = "我是数字游民，请为我推荐几个适合远程工作的城市"
    
    activity = {
        "type": "message",
        "from": {
            "id": user_id,
            "name": "测试用户"
        },
        "text": message_text,
        "locale": "zh-CN"
    }
    
    try:
        response = requests.post(
            f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=activity,
            timeout=30
        )
        
        print(f"{Fore.CYAN}状态码: {response.status_code}{Style.RESET_ALL}")
        
        if response.status_code == 200:
            message_data = response.json()
            message_id = message_data.get("id")
            
            if message_id:
                print(f"{Fore.GREEN}✓ 成功发送消息！{Style.RESET_ALL}")
                print(f"消息ID: {message_id}")
                print(f"消息内容: \"{message_text}\"")
                return message_id
            else:
                print(f"{Fore.RED}✗ 响应中未包含消息ID！{Style.RESET_ALL}")
                print(f"响应内容: {json.dumps(message_data, ensure_ascii=False, indent=2)}")
                return None
        else:
            try:
                error_data = response.json()
                print(f"{Fore.RED}✗ 发送消息失败！{Style.RESET_ALL}")
                print(f"错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"{Fore.RED}✗ 发送消息失败！响应内容:{Style.RESET_ALL}")
                print(response.text)
            return None
    
    except Exception as e:
        print(f"{Fore.RED}✗ 请求异常: {e}{Style.RESET_ALL}")
        return None

def receive_messages(token, conversation_id, watermark=None):
    """接收DirectLine消息"""
    print(f"\n{Fore.CYAN}[4/4] {Fore.WHITE}正在等待Bot响应消息...{Style.RESET_ALL}")
    
    url = f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities"
    if watermark:
        url += f"?watermark={watermark}"
    
    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )
        
        print(f"{Fore.CYAN}状态码: {response.status_code}{Style.RESET_ALL}")
        
        if response.status_code == 200:
            activities_data = response.json()
            activities = activities_data.get("activities", [])
            new_watermark = activities_data.get("watermark")
            
            bot_responses = [a for a in activities if a.get("from", {}).get("role") == "bot"]
            
            if bot_responses:
                print(f"{Fore.GREEN}✓ 收到Bot响应！{Style.RESET_ALL}")
                for activity in bot_responses:
                    activity_type = activity.get("type", "unknown")
                    activity_text = activity.get("text", "")
                    print(f"\n{Fore.YELLOW}Bot 回复 ({activity_type}):{Style.RESET_ALL}")
                    print(f"{activity_text[:100]}...")
                
                return True, new_watermark
            else:
                print(f"{Fore.YELLOW}⚠ 尚未收到Bot响应，活动数量: {len(activities)}{Style.RESET_ALL}")
                return False, new_watermark
        else:
            try:
                error_data = response.json()
                print(f"{Fore.RED}✗ 获取消息失败！{Style.RESET_ALL}")
                print(f"错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"{Fore.RED}✗ 获取消息失败！响应内容:{Style.RESET_ALL}")
                print(response.text)
            return False, None
    
    except Exception as e:
        print(f"{Fore.RED}✗ 请求异常: {e}{Style.RESET_ALL}")
        return False, None

def main():
    parser = argparse.ArgumentParser(description='DirectLine连接测试工具')
    parser.add_argument('--url', default='https://nomadnavigator-app-c7f4hfcabmezadd7.eastus2-01.azurewebsites.net', help='Bot应用URL')
    parser.add_argument('--secret', default='84ByzFvknPLPCV6xXAEitBoF3JHlUt39odqnA6EMqcmtm64IqTlvJQQJ99BDACqBBLyAArohAAABAZBS3G8q.EnTsnCC98Yg4TALcF9zvtXBjwXQRG5iYKghyVxPzkwhjIl9G0DsaJQQJ99BEAC3pKaRAArohAAABAZBS44XQ', help='DirectLine Secret')
    parser.add_argument('--wait', type=int, default=10, help='等待Bot响应的最长时间(秒)')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}        DirectLine通道连接测试工具        {Style.RESET_ALL}")
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")
    print(f"{Fore.WHITE}目标应用: {args.url}{Style.RESET_ALL}")
    
    # 1. 生成DirectLine令牌
    token, user_id = generate_token(args.url, args.secret)
    if not token:
        print(f"{Fore.RED}✗ 测试失败：无法获取DirectLine令牌{Style.RESET_ALL}")
        sys.exit(1)
    
    # 2. 连接到DirectLine服务
    conversation_id = connect_to_directline(token)
    if not conversation_id:
        print(f"{Fore.RED}✗ 测试失败：无法连接到DirectLine服务{Style.RESET_ALL}")
        sys.exit(1)
    
    # 3. 发送测试消息
    message_id = send_message(token, conversation_id, user_id)
    if not message_id:
        print(f"{Fore.RED}✗ 测试失败：无法发送测试消息{Style.RESET_ALL}")
        sys.exit(1)
    
    # 4. 等待并接收Bot响应
    watermark = None
    received = False
    
    print(f"{Fore.YELLOW}等待Bot响应最多{args.wait}秒...{Style.RESET_ALL}")
    
    for i in range(args.wait):
        received, watermark = receive_messages(token, conversation_id, watermark)
        if received:
            break
        
        if i < args.wait - 1:
            print(f"{Fore.YELLOW}等待2秒后重试...{Style.RESET_ALL}")
            time.sleep(2)
    
    # 5. 输出测试结果
    print(f"\n{Fore.CYAN}==============================================={Style.RESET_ALL}")
    if received:
        print(f"{Fore.GREEN}✓ 测试成功：DirectLine通道正常运行!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ 成功创建对话、发送消息并接收Bot响应{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ 测试部分成功：{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ 成功创建对话并发送消息{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ 未收到Bot响应{Style.RESET_ALL}")
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")

if __name__ == "__main__":
    main() 