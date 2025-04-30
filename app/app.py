#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NomadNavigator AI - 主应用入口
"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from app.bot.bot_app import create_adapter, BOT_APP
from app.utils.config import SETTINGS

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 创建Bot适配器
ADAPTER = create_adapter()

@app.route("/api/messages", methods=["POST"])
async def messages():
    """接收来自Bot Framework的消息处理"""
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return jsonify({"error": "不支持的媒体类型"}), 415

    # 使用适配器处理活动
    response = await ADAPTER.process_activity(body, "", BOT_APP.on_turn)
    if response:
        return jsonify(response.body), response.status
    return "", 200

@app.route("/api/health", methods=["GET"])
def health():
    """健康检查端点"""
    return jsonify({"status": "healthy", "version": "1.0.0"}), 200

@app.route("/", methods=["GET"])
def index():
    """主页"""
    return jsonify({
        "name": "NomadNavigator AI",
        "description": "一个基于Azure的智能生活规划代理，帮助数字游民设计旅行路径"
    }), 200

# 应用启动
if __name__ == "__main__":
    # 获取端口
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port) 