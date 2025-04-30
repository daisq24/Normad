#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置Azure AI Search索引 - 创建用于目的地、签证和生活成本的索引
"""

import sys
import logging
import time
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ComplexField,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch
)
from app.utils.config import SETTINGS
from app.models.services.search_service import AzureSearchService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

def create_destinations_index(client):
    """创建目的地索引"""
    
    print(f"开始创建目的地索引: {SETTINGS.AZURE_SEARCH_INDEX}")
    
    # 定义索引
    index = SearchIndex(
        name=SETTINGS.AZURE_SEARCH_INDEX,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="name", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="country", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="region", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="climate", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="cost_index", type=SearchFieldDataType.Double, sortable=True, filterable=True),
            SimpleField(name="internet_speed", type=SearchFieldDataType.Int32, sortable=True, filterable=True),
            SimpleField(name="safety_index", type=SearchFieldDataType.Double, sortable=True, filterable=True),
            SearchableField(name="description", type=SearchFieldDataType.String),
            SimpleField(name="digital_nomad_friendly", type=SearchFieldDataType.Double, sortable=True, filterable=True),
            SearchableField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True)
        ],
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="name"),
                        keywords_fields=[SemanticField(field_name="tags")],
                        content_fields=[
                            SemanticField(field_name="description"),
                            SemanticField(field_name="country"),
                            SemanticField(field_name="region"),
                            SemanticField(field_name="climate")
                        ]
                    )
                )
            ]
        )
    )
    
    # 创建索引
    print(f"正在创建目的地索引: {SETTINGS.AZURE_SEARCH_INDEX}")
    try:
        client.create_or_update_index(index)
        print(f"目的地索引 {SETTINGS.AZURE_SEARCH_INDEX} 创建成功")
        return True
    except Exception as e:
        print(f"创建目的地索引失败: {str(e)}")
        return False

def create_visa_index(client):
    """创建签证索引"""
    
    visa_index_name = f"{SETTINGS.AZURE_SEARCH_INDEX}_visa"
    print(f"开始创建签证索引: {visa_index_name}")
    
    # 定义索引
    index = SearchIndex(
        name=visa_index_name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="country", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="visa_type", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="duration", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="requirements", type=SearchFieldDataType.String),
            SearchableField(name="restrictions", type=SearchFieldDataType.String),
            SearchableField(name="extension_options", type=SearchFieldDataType.String),
            SearchableField(name="digital_nomad_status", type=SearchFieldDataType.String, filterable=True)
        ],
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="country"),
                        keywords_fields=[SemanticField(field_name="visa_type")],
                        content_fields=[
                            SemanticField(field_name="requirements"),
                            SemanticField(field_name="restrictions"),
                            SemanticField(field_name="digital_nomad_status")
                        ]
                    )
                )
            ]
        )
    )
    
    # 创建索引
    print(f"正在创建签证索引: {visa_index_name}")
    try:
        client.create_or_update_index(index)
        print(f"签证索引 {visa_index_name} 创建成功")
        return True
    except Exception as e:
        print(f"创建签证索引失败: {str(e)}")
        return False

def create_cost_index(client):
    """创建生活成本索引"""
    
    cost_index_name = f"{SETTINGS.AZURE_SEARCH_INDEX}_cost"
    print(f"开始创建生活成本索引: {cost_index_name}")
    
    # 定义索引
    index = SearchIndex(
        name=cost_index_name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="city", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="country", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SimpleField(name="accommodation_cost", type=SearchFieldDataType.Int32, sortable=True, filterable=True),
            SimpleField(name="food_cost", type=SearchFieldDataType.Int32, sortable=True, filterable=True),
            SimpleField(name="transportation_cost", type=SearchFieldDataType.Int32, sortable=True, filterable=True),
            SimpleField(name="internet_cost", type=SearchFieldDataType.Int32, sortable=True, filterable=True),
            SimpleField(name="coworking_cost", type=SearchFieldDataType.Int32, sortable=True, filterable=True),
            SimpleField(name="total_monthly", type=SearchFieldDataType.Int32, sortable=True, filterable=True)
        ],
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="city"),
                        keywords_fields=[SemanticField(field_name="country")],
                        content_fields=[]
                    )
                )
            ]
        )
    )
    
    # 创建索引
    print(f"正在创建生活成本索引: {cost_index_name}")
    try:
        client.create_or_update_index(index)
        print(f"生活成本索引 {cost_index_name} 创建成功")
        return True
    except Exception as e:
        print(f"创建生活成本索引失败: {str(e)}")
        return False

def populate_with_sample_data(search_service):
    """用示例数据填充索引"""
    
    print("正在将示例数据填充到索引中...")
    
    # 目的地数据
    destinations = search_service._get_mock_destinations()
    for dest in destinations:
        dest["tags"] = ["数字游民", dest["country"], dest["region"], dest["climate"].split("气候")[0]]
    
    # 签证数据
    visa_info = search_service._get_mock_visa_info()
    
    # 生活成本数据
    cost_info = search_service._get_mock_cost_info()
    
    # 创建索引客户端
    endpoint = f"https://{SETTINGS.AZURE_SEARCH_SERVICE}.search.windows.net/"
    credential = AzureKeyCredential(SETTINGS.AZURE_SEARCH_KEY)
    
    # 填充目的地索引
    try:
        from azure.search.documents import SearchClient
        dest_client = SearchClient(endpoint=endpoint, index_name=SETTINGS.AZURE_SEARCH_INDEX, credential=credential)
        dest_client.upload_documents(documents=destinations)
        print(f"已将 {len(destinations)} 个目的地记录上传到索引")
    except Exception as e:
        print(f"填充目的地索引失败: {str(e)}")
    
    # 填充签证索引
    try:
        visa_client = SearchClient(endpoint=endpoint, index_name=f"{SETTINGS.AZURE_SEARCH_INDEX}_visa", credential=credential)
        visa_client.upload_documents(documents=visa_info)
        print(f"已将 {len(visa_info)} 个签证记录上传到索引")
    except Exception as e:
        print(f"填充签证索引失败: {str(e)}")
    
    # 填充生活成本索引
    try:
        cost_client = SearchClient(endpoint=endpoint, index_name=f"{SETTINGS.AZURE_SEARCH_INDEX}_cost", credential=credential)
        cost_client.upload_documents(documents=cost_info)
        print(f"已将 {len(cost_info)} 个生活成本记录上传到索引")
    except Exception as e:
        print(f"填充生活成本索引失败: {str(e)}")
    
    print("示例数据填充完成！")
    return True

def setup_search_indexes():
    """设置所有搜索索引"""
    
    print("开始设置Azure AI Search索引...")
    
    try:
        # 创建索引客户端
        endpoint = f"https://{SETTINGS.AZURE_SEARCH_SERVICE}.search.windows.net/"
        credential = AzureKeyCredential(SETTINGS.AZURE_SEARCH_KEY)
        client = SearchIndexClient(endpoint=endpoint, credential=credential)
        
        # 获取现有索引
        existing_indexes = list(client.list_indexes())
        existing_index_names = [index.name for index in existing_indexes]
        print(f"找到 {len(existing_indexes)} 个现有索引: {', '.join(existing_index_names)}")
        
        # 创建索引
        dest_ok = create_destinations_index(client)
        
        # 等待一会，避免请求过快
        print("等待2秒...")
        time.sleep(2)
        
        visa_ok = create_visa_index(client)
        
        # 等待一会，避免请求过快
        print("等待2秒...")
        time.sleep(2)
        
        cost_ok = create_cost_index(client)
        
        if all([dest_ok, visa_ok, cost_ok]):
            print("所有索引创建成功！")
            
            # 等待索引创建完成
            print("等待5秒使索引创建完成...")
            time.sleep(5)
            
            # 填充示例数据
            search_service = AzureSearchService()
            populate_with_sample_data(search_service)
            
            return True
        else:
            print("部分索引创建失败，请检查日志。")
            return False
            
    except Exception as e:
        print(f"设置索引时出错: {str(e)}")
        return False

if __name__ == "__main__":
    """主函数"""
    success = setup_search_indexes()
    print(f"索引创建结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1) 