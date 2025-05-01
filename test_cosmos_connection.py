#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试CosmosDB for MongoDB连接
"""

import os
import pymongo
import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_connection():
    """测试CosmosDB连接"""
    
    # 获取连接字符串（修正格式）
    connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING", "")
    
    # 移除可能的重复部分
    if connection_string.count("mongodb://") > 1:
        connection_string = connection_string[:connection_string.find("mongodb://", 1)]
    
    # 确保retrywrites=false参数存在
    if "retrywrites=false" not in connection_string.lower():
        if "?" in connection_string:
            connection_string += "&retrywrites=false"
        else:
            connection_string += "?retrywrites=false"
    
    # 修正appName参数
    connection_string = connection_string.replace("appName=@nomadnavigator-mongo@", "appName=nomadnavigator-mongo")
    
    print(f"使用连接字符串: {connection_string[:60]}...{connection_string[-30:]}")
    
    try:
        # 连接到MongoDB
        client = pymongo.MongoClient(connection_string)
        
        # 列出数据库
        databases = client.list_database_names()
        print(f"可用数据库: {databases}")
        
        # 连接到指定数据库
        db_name = os.getenv("AZURE_COSMOS_DATABASE", "nomadDB")
        db = client[db_name]
        
        # 列出集合
        collections = db.list_collection_names()
        print(f"数据库 '{db_name}' 中的集合: {collections}")
        
        # 尝试插入测试文档
        collection_name = os.getenv("AZURE_COSMOS_CONTAINER", "conversations")
        collection = db[collection_name]
        
        test_doc = {
            "userId": "test-user-1",
            "user_id": "test-user-1",  # 添加分片键
            "conversationId": "test-connection-1",
            "timestamp": datetime.datetime.now(),
            "message": "这是一条连接测试消息",
            "type": "test"
        }
        
        result = collection.insert_one(test_doc)
        print(f"插入文档成功, ID: {result.inserted_id}")
        
        # 查询测试文档
        found_doc = collection.find_one({"user_id": "test-user-1"})
        print(f"查询文档: {found_doc}")
        
        print("CosmosDB连接测试成功!")
        return True
        
    except Exception as e:
        print(f"CosmosDB连接测试失败: {e}")
        return False

if __name__ == "__main__":
    test_connection() 