#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot应用 - 使用Bot Framework SDK
"""

import logging
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
    
    # 创建适配器
    adapter = BotFrameworkAdapter(settings)
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
    
    async def on_turn(self, turn_context: TurnContext):
        """处理活动轮次"""
        
        # 处理消息活动
        if turn_context.activity.type == ActivityTypes.message:
            # 获取用户输入
            user_input = turn_context.activity.text
            
            # 处理用户输入
            response = await self.nomad_agent.process_input(user_input, turn_context)
            
            # 发送响应
            await turn_context.send_activity(response)
        
        # 处理会话更新活动（如用户加入对话）
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            # 检查成员是否已添加
            if turn_context.activity.members_added:
                # 遍历添加的成员
                for member in turn_context.activity.members_added:
                    # 排除Bot自己
                    if member.id != turn_context.activity.recipient.id:
                        # 发送欢迎消息
                        welcome_message = (
                            f"欢迎使用 {SETTINGS.APP_NAME}! 🌍✈️\n\n"
                            f"我可以帮助你规划全球旅行路线，管理签证要求，并根据你的预算和偏好优化生活决策。\n\n"
                            f"例如，你可以问我:\n"
                            f"- '我想明年在欧洲和东南亚之间远程办公，预算每月1500美元以内，可以帮我推荐城市和安排吗？'\n"
                            f"- '泰国的签证政策是怎样的？对数字游民有哪些限制？'\n"
                            f"- '我想在气候温和的地方生活3个月，网络质量好，预算适中，有什么推荐？'\n\n"
                            f"请告诉我你的旅行计划和偏好，我会为你提供个性化建议！"
                        )
                        await turn_context.send_activity(welcome_message)
        
        # 保存状态
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

# 创建Bot应用实例
BOT_APP = NomadNavigatorBot(conversation_state, user_state) 