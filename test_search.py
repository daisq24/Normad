#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Azure AI Search连接和索引
"""

import sys
import logging
import time
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential 
from azure.search.documents.indexes import SearchIndexClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 从.env文件中获取Azure AI Search信息
from app.utils.config import SETTINGS

def test_indexes():
    """测试搜索索引是否存在"""
    
    # 创建索引客户端
    endpoint = f"https://{SETTINGS.AZURE_SEARCH_SERVICE}.search.windows.net/"
    credential = AzureKeyCredential(SETTINGS.AZURE_SEARCH_KEY)
    client = SearchIndexClient(endpoint=endpoint, credential=credential)
    
    # 获取所有索引
    indexes = list(client.list_indexes())
    
    # 显示索引信息
    print(f"找到 {len(indexes)} 个索引:")
    for i, index in enumerate(indexes):
        print(f"{i+1}. {index.name}")
    
    # 检查目标索引是否存在
    target_indexes = [
        SETTINGS.AZURE_SEARCH_INDEX,
        f"{SETTINGS.AZURE_SEARCH_INDEX}_visa", 
        f"{SETTINGS.AZURE_SEARCH_INDEX}_cost"
    ]
    
    for target in target_indexes:
        found = any(index.name == target for index in indexes)
        if found:
            print(f"✅ 索引 {target} 存在")
        else:
            print(f"❌ 索引 {target} 不存在")
    
    return True

if __name__ == "__main__":
    test_indexes() 