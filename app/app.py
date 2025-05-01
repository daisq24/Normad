#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NomadNavigator AI - 主应用入口
"""

import os
import logging
import asyncio
import time
from flask import Flask, request, jsonify, send_from_directory, redirect, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置为DEBUG级别，显示更多信息
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 获取当前工作目录
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, 'static')
logger.debug(f"当前工作目录: {current_dir}")
logger.debug(f"静态文件目录: {static_folder}")
logger.debug(f"静态文件index.html是否存在: {os.path.exists(os.path.join(static_folder, 'index.html'))}")

# 创建Flask应用
app = Flask(__name__, static_folder=static_folder)

# 启用CORS
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/static/*": {"origins": "*"}
})

# 创建Bot适配器
from app.bot.bot_app import create_adapter, BOT_APP
from app.utils.config import SETTINGS
from app.api.direct_line_proxy import direct_line_proxy_bp
from app.utils.bot_helper import ensure_valid_activity, get_simple_activity, create_adapter_request

# 注册DirectLine代理Blueprint
app.register_blueprint(direct_line_proxy_bp, url_prefix='/api/directline')

ADAPTER = create_adapter()

# 处理异步运行
def run_async(coroutine):
    """运行异步协程的辅助函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

@app.route("/api/messages", methods=["POST"])
def messages():
    """接收来自Bot Framework的消息处理"""
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return jsonify({"error": "不支持的媒体类型"}), 415

    # 使用适配器处理活动
    try:
        auth_header = request.headers.get("Authorization", "")
        logger.info(f"收到消息: {body}")
        
        # 使用辅助函数确保活动格式正确
        try:
            # 标准化活动
            body = ensure_valid_activity(body)
            logger.info(f"标准化后的活动: {body}")
        except (TypeError, ValueError) as e:
            logger.error(f"活动验证失败: {e}")
            return jsonify({"error": str(e)}), 400
        
        # 运行异步处理 - 直接传递活动对象
        response = run_async(ADAPTER.process_activity(body, auth_header, BOT_APP.on_turn))
        
        logger.info(f"消息处理完成，响应: {response}")
        if response:
            return jsonify(response.body), response.status
        return "", 200
    except Exception as e:
        logger.exception(f"处理消息时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    """主页路由 - 返回静态页面或应用信息"""
    try:
        static_file_path = os.path.join(app.static_folder, 'index.html')
        logger.debug(f"尝试返回静态文件: {static_file_path}")
        logger.debug(f"文件是否存在: {os.path.exists(static_file_path)}")
        
        if os.path.exists(static_file_path):
            logger.info(f"返回静态文件: {static_file_path}")
            # 直接返回文件内容，而不是重定向
            with open(static_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.debug(f"文件内容前100个字符: {content[:100]}")
            return send_file(static_file_path)
        else:
            logger.warning(f"静态文件不存在: {static_file_path}")
            return jsonify({
                "name": "NomadNavigator AI",
                "description": "一个基于Azure的智能生活规划代理，帮助数字游民设计旅行路径"
            })
    except Exception as e:
        logger.exception(f"提供静态文件时出错: {e}")
        return jsonify({
            "name": "NomadNavigator AI",
            "description": "一个基于Azure的智能生活规划代理，帮助数字游民设计旅行路径",
            "error": str(e)
        })

@app.route('/static/<path:path>')
def serve_static(path):
    """静态文件服务"""
    logger.debug(f"请求静态文件: {path}")
    logger.debug(f"完整路径: {os.path.join(app.static_folder, path)}")
    logger.debug(f"文件是否存在: {os.path.exists(os.path.join(app.static_folder, path))}")
    return send_from_directory(app.static_folder, path)

@app.route("/api/health", methods=["GET"])
def health():
    """健康检查端点"""
    return jsonify({"status": "healthy", "version": "1.0.0"}), 200

@app.route("/api/diagnostic", methods=["GET"])
def diagnostic():
    """诊断端点，返回服务配置和状态"""
    try:
        bot_config = {
            "app_id": SETTINGS.MICROSOFT_APP_ID and SETTINGS.MICROSOFT_APP_ID[:5] + "..." or "未设置",
            "app_password": SETTINGS.MICROSOFT_APP_PASSWORD and "已设置" or "未设置",
            "openai_ready": bool(SETTINGS.AZURE_OPENAI_KEY and SETTINGS.AZURE_OPENAI_ENDPOINT),
            "search_ready": bool(SETTINGS.AZURE_SEARCH_SERVICE and SETTINGS.AZURE_SEARCH_KEY),
            "cosmos_ready": bool(SETTINGS.AZURE_COSMOS_KEY),
            "debug_mode": SETTINGS.DEBUG,
            "environment": os.environ.get("FLASK_ENV", "production"),
            "endpoints": {
                "messages": request.host_url + "api/messages",
                "directline_token": request.host_url + "api/directline/tokens/generate",
            }
        }
        return jsonify({
            "status": "healthy", 
            "version": "1.0.0",
            "config": bot_config
        }), 200
    except Exception as e:
        logger.exception("诊断端点错误")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/test-bot", methods=["POST"])
def test_bot():
    """测试Bot功能的简化端点"""
    try:
        # 获取请求数据
        if not request.json or "text" not in request.json:
            return jsonify({"error": "请求必须包含text字段"}), 400
            
        # 从请求中提取文本
        text = request.json.get("text")
        user_id = request.json.get("user_id", f"dl_{int(time.time())}")
        
        # 创建简单的活动对象
        activity = get_simple_activity(text, user_id)
        logger.info(f"测试Bot端点创建的活动: {activity}")
        
        # 处理活动 - 直接传递活动对象
        response = run_async(ADAPTER.process_activity(activity, "", BOT_APP.on_turn))
        
        # 返回结果
        if response:
            result = {
                "success": True,
                "response": response.body
            }
            logger.info(f"测试Bot响应: {result}")
            return jsonify(result), 200
        else:
            # 没有直接响应，查询最新一条消息
            return jsonify({
                "success": True, 
                "response": {
                    "text": "处理完成，但没有直接响应。这是正常的，因为响应可能通过DirectLine通道发送。"
                }
            }), 200
            
    except Exception as e:
        logger.exception(f"测试Bot端点出错: {e}")
        return jsonify({"error": str(e)}), 500

# 添加跨域预检请求支持
@app.after_request
def after_request(response):
    """添加CORS头部到所有响应"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    # 获取端口
    port = int(os.environ.get("PORT", 3978))
    logger.info(f"启动应用，监听端口: {port}")
    app.run(host="0.0.0.0", port=port, debug=True) 