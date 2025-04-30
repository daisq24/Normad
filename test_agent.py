#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试NomadAgent代理功能
"""

import asyncio
import json
from app.models.nomad_agent import NomadAgent

class MockTurnContext:
    """模拟TurnContext类"""
    def __init__(self, user_id):
        """初始化"""
        self.activity = type('obj', (object,), {
            'from_property': type('obj', (object,), {
                'id': user_id
            }),
            'timestamp': None
        })

async def test_agent():
    """测试代理功能"""
    print("开始测试NomadAgent代理功能...")
    
    # 创建代理实例
    agent = NomadAgent()
    
    # 创建模拟TurnContext
    context = MockTurnContext("test-user-456")
    
    # 测试用例
    test_cases = [
        "你好，我是一名数字游民，想了解泰国的签证信息",
        "我想在东南亚找一个生活成本低、网络速度快的城市",
        "我的预算每月是1000美元，推荐什么地方适合长期居住？",
        "欧洲有哪些适合数字游民的城市？"
    ]
    
    # 执行测试
    for i, query in enumerate(test_cases):
        print(f"\n===== 测试用例 {i+1}: {query} =====")
        
        # 获取响应
        response = await agent.process_input(query, context)
        
        # 打印响应
        print(f"代理响应:\n{response}")
        
        # 等待一下，避免请求过快
        await asyncio.sleep(1)

async def main():
    """主函数"""
    await test_agent()

if __name__ == "__main__":
    asyncio.run(main()) 