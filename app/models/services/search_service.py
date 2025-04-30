#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Azure AI Search服务 - 处理与Azure AI Search的交互
"""

import logging
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from app.utils.config import SETTINGS

# 配置日志
logger = logging.getLogger(__name__)

class AzureSearchService:
    """Azure AI Search服务类，用于检索目的地、签证和生活成本数据"""
    
    def __init__(self):
        """初始化搜索服务"""
        # 定义搜索服务端点和凭据
        self.endpoint = f"https://{SETTINGS.AZURE_SEARCH_SERVICE}.search.windows.net/"
        self.credential = AzureKeyCredential(SETTINGS.AZURE_SEARCH_KEY)
        
        # 初始化各种索引客户端
        self.destinations_index = SETTINGS.AZURE_SEARCH_INDEX
        self.visa_index = f"{SETTINGS.AZURE_SEARCH_INDEX}_visa"
        self.cost_index = f"{SETTINGS.AZURE_SEARCH_INDEX}_cost"
        
        logger.info("Azure AI Search服务已初始化")
    
    async def search_destinations(self, query, top=10):
        """
        搜索目的地数据
        
        Args:
            query (str): 搜索查询
            top (int): 返回结果数量
            
        Returns:
            list: 匹配的目的地列表
        """
        try:
            # 创建搜索客户端
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.destinations_index,
                credential=self.credential
            )
            
            # 执行搜索
            results = search_client.search(
                search_text=query,
                query_type=QueryType.SEMANTIC,
                query_language="zh-CN",
                search_fields=["name", "country", "region", "description", "tags"],
                select=["id", "name", "country", "region", "climate", "cost_index", 
                        "internet_speed", "safety_index", "description", "digital_nomad_friendly"],
                top=top
            )
            
            # 处理结果
            destinations = []
            for result in results:
                destinations.append(dict(result))
            
            logger.info(f"目的地搜索 '{query}' 返回 {len(destinations)} 条结果")
            return destinations
            
        except Exception as e:
            logger.error(f"目的地搜索失败: {str(e)}")
            # 返回模拟数据
            return self._get_mock_destinations()
    
    async def search_visa_info(self, query, top=5):
        """
        搜索签证信息
        
        Args:
            query (str): 搜索查询
            top (int): 返回结果数量
            
        Returns:
            list: 匹配的签证信息列表
        """
        try:
            # 创建搜索客户端
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.visa_index,
                credential=self.credential
            )
            
            # 执行搜索
            results = search_client.search(
                search_text=query,
                query_type=QueryType.SEMANTIC,
                query_language="zh-CN",
                search_fields=["country", "visa_type", "requirements", "restrictions"],
                select=["id", "country", "visa_type", "duration", "requirements", 
                        "restrictions", "extension_options", "digital_nomad_status"],
                top=top
            )
            
            # 处理结果
            visa_info = []
            for result in results:
                visa_info.append(dict(result))
            
            logger.info(f"签证信息搜索 '{query}' 返回 {len(visa_info)} 条结果")
            return visa_info
            
        except Exception as e:
            logger.error(f"签证信息搜索失败: {str(e)}")
            # 返回模拟数据
            return self._get_mock_visa_info()
    
    async def search_cost_info(self, query, top=5):
        """
        搜索生活成本信息
        
        Args:
            query (str): 搜索查询
            top (int): 返回结果数量
            
        Returns:
            list: 匹配的生活成本信息列表
        """
        try:
            # 创建搜索客户端
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.cost_index,
                credential=self.credential
            )
            
            # 执行搜索
            results = search_client.search(
                search_text=query,
                query_type=QueryType.SEMANTIC,
                query_language="zh-CN",
                search_fields=["city", "country", "description"],
                select=["id", "city", "country", "accommodation_cost", "food_cost", 
                        "transportation_cost", "total_monthly", "internet_cost", "coworking_cost"],
                top=top
            )
            
            # 处理结果
            cost_info = []
            for result in results:
                cost_info.append(dict(result))
            
            logger.info(f"生活成本搜索 '{query}' 返回 {len(cost_info)} 条结果")
            return cost_info
            
        except Exception as e:
            logger.error(f"生活成本搜索失败: {str(e)}")
            # 返回模拟数据
            return self._get_mock_cost_info()
    
    def _get_mock_destinations(self):
        """获取模拟目的地数据"""
        return [
            {
                "id": "1",
                "name": "清迈",
                "country": "泰国",
                "region": "东南亚",
                "climate": "热带季风气候",
                "cost_index": 0.4,  # 相对纽约的生活成本指数
                "internet_speed": 30,  # Mbps
                "safety_index": 0.7,  # 0-1之间的安全指数
                "description": "泰国北部城市，数字游民热门目的地，气候宜人，生活成本低，有丰富的咖啡馆和共享工作空间。",
                "digital_nomad_friendly": 0.9  # 0-1之间的友好指数
            },
            {
                "id": "2",
                "name": "里斯本",
                "country": "葡萄牙",
                "region": "欧洲",
                "climate": "地中海气候",
                "cost_index": 0.6,
                "internet_speed": 50,
                "safety_index": 0.85,
                "description": "葡萄牙首都，欧洲新兴数字游民热点，气候温和，食物美味，文化丰富，有良好的英语普及率。",
                "digital_nomad_friendly": 0.85
            },
            {
                "id": "3",
                "name": "巴厘岛",
                "country": "印度尼西亚",
                "region": "东南亚",
                "climate": "热带气候",
                "cost_index": 0.45,
                "internet_speed": 25,
                "safety_index": 0.75,
                "description": "印尼著名岛屿，拥有美丽的海滩和丰富的瑜伽、冥想等活动，共享工作空间丰富，数字游民社区活跃。",
                "digital_nomad_friendly": 0.85
            },
            {
                "id": "4",
                "name": "墨西哥城",
                "country": "墨西哥",
                "region": "北美",
                "climate": "热带高原气候",
                "cost_index": 0.5,
                "internet_speed": 40,
                "safety_index": 0.6,
                "description": "拉丁美洲最大城市之一，文化丰富，美食闻名，生活成本适中，有良好的数字游民基础设施。",
                "digital_nomad_friendly": 0.8
            },
            {
                "id": "5",
                "name": "布达佩斯",
                "country": "匈牙利",
                "region": "欧洲",
                "climate": "温带大陆性气候",
                "cost_index": 0.55,
                "internet_speed": 60,
                "safety_index": 0.8,
                "description": "匈牙利首都，欧洲性价比极高的城市，有丰富的咖啡文化和共享工作空间，公共交通便利。",
                "digital_nomad_friendly": 0.8
            }
        ]
    
    def _get_mock_visa_info(self):
        """获取模拟签证信息数据"""
        return [
            {
                "id": "1",
                "country": "泰国",
                "visa_type": "旅游签证",
                "duration": "60天",
                "requirements": "有效护照（至少6个月有效期），往返机票证明，住宿证明，资金证明（每人2万泰铢现金或等值货币）",
                "restrictions": "不允许工作，可延期一次额外30天",
                "extension_options": "可在泰国移民局申请30天延期，费用1900泰铢",
                "digital_nomad_status": "灰色地带，理论上不允许工作，但对远程工作通常不严格执行"
            },
            {
                "id": "2",
                "country": "葡萄牙",
                "visa_type": "D7签证（被动收入签证）",
                "duration": "4个月，之后可申请2年居留许可",
                "requirements": "有效护照，健康保险，无犯罪记录证明，证明每月有被动收入（约€760/月）",
                "restrictions": "需要在葡萄牙居住至少16个月（两年内）",
                "extension_options": "可续签3年，之后可申请永久居留或公民身份",
                "digital_nomad_status": "适合数字游民，可合法工作"
            },
            {
                "id": "3",
                "country": "印度尼西亚",
                "visa_type": "B211A商务签证",
                "duration": "60天，可延期最多4次（每次30天）",
                "requirements": "有效护照，往返机票，本地担保信，资金证明，商务活动证明",
                "restrictions": "不允许工作获得印尼收入，需要每60天离境再入境",
                "extension_options": "可延期4次，每次30天，最长停留180天",
                "digital_nomad_status": "灰色地带，适合短期数字游民"
            },
            {
                "id": "4",
                "country": "墨西哥",
                "visa_type": "旅游卡",
                "duration": "180天",
                "requirements": "有效护照，返程机票，酒店预订（可选）",
                "restrictions": "不允许工作获得墨西哥收入",
                "extension_options": "不可延期，需要离境再入境",
                "digital_nomad_status": "适合数字游民，对远程工作态度宽松"
            },
            {
                "id": "5",
                "country": "匈牙利",
                "visa_type": "白卡（White Card）",
                "duration": "1年，可续签",
                "requirements": "有效护照，健康保险，地址证明，每月最低收入约€2000",
                "restrictions": "需要向匈牙利缴税",
                "extension_options": "可续签，满5年可申请永久居留",
                "digital_nomad_status": "专为数字游民设计的签证"
            }
        ]
    
    def _get_mock_cost_info(self):
        """获取模拟生活成本数据"""
        return [
            {
                "id": "1",
                "city": "清迈",
                "country": "泰国",
                "accommodation_cost": 400,  # 美元/月（单间公寓）
                "food_cost": 350,  # 美元/月
                "transportation_cost": 50,  # 美元/月
                "internet_cost": 25,  # 美元/月
                "coworking_cost": 100,  # 美元/月
                "total_monthly": 925  # 美元/月
            },
            {
                "id": "2",
                "city": "里斯本",
                "country": "葡萄牙",
                "accommodation_cost": 800,
                "food_cost": 400,
                "transportation_cost": 40,
                "internet_cost": 30,
                "coworking_cost": 120,
                "total_monthly": 1390
            },
            {
                "id": "3",
                "city": "巴厘岛",
                "country": "印度尼西亚",
                "accommodation_cost": 500,
                "food_cost": 300,
                "transportation_cost": 80,
                "internet_cost": 40,
                "coworking_cost": 100,
                "total_monthly": 1020
            },
            {
                "id": "4",
                "city": "墨西哥城",
                "country": "墨西哥",
                "accommodation_cost": 600,
                "food_cost": 350,
                "transportation_cost": 50,
                "internet_cost": 30,
                "coworking_cost": 110,
                "total_monthly": 1140
            },
            {
                "id": "5",
                "city": "布达佩斯",
                "country": "匈牙利",
                "accommodation_cost": 550,
                "food_cost": 300,
                "transportation_cost": 30,
                "internet_cost": 20,
                "coworking_cost": 120,
                "total_monthly": 1020
            }
        ] 