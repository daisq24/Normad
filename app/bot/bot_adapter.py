#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自定义Bot Framework适配器
"""

import json
import logging
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio

logger = logging.getLogger(__name__)

class CustomBotAdapter(BotFrameworkAdapter):
    """
    扩展BotFrameworkAdapter以支持直接处理活动对象
    """
    
    def __init__(self, settings: BotFrameworkAdapterSettings):
        super().__init__(settings)
        logger.info("初始化自定义Bot适配器")
        self.settings = settings
        
    async def process_activity(self, req, auth_header, logic):
        """
        处理活动请求，支持直接的活动对象或标准请求
        
        Args:
            req: 请求对象或活动对象
            auth_header: 授权头
            logic: Bot逻辑处理函数
            
        Returns:
            InvokeResponse: 响应对象
        """
        logger.debug(f"处理活动请求: {type(req)}")
        
        try:
            # 检查请求类型
            if isinstance(req, dict) and 'body' in req and isinstance(req['body'], dict):
                # 使用标准适配器处理
                logger.debug("使用标准适配器处理请求")
                return await super().process_activity(req, auth_header, logic)
            elif isinstance(req, dict):
                # 作为活动对象处理
                logger.debug(f"请求作为活动对象处理: {json.dumps(req, default=str)[:200]}...")
                
                # 创建活动对象
                activity = Activity().deserialize(req)
                logger.debug(f"已反序列化活动: {activity.type}, ID: {activity.id}")
                
                # 检查授权 - 在测试环境或没有AppID时跳过身份验证
                if not self.settings.app_id or self.settings.app_id == "":
                    logger.info("AppID未设置，跳过身份验证")
                elif not auth_header or auth_header == "":
                    logger.warning("缺少授权头，但在非严格模式下继续")
                else:
                    # 在生产环境中，这里应该验证auth_header
                    logger.info(f"使用授权头: {auth_header[:20]}...")
                
                # 创建上下文
                context = TurnContext(self, activity)
                
                # 执行Bot逻辑
                await logic(context)
                
                # 返回空响应
                return None
            else:
                logger.error(f"无法识别的请求类型: {type(req)}")
                raise TypeError("无法识别的请求类型")
        except Exception as e:
            logger.exception(f"处理活动请求时出错: {e}")
            # 重新抛出异常，保留原始堆栈跟踪
            raise
            
    async def create_context(self, activity):
        """
        创建Turn上下文
        
        Args:
            activity: 活动对象
            
        Returns:
            TurnContext: 上下文对象
        """
        logger.debug(f"创建上下文, 活动类型: {activity.type}")
        context = TurnContext(self, activity)
        return context 