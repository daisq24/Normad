FROM python:3.10-slim

WORKDIR /app

# 复制依赖项文件
COPY requirements.txt .

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=3978

# 暴露端口
EXPOSE 3978

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:3978", "--timeout", "600", "app.app:app"] 