#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证Azure服务连接
"""

import sys
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 导入配置
from app.utils.config import SETTINGS

def check_openai_connection():
    """验证Azure OpenAI连接"""
    try:
        import openai
        
        # 设置Azure OpenAI配置
        openai.api_type = "azure"
        openai.api_base = SETTINGS.AZURE_OPENAI_ENDPOINT
        openai.api_key = SETTINGS.AZURE_OPENAI_KEY
        openai.api_version = "2023-05-15"
        
        # 尝试发送简单请求
        response = openai.Completion.create(
            engine=SETTINGS.AZURE_OPENAI_DEPLOYMENT,
            prompt="测试连接",
            max_tokens=5
        )
        
        logger.info("✅ Azure OpenAI连接成功")
        return True
    except Exception as e:
        logger.error(f"❌ Azure OpenAI连接失败: {str(e)}")
        return False

def check_search_connection():
    """验证Azure AI Search连接"""
    try:
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient
        
        # 创建搜索客户端
        search_client = SearchClient(
            endpoint=f"https://{SETTINGS.AZURE_SEARCH_SERVICE}.search.windows.net/",
            index_name=SETTINGS.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(SETTINGS.AZURE_SEARCH_KEY)
        )
        
        # 尝试获取索引统计信息
        result = search_client.get_document_count()
        
        logger.info(f"✅ Azure AI Search连接成功，索引包含 {result} 个文档")
        return True
    except Exception as e:
        logger.error(f"❌ Azure AI Search连接失败: {str(e)}")
        return False

def check_cosmos_connection():
    """验证Azure CosmosDB连接"""
    try:
        from azure.cosmos import CosmosClient
        
        # 创建CosmosDB客户端
        client = CosmosClient(
            url=SETTINGS.AZURE_COSMOS_ENDPOINT,
            credential=SETTINGS.AZURE_COSMOS_KEY
        )
        
        # 获取数据库
        database = client.get_database_client(SETTINGS.AZURE_COSMOS_DATABASE)
        # 获取容器
        container = database.get_container_client(SETTINGS.AZURE_COSMOS_CONTAINER)
        
        # 尝试查询一条记录
        items = list(container.query_items(
            query="SELECT TOP 1 * FROM c",
            enable_cross_partition_query=True
        ))
        
        logger.info(f"✅ Azure CosmosDB连接成功")
        return True
    except Exception as e:
        logger.error(f"❌ Azure CosmosDB连接失败: {str(e)}")
        return False

def check_all_connections():
    """验证所有Azure服务连接"""
    logger.info("开始验证Azure服务连接...")
    
    openai_ok = check_openai_connection()
    search_ok = check_search_connection()
    cosmos_ok = check_cosmos_connection()
    
    if all([openai_ok, search_ok, cosmos_ok]):
        logger.info("🎉 所有Azure服务连接验证成功!")
        return True
    else:
        logger.warning("⚠️ 部分Azure服务连接验证失败，请检查配置")
        return False

if __name__ == "__main__":
    """主函数"""
    success = check_all_connections()
    sys.exit(0 if success else 1) 