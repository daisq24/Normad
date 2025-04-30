#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查Azure服务配置是否完整，不显示具体值
"""

import os
from dotenv import load_dotenv

def check_config():
    """检查配置是否完整"""
    # 加载环境变量
    load_dotenv()
    
    # 检查必要的配置项
    config_checks = {
        "Azure OpenAI": {
            "AZURE_OPENAI_KEY": bool(os.getenv("AZURE_OPENAI_KEY")),
            "AZURE_OPENAI_ENDPOINT": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
            "AZURE_OPENAI_DEPLOYMENT": bool(os.getenv("AZURE_OPENAI_DEPLOYMENT")),
        },
        "Azure AI Search": {
            "AZURE_SEARCH_SERVICE": bool(os.getenv("AZURE_SEARCH_SERVICE")),
            "AZURE_SEARCH_KEY": bool(os.getenv("AZURE_SEARCH_KEY")),
            "AZURE_SEARCH_INDEX": bool(os.getenv("AZURE_SEARCH_INDEX")),
        },
        "Azure CosmosDB": {
            "AZURE_COSMOS_CONNECTION_STRING": bool(os.getenv("AZURE_COSMOS_CONNECTION_STRING")),
            "AZURE_COSMOS_ACCOUNT": bool(os.getenv("AZURE_COSMOS_ACCOUNT")),
            "AZURE_COSMOS_KEY": bool(os.getenv("AZURE_COSMOS_KEY")),
            "AZURE_COSMOS_DATABASE": bool(os.getenv("AZURE_COSMOS_DATABASE")),
            "AZURE_COSMOS_CONTAINER": bool(os.getenv("AZURE_COSMOS_CONTAINER")),
        },
        "Azure Bot Service": {
            "MICROSOFT_APP_ID": bool(os.getenv("MICROSOFT_APP_ID")),
            "MICROSOFT_APP_PASSWORD": bool(os.getenv("MICROSOFT_APP_PASSWORD")),
        },
        "Azure Function App": {
            "AZURE_FUNCTION_APP_NAME": bool(os.getenv("AZURE_FUNCTION_APP_NAME")),
            "AZURE_FUNCTION_KEY": bool(os.getenv("AZURE_FUNCTION_KEY")),
        },
        "Azure App Service": {
            "AZURE_APP_SERVICE_NAME": bool(os.getenv("AZURE_APP_SERVICE_NAME")),
        },
        "其他配置": {
            "DEBUG": os.getenv("DEBUG", "False"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        }
    }
    
    # 输出检查结果
    print("Azure服务配置检查结果：\n")
    
    all_configured = True
    for service, configs in config_checks.items():
        print(f"## {service}")
        service_configured = True
        
        for config_name, configured in configs.items():
            status = "✅ 已配置" if configured else "❌ 未配置"
            print(f"   {config_name}: {status}")
            
            if not configured and service != "其他配置":  # 允许其他配置未设置
                service_configured = False
                all_configured = False
        
        service_status = "✅ 完整" if service_configured else "❌ 不完整"
        print(f"   服务配置状态: {service_status}\n")
    
    # 总体结论
    if all_configured:
        print("✅ 所有必要的Azure服务配置已完成，可以进行部署")
    else:
        print("❌ 部分Azure服务配置缺失，请完成配置后再进行部署")

if __name__ == "__main__":
    check_config() 