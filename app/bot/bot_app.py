#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot应用 - 使用Bot Framework SDK
"""

import logging
import traceback
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState
)
from botbuilder.schema import Activity, ActivityTypes

from app.utils.config import SETTINGS
from app.models.nomad_agent import NomadAgent
from app.bot.bot_adapter import CustomBotAdapter

# 配置日志
logger = logging.getLogger(__name__)

# 创建内存存储
memory = MemoryStorage()

# 创建会话状态
conversation_state = ConversationState(memory)

# 创建用户状态
user_state = UserState(memory)

def create_adapter():
    """创建Bot Framework适配器"""
    
    # 定义错误处理函数
    async def on_error(context, error):
        logger.error(f"Bot框架适配器错误: {str(error)}")
        logger.error(f"错误堆栈跟踪: {traceback.format_exc()}")
        
        # 发送错误消息给用户
        await context.send_activity("抱歉，机器人遇到了问题。")
        
        # 为开发环境打印详细错误
        if SETTINGS.DEBUG:
            await context.send_activity(f"错误详情: {str(error)}")
        
        # 清除会话状态
        await conversation_state.delete(context)
    
    # 创建Bot适配器设置
    settings = BotFrameworkAdapterSettings(
        app_id=SETTINGS.MICROSOFT_APP_ID,
        app_password=SETTINGS.MICROSOFT_APP_PASSWORD
    )
    
    logger.info(f"创建Bot适配器，App ID: {SETTINGS.MICROSOFT_APP_ID}")
    if not SETTINGS.MICROSOFT_APP_ID or not SETTINGS.MICROSOFT_APP_PASSWORD:
        logger.warning("未设置App ID或密码，Bot将以非验证模式运行")
    
    # 创建自定义适配器
    adapter = CustomBotAdapter(settings)
    adapter.on_turn_error = on_error
    
    return adapter

class NomadNavigatorBot:
    """NomadNavigator AI Bot应用类"""
    
    def __init__(self, conversation_state, user_state):
        """初始化Bot"""
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.conversation_state_accessor = self.conversation_state.create_property("ConversationState")
        self.user_state_accessor = self.user_state.create_property("UserState")
        self.nomad_agent = NomadAgent()  # 创建Agent实例
        logger.info("NomadNavigator Bot已初始化")
    
    async def on_turn(self, turn_context: TurnContext):
        """处理活动轮次"""
        logger.info(f"收到活动: {turn_context.activity.type}")
        
        # 处理消息活动
        if turn_context.activity.type == ActivityTypes.message:
            # 获取用户输入
            user_input = turn_context.activity.text
            logger.info(f"收到用户消息: {user_input}")
            
            try:
                # 处理用户输入
                response = await self.nomad_agent.process_input(user_input, turn_context)
                logger.info(f"生成响应: {response}")
                
                # 发送响应
                await turn_context.send_activity(response)
            except Exception as e:
                logger.exception(f"处理消息时出错: {e}")
                await turn_context.send_activity(f"处理您的消息时出现错误: {str(e)}")
        
        # 处理事件活动
        elif turn_context.activity.type == ActivityTypes.event:
            event_name = turn_context.activity.name
            logger.info(f"收到事件: {event_name}")
            
            # 处理加入事件
            if event_name == "webchat/join":
                logger.info("处理webchat/join事件")
                await turn_context.send_activity("👋 欢迎使用NomadNavigator AI! 我是您的数字游民智能助手，可以帮助您规划旅行路径、了解签证政策、比较生活成本。有什么我可以帮您的吗？")
        
        # 处理会话更新活动
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            logger.info("处理会话更新事件")
            if turn_context.activity.members_added:
                for member in turn_context.activity.members_added:
                    if member.id != turn_context.activity.recipient.id:
                        await turn_context.send_activity("👋 欢迎使用NomadNavigator AI! 我是您的数字游民智能助手，可以帮助您规划旅行路径、了解签证政策、比较生活成本。有什么我可以帮您的吗？")
        
        # 保存状态
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

# 创建Bot应用实例
BOT_APP = NomadNavigatorBot(conversation_state, user_state) 