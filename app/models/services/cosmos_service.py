#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Azure CosmosDB for MongoDB服务 - 处理与Azure CosmosDB for MongoDB的交互
"""

import logging
import json
import uuid
from datetime import datetime
import pymongo
from app.utils.config import SETTINGS

# 配置日志
logger = logging.getLogger(__name__)

class CosmosDBService:
    """Azure CosmosDB for MongoDB服务类，用于存储用户偏好和历史记录"""
    
    def __init__(self):
        """初始化CosmosDB for MongoDB服务"""
        try:
            # 创建MongoDB客户端连接
            connection_string = SETTINGS.AZURE_COSMOS_CONNECTION_STRING
            
            if not connection_string:
                # 构建连接字符串（如果没有提供完整的连接字符串）
                connection_string = f"mongodb://{SETTINGS.AZURE_COSMOS_ACCOUNT}:{SETTINGS.AZURE_COSMOS_KEY}@{SETTINGS.AZURE_COSMOS_ACCOUNT}.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName={SETTINGS.AZURE_COSMOS_ACCOUNT}"
            else:
                # 修正连接字符串中的appName格式问题
                connection_string = connection_string.replace("appName=@nomadnavigator-mongo@", "appName=nomadnavigator-mongo")
                
                # 移除可能的重复部分
                if connection_string.count("mongodb://") > 1:
                    connection_string = connection_string[:connection_string.find("mongodb://", 1)]
                
                # 确保retrywrites=false参数存在
                if "retrywrites=false" not in connection_string.lower():
                    if "?" in connection_string:
                        connection_string += "&retrywrites=false"
                    else:
                        connection_string += "?retrywrites=false"
            
            logger.debug(f"使用连接字符串: {connection_string[:60]}...{connection_string[-30:]}")
                
            # 创建客户端
            self.client = pymongo.MongoClient(connection_string)
            
            # 获取数据库
            self.database = self.client[SETTINGS.AZURE_COSMOS_DATABASE]
            
            # 获取集合（相当于SQL API中的容器）
            self.user_collection = self.database[SETTINGS.AZURE_COSMOS_CONTAINER]
            self.history_collection = self.database[f"{SETTINGS.AZURE_COSMOS_CONTAINER}_history"]
            
            logger.info(f"已连接到MongoDB数据库: {SETTINGS.AZURE_COSMOS_DATABASE}")
            logger.info(f"已连接到MongoDB集合: {SETTINGS.AZURE_COSMOS_CONTAINER}")
            logger.info("Azure CosmosDB for MongoDB服务已初始化")
            
        except Exception as e:
            logger.error(f"初始化CosmosDB for MongoDB服务失败: {str(e)}")
            # 使用模拟数据
            self.client = None
            self.database = None
            self.user_collection = None
            self.history_collection = None
            self.mock_mode = True
            logger.warning("CosmosDB连接失败，切换到模拟模式")
    
    async def get_user_profile(self, user_id):
        """
        获取用户配置文件
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            dict: 用户配置文件
        """
        try:
            if getattr(self, 'mock_mode', False):
                return self._get_mock_user_profile(user_id)
            
            # 查询用户配置
            profile = self.user_collection.find_one({
                "user_id": user_id, 
                "type": "profile"
            })
            
            if profile:
                # 转换MongoDB的_id为字符串（因为ObjectId不可序列化）
                profile["id"] = str(profile.pop("_id"))
                logger.info(f"已获取用户 {user_id} 的配置文件")
                return profile
            else:
                # 用户不存在，创建新用户配置
                new_profile = {
                    "user_id": user_id,  # 分片键
                    "type": "profile",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "preferences": {},
                    "travel_history": []
                }
                
                # 创建新用户
                result = self.user_collection.insert_one(new_profile)
                new_profile["id"] = str(result.inserted_id)
                # 删除MongoDB的_id（可能会自动添加）
                new_profile.pop("_id", None)
                
                logger.info(f"已创建新用户 {user_id} 的配置文件")
                return new_profile
                
        except Exception as e:
            logger.error(f"获取用户配置文件失败: {str(e)}")
            return self._get_mock_user_profile(user_id)
    
    async def update_user_preferences(self, user_id, preferences):
        """
        更新用户偏好
        
        Args:
            user_id (str): 用户ID
            preferences (list): 偏好列表
            
        Returns:
            bool: 是否成功
        """
        try:
            if getattr(self, 'mock_mode', False):
                return True
            
            # 获取用户配置
            profile = await self.get_user_profile(user_id)
            
            # 更新偏好
            current_prefs = profile.get("preferences", {})
            
            # 将新偏好添加到现有偏好中
            for pref in preferences:
                if isinstance(pref, str):
                    # 增加偏好权重或添加新偏好
                    current_prefs[pref] = current_prefs.get(pref, 0) + 1
            
            # 确保查询中包含分片键
            self.user_collection.update_one(
                {"user_id": user_id, "type": "profile"},
                {
                    "$set": {
                        "preferences": current_prefs,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            logger.info(f"已更新用户 {user_id} 的偏好")
            return True
            
        except Exception as e:
            logger.error(f"更新用户偏好失败: {str(e)}")
            return False
    
    async def save_user_interaction(self, interaction):
        """
        保存用户交互记录
        
        Args:
            interaction (dict): 交互记录
            
        Returns:
            bool: 是否成功
        """
        try:
            if getattr(self, 'mock_mode', False):
                return True
            
            # 添加必要字段
            interaction["type"] = "interaction"
            interaction["created_at"] = datetime.utcnow().isoformat()
            
            # 确保包含分片键
            if "user_id" not in interaction and "userId" in interaction:
                interaction["user_id"] = interaction["userId"]
                
            # 保存到历史集合
            self.history_collection.insert_one(interaction)
            
            logger.info(f"已保存用户 {interaction['user_id']} 的交互记录")
            return True
            
        except Exception as e:
            logger.error(f"保存用户交互记录失败: {str(e)}")
            return False
    
    async def get_user_preferences(self, user_id):
        """
        获取用户偏好
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            dict: 用户偏好
        """
        try:
            if getattr(self, 'mock_mode', False):
                return self._get_mock_user_preferences(user_id)
            
            # 获取用户配置
            profile = await self.get_user_profile(user_id)
            
            # 返回偏好
            return profile.get("preferences", {})
            
        except Exception as e:
            logger.error(f"获取用户偏好失败: {str(e)}")
            return {}
    
    async def get_user_interactions(self, user_id, limit=10):
        """
        获取用户历史交互
        
        Args:
            user_id (str): 用户ID
            limit (int): 返回记录数量限制
            
        Returns:
            list: 用户历史交互列表
        """
        try:
            if getattr(self, 'mock_mode', False):
                return []
            
            # 查询历史交互并排序 - 确保包含分片键
            cursor = self.history_collection.find(
                {"user_id": user_id}
            ).sort("created_at", pymongo.DESCENDING).limit(limit)
            
            # 转换结果
            items = []
            for item in cursor:
                # 转换MongoDB的_id为字符串
                item["id"] = str(item.pop("_id"))
                items.append(item)
            
            logger.info(f"已获取用户 {user_id} 的 {len(items)} 条历史交互")
            return items
            
        except Exception as e:
            logger.error(f"获取用户历史交互失败: {str(e)}")
            return []
    
    def _get_mock_user_profile(self, user_id):
        """获取模拟用户配置文件"""
        return {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "profile",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "preferences": self._get_mock_user_preferences(user_id),
            "travel_history": []
        }
    
    def _get_mock_user_preferences(self, user_id):
        """获取模拟用户偏好"""
        # 根据用户ID最后一位数生成不同偏好
        last_digit = int(str(hash(user_id))[-1])
        
        if last_digit < 3:
            # 预算型旅行者
            return {
                "低预算": 3,
                "便宜的食物": 2,
                "公共交通": 2,
                "共享住宿": 1
            }
        elif last_digit < 6:
            # 数字游民工作者
            return {
                "良好网络": 3,
                "咖啡馆工作": 2,
                "共享工作空间": 2,
                "安静环境": 1
            }
        else:
            # 探险型旅行者
            return {
                "自然景观": 3,
                "户外活动": 2,
                "文化体验": 2,
                "地方美食": 1
            } 