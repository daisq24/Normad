#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot直接测试脚本 - 使用/api/test-bot端点
"""

import requests
import json
import argparse
import time

def test_bot_direct(base_url, text="你好，这是一条测试消息"):
    """直接测试Bot功能"""
    print(f"\n测试Bot端点: {base_url}/api/test-bot")
    print(f"发送消息: {text}")
    
    # 创建请求数据
    data = {
        "text": text,
        "user_id": f"dl_{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/test-bot",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bot测试成功")
            
            if "response" in result and result["response"]:
                bot_response = result["response"]
                if "text" in bot_response:
                    print(f"\nBot回复: {bot_response['text']}")
                else:
                    print(f"\nBot响应: {json.dumps(bot_response, indent=2, ensure_ascii=False)}")
            else:
                print("\nBot没有返回文本响应")
                
            return result
        else:
            print(f"❌ Bot测试失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Bot直接测试工具')
    parser.add_argument('--url', default='http://localhost:5000', help='Bot应用URL')
    parser.add_argument('--message', default='我是数字游民，请为我推荐几个东南亚国家', help='测试消息')
    
    args = parser.parse_args()
    base_url = args.url
    message = args.message
    
    # 测试Bot
    result = test_bot_direct(base_url, message)
    
    if result and result.get("success"):
        print("\n✅ Bot响应测试成功")
    else:
        print("\n❌ Bot响应测试失败")

if __name__ == "__main__":
    main() 