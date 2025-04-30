#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置模块 - 从环境变量加载配置
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    """应用配置设置类"""
    
    # Azure OpenAI设置
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    
    # Azure AI Search设置
    AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE", "")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "")
    AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "nomad_destinations")
    
    # Azure CosmosDB for MongoDB设置
    AZURE_COSMOS_CONNECTION_STRING = os.getenv("AZURE_COSMOS_CONNECTION_STRING", "")
    AZURE_COSMOS_ACCOUNT = os.getenv("AZURE_COSMOS_ACCOUNT", "")
    AZURE_COSMOS_ENDPOINT = os.getenv("AZURE_COSMOS_ENDPOINT", "")
    AZURE_COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY", "")
    AZURE_COSMOS_DATABASE = os.getenv("AZURE_COSMOS_DATABASE", "nomad_navigator")
    AZURE_COSMOS_CONTAINER = os.getenv("AZURE_COSMOS_CONTAINER", "user_profiles")
    
    # Azure Bot Service设置
    MICROSOFT_APP_ID = os.getenv("MICROSOFT_APP_ID", "")
    MICROSOFT_APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")
    
    # Azure Functions设置
    AZURE_FUNCTION_APP_NAME = os.getenv("AZURE_FUNCTION_APP_NAME", "")
    AZURE_FUNCTION_KEY = os.getenv("AZURE_FUNCTION_KEY", "")
    
    # Azure App Service设置
    AZURE_APP_SERVICE_NAME = os.getenv("AZURE_APP_SERVICE_NAME", "")
    
    # 应用设置
    APP_NAME = "NomadNavigator AI"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "一个基于Azure的智能生活规划代理，帮助数字游民设计旅行路径"
    
    # 数据设置
    DEFAULT_BUDGET = 1500  # 默认每月预算（美元）
    
    # 其他设置 
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# 创建设置实例
SETTINGS = Settings() 