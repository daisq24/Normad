#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot Framework辅助函数
"""

import time
import logging
import uuid
import datetime
from typing import Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

def get_iso_timestamp() -> str:
    """
    获取标准ISO8601格式的时间戳
    
    Returns:
        str: ISO8601格式的时间戳
    """
    return datetime.datetime.utcnow().isoformat() + "Z"

def ensure_valid_activity(activity: Dict[str, Any]) -> Dict[str, Any]:
    """
    确保活动符合Bot Framework ActivitySchema规范
    
    Args:
        activity: 输入活动对象
        
    Returns:
        Dict: 标准化的活动对象
    """
    if not isinstance(activity, dict):
        logger.error("活动不是字典类型")
        raise TypeError("Activity must be a dictionary")
    
    # 基本必填字段检查
    required_fields = ["type"]
    for field in required_fields:
        if field not in activity:
            logger.error(f"活动缺少必要字段: {field}")
            raise ValueError(f"Activity is missing required field: {field}")
    
    # 确保有id字段
    if "id" not in activity:
        activity["id"] = str(uuid.uuid4())
    
    # 确保有timestamp字段
    if "timestamp" not in activity:
        activity["timestamp"] = get_iso_timestamp()
    
    # 确保from字段正确
    if "from" not in activity:
        activity["from"] = {
            "id": f"dl_{int(time.time())}",
            "name": "User"
        }
    elif not isinstance(activity["from"], dict):
        activity["from"] = {
            "id": f"dl_{int(time.time())}",
            "name": "User"
        }
    elif "id" not in activity["from"]:
        activity["from"]["id"] = f"dl_{int(time.time())}"
    
    # 确保conversation字段正确
    if "conversation" not in activity:
        activity["conversation"] = {
            "id": f"conversation_{uuid.uuid4()}"
        }
    elif not isinstance(activity["conversation"], dict):
        activity["conversation"] = {
            "id": f"conversation_{uuid.uuid4()}"
        }
    elif "id" not in activity["conversation"]:
        activity["conversation"]["id"] = f"conversation_{uuid.uuid4()}"
    
    # 确保用户ID有dl_前缀
    if "from" in activity and "id" in activity["from"] and not str(activity["from"]["id"]).startswith("dl_"):
        old_id = activity["from"]["id"]
        activity["from"]["id"] = f"dl_{old_id}"
    
    # 添加其他可能需要的默认字段
    if "channelId" not in activity:
        activity["channelId"] = "directline"
    
    if "locale" not in activity:
        activity["locale"] = "zh-CN"
    
    return activity

def format_bot_response(text: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    格式化Bot响应为标准Activity
    
    Args:
        text: 响应文本
        conversation_id: 会话ID
        
    Returns:
        Dict: 格式化的活动对象
    """
    if not conversation_id:
        conversation_id = f"conversation_{uuid.uuid4()}"
    
    return {
        "type": "message",
        "id": str(uuid.uuid4()),
        "timestamp": get_iso_timestamp(),
        "channelId": "directline",
        "from": {
            "id": "bot",
            "name": "NomadNavigator"
        },
        "conversation": {
            "id": conversation_id
        },
        "text": text,
        "locale": "zh-CN"
    }

def get_simple_activity(text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    创建简单的消息活动
    
    Args:
        text: 消息文本
        user_id: 用户ID
        
    Returns:
        Dict: 活动对象
    """
    if not user_id:
        user_id = f"dl_{int(time.time())}"
    elif not user_id.startswith("dl_"):
        user_id = f"dl_{user_id}"
    
    return {
        "type": "message",
        "id": str(uuid.uuid4()),
        "timestamp": get_iso_timestamp(),
        "channelId": "directline",
        "from": {
            "id": user_id,
            "name": "User"
        },
        "conversation": {
            "id": f"conversation_{uuid.uuid4()}"
        },
        "text": text,
        "locale": "zh-CN"
    }

def create_adapter_request(activity: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建Bot Framework适配器可以解析的请求对象
    
    Args:
        activity: 活动对象
        
    Returns:
        Dict: 适配器请求对象
    """
    # 确保活动是有效的
    activity = ensure_valid_activity(activity)
    
    # 创建请求对象，这是适配器parse_request期望的格式
    adapter_request = {
        "body": activity,
        "headers": {
            "Content-Type": "application/json"
        }
    }
    
    return adapter_request 