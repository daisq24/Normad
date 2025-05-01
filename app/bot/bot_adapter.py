#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自定义Bot Framework适配器
"""

import json
import logging
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity

logger = logging.getLogger(__name__)

class CustomBotAdapter(BotFrameworkAdapter):
    """
    扩展BotFrameworkAdapter以支持直接处理活动对象
    """
    
    def __init__(self, settings: BotFrameworkAdapterSettings):
        super().__init__(settings)
        logger.info("初始化自定义Bot适配器")
        
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
        
        # 检查请求类型
        if isinstance(req, dict) and 'body' in req and isinstance(req['body'], dict):
            # 使用标准适配器处理
            logger.debug("使用标准适配器处理请求")
            return await super().process_activity(req, auth_header, logic)
        else:
            # 尝试将req作为直接活动对象处理
            logger.debug("尝试将请求作为直接活动对象处理")
            try:
                # 创建活动对象
                activity = Activity().deserialize(req) if not isinstance(req, Activity) else req
                
                # 创建上下文
                context = await self.create_context(activity)
                
                # 运行逻辑
                await logic(context)
                
                # 返回空响应
                return None
            except Exception as e:
                logger.exception(f"处理直接活动对象时出错: {e}")
                raise 