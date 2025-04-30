#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部署测试脚本 - 验证部署后的服务是否正常工作
"""

import sys
import requests
import json
import argparse
from colorama import init, Fore, Style

# 初始化colorama
init()

def test_endpoint(name, url, method="GET", data=None, headers=None, expected_status=200):
    """测试端点"""
    print(f"{Fore.CYAN}测试 {name}...{Style.RESET_ALL}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"{Fore.RED}不支持的HTTP方法: {method}{Style.RESET_ALL}")
            return False
        
        if response.status_code == expected_status:
            print(f"{Fore.GREEN}✓ {name} 测试通过 (状态码: {response.status_code}){Style.RESET_ALL}")
            print(f"  响应: {response.text[:100]}{'...' if len(response.text) > 100 else ''}")
            return True
        else:
            print(f"{Fore.RED}✗ {name} 测试失败 (状态码: {response.status_code}){Style.RESET_ALL}")
            print(f"  响应: {response.text[:100]}{'...' if len(response.text) > 100 else ''}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ {name} 测试出错: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="NomadNavigator AI 部署测试工具")
    parser.add_argument("--url", required=True, help="部署的应用URL，例如 https://your-app.azurewebsites.net")
    args = parser.parse_args()
    
    base_url = args.url.rstrip("/")
    
    print(f"{Fore.YELLOW}NomadNavigator AI 部署测试{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}基础URL: {base_url}{Style.RESET_ALL}")
    print()
    
    # 测试列表
    tests = [
        {"name": "主页", "url": f"{base_url}/", "method": "GET"},
        {"name": "健康检查", "url": f"{base_url}/api/health", "method": "GET"},
        {"name": "Bot消息", "url": f"{base_url}/api/messages", "method": "POST", 
         "data": {
             "type": "message",
             "text": "你好，测试消息",
             "from": {"id": "test-user"},
             "recipient": {"id": "bot"},
             "channelId": "emulator",
             "conversation": {"id": "test-conversation"}
         },
         "headers": {"Content-Type": "application/json"}
        }
    ]
    
    # 执行测试
    results = []
    for test in tests:
        result = test_endpoint(
            test["name"], 
            test["url"], 
            method=test.get("method", "GET"),
            data=test.get("data"),
            headers=test.get("headers"),
            expected_status=test.get("expected_status", 200)
        )
        results.append(result)
        print()
    
    # 总结
    success_count = sum(1 for r in results if r)
    print(f"{Fore.YELLOW}测试总结{Style.RESET_ALL}")
    print(f"总测试数: {len(results)}")
    print(f"通过: {success_count}")
    print(f"失败: {len(results) - success_count}")
    
    if all(results):
        print(f"{Fore.GREEN}所有测试通过！部署成功。{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}部分测试失败。请检查日志和配置。{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 