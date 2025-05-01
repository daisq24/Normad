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
        
        headers = {
            'Authorization': f'Bearer {secret}'
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
        
        response = requests.post(
            f'{DIRECT_LINE_URL}/tokens/generate',
            headers=headers,
            json=params
        )
        
        logger.debug(f"DirectLine API响应: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info("成功获取令牌")
            return jsonify(token_data), 200
        else:
            error_text = response.text
            logger.error(f"生成令牌失败: {response.status_code} - {error_text}")
            return jsonify({'error': f'Failed to generate token: {error_text}'}), response.status_code
    
    except Exception as e:
        logger.exception(f"生成令牌时出错: {e}")
        return jsonify({'error': str(e)}), 500

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
    """发送活动"""
    try:
        secret = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not secret:
            logger.error("请求中缺少Authorization头部")
            return jsonify({'error': 'Authorization header with Bearer token is required'}), 401
        
        headers = {
            'Authorization': f'Bearer {secret}',
            'Content-Type': 'application/json'
        }
        
        data = request.json
        logger.info(f"发送活动到会话 {conversation_id}: {data}")
        
        response = requests.post(
            f'{DIRECT_LINE_URL}/conversations/{conversation_id}/activities',
            headers=headers,
            json=data
        )
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"成功发送活动")
            return jsonify(response.json()), response.status_code
        else:
            logger.error(f"发送活动失败: {response.status_code} - {response.text}")
            return jsonify({'error': f'Failed to send activity: {response.text}'}), response.status_code
    
    except Exception as e:
        logger.exception(f"发送活动时出错: {e}")
        return jsonify({'error': str(e)}), 500

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