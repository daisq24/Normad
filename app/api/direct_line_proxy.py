#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DirectLine代理 - 用于将消息从Web客户端转发到Bot服务
"""

import json
import logging
import requests
from flask import Blueprint, request, jsonify, current_app
import time

# 配置日志
logger = logging.getLogger(__name__)

# 创建Blueprint
direct_line_proxy_bp = Blueprint('direct_line_proxy', __name__)

# DirectLine API URL
DIRECT_LINE_URL = "https://directline.botframework.com/v3/directline"

@direct_line_proxy_bp.route('/tokens/generate', methods=['POST'])
def generate_token():
    """生成DirectLine令牌"""
    try:
        logger.info("收到生成令牌请求")
        secret = request.json.get('secret')
        if not secret:
            logger.error("请求中缺少secret参数")
            return jsonify({'error': 'Secret is required'}), 400
        
        # 添加用户ID参数，如果请求中没有，则生成一个
        user_id = request.json.get('user_id', f'dl_{int(time.time())}')
        
        # 确保用户ID格式正确
        if not user_id.startswith('dl_'):
            logger.warning(f"用户ID格式不正确，自动添加前缀: {user_id}")
            user_id = f'dl_{user_id}'
        
        headers = {
            'Authorization': f'Bearer {secret}',
            'Content-Type': 'application/json'
        }
        
        # DirectLine API期望的正确格式
        params = {
            'User': {
                'Id': user_id,
                'Name': '游客'
            }
        }
        
        logger.debug(f"向DirectLine API发送请求获取令牌，URL: {DIRECT_LINE_URL}/tokens/generate")
        logger.debug(f"请求参数: {params}")
        
        # 增加连接超时和重试逻辑
        max_retries = 2
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.post(
                    f'{DIRECT_LINE_URL}/tokens/generate',
                    headers=headers,
                    json=params,
                    timeout=15  # 增加超时时间
                )
                break
            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"DirectLine API请求失败，已重试{retry_count}次: {str(e)}")
                    return jsonify({'error': f'Failed to connect to DirectLine API: {str(e)}'}), 500
                logger.warning(f"DirectLine API请求失败，正在重试({retry_count}/{max_retries}): {str(e)}")
                time.sleep(1)  # 重试前等待1秒
        
        logger.debug(f"DirectLine API响应: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info("成功获取令牌")
            
            # 返回令牌和其他相关信息
            return jsonify({
                'token': token_data.get('token'),
                'expires_in': token_data.get('expires_in', 3600),
                'conversation_id': token_data.get('conversationId')
            })
        else:
            error_msg = f"DirectLine API返回错误: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {json.dumps(error_details)}"
            except:
                error_msg += f" - {response.text[:200]}"
            
            logger.error(error_msg)
            return jsonify({'error': f'Failed to generate token: {error_msg}'}), response.status_code
            
    except Exception as e:
        error_msg = f"生成令牌时发生异常: {str(e)}"
        logger.exception(error_msg)
        return jsonify({'error': error_msg}), 500

@direct_line_proxy_bp.route('/conversations', methods=['POST'])
def start_conversation():
    """启动会话"""
    try:
        secret = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not secret:
            logger.error("请求中缺少Authorization头部")
            return jsonify({'error': 'Authorization header with Bearer token is required'}), 401
        
        headers = {
            'Authorization': f'Bearer {secret}'
        }
        
        logger.debug(f"向DirectLine API发送请求启动会话")
        response = requests.post(
            f'{DIRECT_LINE_URL}/conversations',
            headers=headers
        )
        
        if response.status_code == 201:
            logger.info("成功启动会话")
            return jsonify(response.json()), 201
        else:
            logger.error(f"启动会话失败: {response.status_code} - {response.text}")
            return jsonify({'error': f'Failed to start conversation: {response.text}'}), response.status_code
    
    except Exception as e:
        logger.exception(f"启动会话时出错: {e}")
        return jsonify({'error': str(e)}), 500

@direct_line_proxy_bp.route('/conversations/<conversation_id>/activities', methods=['POST'])
def send_activity(conversation_id):
    """发送活动到DirectLine服务"""
    try:
        logger.info(f"收到发送活动请求，会话ID: {conversation_id}")
        token = request.headers.get('Authorization', '')
        
        if not token or not token.startswith('Bearer '):
            logger.error("请求中缺少有效的Authorization令牌")
            return jsonify({'error': 'Authorization token required'}), 401
        
        # 准备转发活动
        activity = request.json
        if not activity:
            logger.error("请求中缺少活动数据")
            return jsonify({'error': 'Activity data required'}), 400
        
        # 确保用户ID格式正确
        if 'from' in activity and 'id' in activity['from'] and not activity['from']['id'].startswith('dl_'):
            activity['from']['id'] = f"dl_{activity['from']['id']}"
            logger.warning(f"已修正用户ID格式: {activity['from']['id']}")
        
        # 转发到DirectLine API
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{DIRECT_LINE_URL}/conversations/{conversation_id}/activities',
            headers=headers,
            json=activity,
            timeout=30
        )
        
        logger.debug(f"DirectLine API响应: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            result = response.json()
            logger.info(f"活动发送成功，ID: {result.get('id')}")
            return jsonify(result)
        else:
            error_msg = f"DirectLine API返回错误: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return jsonify({'error': error_msg}), response.status_code
            
    except Exception as e:
        error_msg = f"发送活动时发生异常: {str(e)}"
        logger.exception(error_msg)
        return jsonify({'error': error_msg}), 500

@direct_line_proxy_bp.route('/conversations/<conversation_id>/activities', methods=['GET'])
def get_activities(conversation_id):
    """获取活动"""
    try:
        secret = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not secret:
            logger.error("请求中缺少Authorization头部")
            return jsonify({'error': 'Authorization header with Bearer token is required'}), 401
        
        headers = {
            'Authorization': f'Bearer {secret}'
        }
        
        watermark = request.args.get('watermark', '')
        url = f'{DIRECT_LINE_URL}/conversations/{conversation_id}/activities'
        if watermark:
            url += f'?watermark={watermark}'
        
        logger.debug(f"获取活动，URL: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            activities = response.json()
            logger.info(f"成功获取活动: {activities}")
            return jsonify(activities), 200
        else:
            logger.error(f"获取活动失败: {response.status_code} - {response.text}")
            return jsonify({'error': f'Failed to get activities: {response.text}'}), response.status_code
    
    except Exception as e:
        logger.exception(f"获取活动时出错: {e}")
        return jsonify({'error': str(e)}), 500 