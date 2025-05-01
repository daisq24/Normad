#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot测试端点测试脚本
使用/api/test-bot端点直接测试Bot的功能
"""

import requests
import json
import argparse
import time
import colorama
from colorama import Fore, Style

# 初始化colorama
colorama.init()

def test_bot_endpoint(base_url):
    """测试Bot测试端点"""
    print(f"\n{Fore.CYAN}[1/1] {Fore.WHITE}测试Bot测试端点...{Style.RESET_ALL}")
    print(f"目标: {base_url}/api/test-bot")
    
    # 准备测试数据
    user_id = f"dl_{int(time.time())}"
    test_data = {
        "text": "我是数字游民，请为我推荐几个适合远程工作的城市",
        "user_id": user_id,
        "channel_id": "test"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"{Fore.CYAN}发送请求:{Style.RESET_ALL}")
        print(json.dumps(test_data, ensure_ascii=False, indent=2))
        
        response = requests.post(
            f"{base_url}/api/test-bot",
            headers=headers,
            json=test_data,
            timeout=60  # 增加超时时间，因为Bot可能需要一些时间处理
        )
        
        print(f"{Fore.CYAN}状态码: {response.status_code}{Style.RESET_ALL}")
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ 请求成功!{Style.RESET_ALL}")
            
            try:
                result = response.json()
                print(f"{Fore.YELLOW}响应内容:{Style.RESET_ALL}")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                # 检查处理时间
                if "processing_time" in result:
                    print(f"{Fore.CYAN}处理时间: {result['processing_time']}{Style.RESET_ALL}")
                
                # 检查响应内容
                if "response" in result and "text" in result["response"]:
                    print(f"\n{Fore.GREEN}Bot回复:{Style.RESET_ALL}")
                    print(result["response"]["text"])
                    
                return True
            except:
                print(f"{Fore.YELLOW}响应内容 (非JSON):{Style.RESET_ALL}")
                print(response.text[:500])
                return False
        else:
            print(f"{Fore.RED}✗ 请求失败!{Style.RESET_ALL}")
            try:
                result = response.json()
                print(f"{Fore.YELLOW}错误详情:{Style.RESET_ALL}")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            except:
                print(f"{Fore.YELLOW}响应内容:{Style.RESET_ALL}")
                print(response.text[:500])
            
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ 请求异常: {e}{Style.RESET_ALL}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Bot测试端点测试工具')
    parser.add_argument('--url', default='https://nomadnavigator-app-c7f4hfcabmezadd7.eastus2-01.azurewebsites.net', help='Bot应用URL')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}        Bot测试端点工具        {Style.RESET_ALL}")
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")
    print(f"{Fore.WHITE}目标应用: {args.url}{Style.RESET_ALL}")
    
    # 测试Bot测试端点
    success = test_bot_endpoint(args.url)
    
    print(f"\n{Fore.CYAN}==============================================={Style.RESET_ALL}")
    if success:
        print(f"{Fore.GREEN}✓ 测试成功: Bot测试端点正常响应{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Bot能够正确接收和处理消息{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ 测试失败: Bot测试端点响应出错{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}可能的问题:{Style.RESET_ALL}")
        print(f"1. Bot应用无法正确处理用户消息")
        print(f"2. OpenAI或其他依赖服务可能无法访问")
        print(f"3. 应用配置有误")
    print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}")

if __name__ == "__main__":
    main() 