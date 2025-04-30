#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
游牧代理模型 - 主要智能代理实现
"""

import logging
import json
import asyncio
from botbuilder.core import TurnContext
from app.utils.config import SETTINGS
from app.models.services.openai_service import OpenAIService
from app.models.services.search_service import AzureSearchService
from app.models.services.cosmos_service import CosmosDBService

# 配置日志
logger = logging.getLogger(__name__)

class NomadAgent:
    """NomadNavigator AI代理类"""
    
    def __init__(self):
        """初始化代理"""
        # 创建服务实例
        self.openai_service = OpenAIService()
        self.search_service = AzureSearchService()
        self.cosmos_service = CosmosDBService()
        
        # 能力状态
        self.perception_enabled = True
        self.planning_enabled = True
        self.memory_enabled = True
        self.action_enabled = True
    
    async def process_input(self, user_input: str, turn_context: TurnContext) -> str:
        """处理用户输入"""
        logger.info(f"处理用户输入: {user_input}")
        
        try:
            # 1. 感知阶段 - 理解用户输入
            intent, entities = await self._perception(user_input)
            
            # 2. 检索阶段 - 获取相关信息
            search_results = await self._retrieve_information(intent, entities)
            
            # 3. 规划阶段 - 生成行动方案
            plan = await self._planning(intent, entities, search_results)
            
            # 4. 记忆阶段 - 保存用户偏好和历史
            await self._memory(user_input, intent, entities, turn_context)
            
            # 5. 行动阶段 - 执行计划并生成响应
            response = await self._action(plan, intent, entities, search_results, turn_context)
            
            return response
            
        except Exception as e:
            logger.error(f"处理用户输入时出错: {str(e)}")
            return f"抱歉，处理您的请求时出现问题。请稍后再试。错误: {str(e) if SETTINGS.DEBUG else '技术故障'}"
    
    async def _perception(self, user_input: str):
        """感知阶段 - 理解用户输入内容"""
        if not self.perception_enabled:
            return "general", {}
        
        try:
            # 使用OpenAI进行意图识别和实体提取
            system_prompt = """
            你是一个专门负责理解数字游民请求的AI助手。你的任务是:
            1. 识别用户意图(旅行规划/签证信息/预算咨询/目的地推荐/生活方式)
            2. 提取实体(地点/预算/时间/偏好/限制条件)
            输出JSON格式，包含intent和entities字段
            """
            
            user_prompt = f"分析以下数字游民的请求并提取意图和实体：\n\n{user_input}"
            
            result = await self.openai_service.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=500
            )
            
            # 解析JSON响应
            try:
                response_json = json.loads(result)
                intent = response_json.get("intent", "general")
                entities = response_json.get("entities", {})
                
                logger.info(f"识别到的意图: {intent}, 实体: {entities}")
                return intent, entities
            except json.JSONDecodeError:
                logger.warning(f"无法解析OpenAI响应为JSON: {result}")
                return "general", {}
                
        except Exception as e:
            logger.error(f"感知阶段错误: {str(e)}")
            return "general", {}
    
    async def _retrieve_information(self, intent, entities):
        """检索阶段 - 获取相关信息"""
        results = {}
        
        try:
            # 根据意图和实体构建搜索查询
            search_terms = []
            
            # 添加地点信息
            if "locations" in entities:
                for location in entities["locations"]:
                    search_terms.append(location)
            
            # 添加预算信息
            if "budget" in entities:
                search_terms.append(f"budget:{entities['budget']}")
            
            # 添加时间/季节信息
            if "time" in entities:
                search_terms.append(entities["time"])
            
            # 添加偏好
            if "preferences" in entities:
                for pref in entities["preferences"]:
                    search_terms.append(pref)
            
            # 构建查询字符串
            query = " ".join(search_terms) if search_terms else intent
            
            # 执行搜索
            if intent == "visa_info":
                # 签证信息搜索
                results["visa_data"] = await self.search_service.search_visa_info(query)
            elif intent == "destination_recommendation":
                # 目的地推荐搜索
                results["destinations"] = await self.search_service.search_destinations(query)
            elif intent == "cost_of_living":
                # 生活成本搜索
                results["cost_data"] = await self.search_service.search_cost_info(query)
            elif intent == "travel_planning":
                # 旅行规划相关的所有信息
                visa_task = self.search_service.search_visa_info(query)
                dest_task = self.search_service.search_destinations(query)
                cost_task = self.search_service.search_cost_info(query)
                
                # 并行执行搜索任务
                visa_results, dest_results, cost_results = await asyncio.gather(
                    visa_task, dest_task, cost_task
                )
                
                results["visa_data"] = visa_results
                results["destinations"] = dest_results
                results["cost_data"] = cost_results
            
            logger.info(f"检索到的信息: {json.dumps(results, ensure_ascii=False)[:200]}...")
            return results
            
        except Exception as e:
            logger.error(f"检索阶段错误: {str(e)}")
            return {}
    
    async def _planning(self, intent, entities, search_results):
        """规划阶段 - 生成行动方案"""
        if not self.planning_enabled:
            return {}
        
        try:
            # 根据意图和搜索结果构建规划提示
            system_prompt = """
            你是一个专业的旅行规划者，擅长为数字游民创建详细的旅行计划。
            基于用户意图、实体和检索到的信息，制定一个结构化的行动计划。
            考虑以下因素:
            1. 签证限制和要求
            2. 预算限制
            3. 气候和季节因素
            4. 网络连接质量
            5. 生活成本
            6. 安全因素
            
            输出应为JSON格式，包含以下字段:
            - plan_type: 计划类型(如"itinerary", "visa_advice", "destination_ranking")
            - timeline: 时间线(如适用)
            - recommendations: 推荐列表
            - actions: 建议的行动
            - alerts: 重要提醒或注意事项
            """
            
            # 构建用户提示
            user_prompt = f"""
            用户意图: {intent}
            实体信息: {json.dumps(entities, ensure_ascii=False)}
            搜索结果: {json.dumps(search_results, ensure_ascii=False)}
            
            请基于以上信息为数字游民生成一个详细的行动计划。
            """
            
            result = await self.openai_service.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1500
            )
            
            # 解析JSON响应
            try:
                plan = json.loads(result)
                logger.info(f"生成的计划: {json.dumps(plan, ensure_ascii=False)[:200]}...")
                return plan
            except json.JSONDecodeError:
                logger.warning(f"无法解析OpenAI响应为JSON: {result}")
                # 如果无法解析为JSON，直接返回文本结果
                return {"plan_text": result}
                
        except Exception as e:
            logger.error(f"规划阶段错误: {str(e)}")
            return {}
    
    async def _memory(self, user_input, intent, entities, turn_context):
        """记忆阶段 - 保存用户偏好和历史"""
        if not self.memory_enabled:
            return
        
        try:
            # 获取用户ID
            user_id = turn_context.activity.from_property.id
            
            # 构建记忆条目
            memory_entry = {
                "user_id": user_id,
                "timestamp": turn_context.activity.timestamp.isoformat() if turn_context.activity.timestamp else None,
                "user_input": user_input,
                "intent": intent,
                "entities": entities
            }
            
            # 保存到CosmosDB
            await self.cosmos_service.save_user_interaction(memory_entry)
            
            # 更新用户偏好
            if "preferences" in entities:
                await self.cosmos_service.update_user_preferences(
                    user_id, 
                    entities.get("preferences", [])
                )
            
            logger.info(f"已保存用户 {user_id} 的交互记录")
            
        except Exception as e:
            logger.error(f"记忆阶段错误: {str(e)}")
    
    async def _action(self, plan, intent, entities, search_results, turn_context):
        """行动阶段 - 执行计划并生成响应"""
        if not self.action_enabled:
            return "我目前无法执行此操作。"
        
        try:
            # 获取用户ID
            user_id = turn_context.activity.from_property.id
            
            # 获取用户历史偏好
            user_preferences = await self.cosmos_service.get_user_preferences(user_id)
            
            # 构建响应生成提示
            system_prompt = """
            你是NomadNavigator AI，一个为数字游民提供旅行和生活建议的智能助手。
            你的任务是根据提供的计划、用户意图、检索到的信息和用户历史偏好，生成一个友好、信息丰富且个性化的响应。
            
            你的回复应该:
            1. 直接解答用户的问题
            2. 提供具体和实用的建议
            3. 考虑用户的历史偏好
            4. 包含相关的旅行提示、签证要求或生活成本信息
            5. 提供清晰的后续步骤或建议的行动
            
            使用友好、专业的语气，避免过于冗长。重点放在提供有价值的实用信息上。
            """
            
            # 构建用户提示
            user_prompt = f"""
            用户意图: {intent}
            用户实体: {json.dumps(entities, ensure_ascii=False)}
            用户历史偏好: {json.dumps(user_preferences, ensure_ascii=False)}
            制定的计划: {json.dumps(plan, ensure_ascii=False)}
            检索到的信息: {json.dumps(search_results, ensure_ascii=False)}
            
            请根据以上信息，生成一个友好、信息丰富且个性化的响应。
            """
            
            response = await self.openai_service.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1000
            )
            
            logger.info(f"生成的响应: {response[:100]}...")
            return response
                
        except Exception as e:
            logger.error(f"行动阶段错误: {str(e)}")
            return "抱歉，我在处理您的请求时遇到了问题。请稍后再试。" 