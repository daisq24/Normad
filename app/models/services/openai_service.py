#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Azure OpenAI服务 - 处理与Azure OpenAI的交互
"""

import logging
import json
import re
import openai
from app.utils.config import SETTINGS

# 配置日志
logger = logging.getLogger(__name__)

class OpenAIService:
    """Azure OpenAI服务类，用于处理与Azure OpenAI的所有交互"""
    
    def __init__(self):
        """初始化OpenAI服务"""
        # 配置Azure OpenAI
        openai.api_type = "azure"
        openai.api_base = SETTINGS.AZURE_OPENAI_ENDPOINT
        openai.api_key = SETTINGS.AZURE_OPENAI_KEY
        openai.api_version = "2023-05-15"
        
        # 部署名称
        self.deployment_name = SETTINGS.AZURE_OPENAI_DEPLOYMENT
        
        logger.info("Azure OpenAI服务已初始化")
    
    async def get_completion(self, system_prompt, user_prompt, max_tokens=1000, temperature=0.7):
        """
        获取AI完成回答
        
        Args:
            system_prompt (str): 系统角色提示
            user_prompt (str): 用户提示
            max_tokens (int): 最大生成令牌数
            temperature (float): 生成多样性参数
            
        Returns:
            str: AI生成的回答
        """
        try:
            logger.info(f"请求Azure OpenAI生成，最大令牌数:{max_tokens}，温度:{temperature}")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                n=1,
                stop=None,
            )
            
            # 提取生成的文本
            content = response.choices[0].message.content
            
            return content
            
        except Exception as e:
            logger.error(f"Azure OpenAI调用失败: {str(e)}")
            raise Exception(f"无法获取AI回答: {str(e)}")
    
    async def extract_entities(self, text):
        """
        从文本中提取实体
        
        Args:
            text (str): 要分析的文本
            
        Returns:
            dict: 提取的实体
        """
        try:
            system_prompt = """
            你是一个专门负责从数字游民请求中提取实体的AI助手。分析提供的文本，提取以下类型的实体：
            - 地点(locations): 任何提到的城市、国家或地区
            - 预算(budget): 提到的预算限制
            - 时间(time): 任何提到的时间段、月份或季节
            - 偏好(preferences): 表达的偏好或需求(如'良好网络'、'温暖气候'等)
            - 限制(constraints): 任何提到的限制条件
            
            以JSON格式输出结果，使用上述类别作为键。
            """
            
            user_prompt = f"从以下文本中提取实体:\n\n{text}"
            
            result = await self.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # 解析JSON
            try:
                # 清理Markdown代码块标记
                cleaned_result = self._clean_markdown_json(result)
                entities = json.loads(cleaned_result)
                return entities
            except json.JSONDecodeError:
                logger.warning(f"无法解析实体提取结果为JSON: {result}")
                return {}
                
        except Exception as e:
            logger.error(f"实体提取失败: {str(e)}")
            return {}
            
    def _clean_markdown_json(self, text):
        """清理Markdown代码块中的JSON文本
        
        Args:
            text (str): 可能包含Markdown格式的JSON文本
            
        Returns:
            str: 清理后的JSON文本
        """
        # 尝试匹配 ```json ... ``` 格式
        json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(json_block_pattern, text)
        
        if match:
            # 提取代码块内容
            return match.group(1).strip()
        
        # 如果没有Markdown格式，直接返回原文本
        return text 