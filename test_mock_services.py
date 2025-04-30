#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试搜索服务和CosmosDB服务的模拟数据功能
"""

import asyncio
from app.models.services.search_service import AzureSearchService
from app.models.services.cosmos_service import CosmosDBService
from app.models.services.openai_service import OpenAIService

async def test_search_service():
    """测试搜索服务"""
    print("开始测试搜索服务...")
    
    # 创建搜索服务实例
    search_service = AzureSearchService()
    
    # 测试搜索目的地
    print("\n===== 测试搜索目的地 =====")
    destinations = await search_service.search_destinations("适合数字游民的东南亚城市")
    print(f"找到 {len(destinations)} 个目的地:")
    for dest in destinations:
        print(f"- {dest['name']}, {dest['country']}: {dest['description'][:50]}...")
    
    # 测试搜索签证信息
    print("\n===== 测试搜索签证信息 =====")
    visa_info = await search_service.search_visa_info("泰国签证")
    print(f"找到 {len(visa_info)} 条签证信息:")
    for visa in visa_info:
        print(f"- {visa['country']} ({visa['visa_type']}): 有效期 {visa['duration']}")
    
    # 测试搜索生活成本
    print("\n===== 测试搜索生活成本 =====")
    cost_info = await search_service.search_cost_info("清迈生活成本")
    print(f"找到 {len(cost_info)} 条生活成本信息:")
    for cost in cost_info:
        print(f"- {cost['city']}, {cost['country']}: 总月支出约 ${cost['total_monthly']}")

async def test_cosmos_service():
    """测试Cosmos数据库服务"""
    print("\n开始测试Cosmos数据库服务...")
    
    # 创建Cosmos服务实例
    cosmos_service = CosmosDBService()
    
    # 测试获取用户配置
    print("\n===== 测试获取用户偏好 =====")
    user_prefs = await cosmos_service.get_user_preferences("test-user-123")
    print(f"用户偏好: {user_prefs}")

async def main():
    """主函数"""
    # 测试搜索服务
    await test_search_service()
    
    # 测试Cosmos服务
    await test_cosmos_service()

if __name__ == "__main__":
    asyncio.run(main()) 