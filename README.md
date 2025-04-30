# NomadNavigator AI

一个基于Azure的智能生活规划代理，帮助数字游民设计旅行路径、管理签证要求并优化全球生活决策。

## 项目简介

NomadNavigator AI是基于Azure AI服务构建的代理系统。它根据实时数据为数字游民提供个性化旅行计划、签证管理和目的地优化。利用GPT-4o推理、Azure AI Search索引和Azure CosmosDB中的动态记忆，它可以自主规划多国行程，同时保持签证和税法合规。

通过自然对话，用户可以获得考虑其预算、签证资格、生活方式偏好和工作限制的定制建议——帮助他们在世界任何地方生活、工作和茁壮成长。

## 系统架构

```
[用户输入]
   ↓
Azure Bot Service（聊天界面）
   ↓
Azure OpenAI (GPT-4o)
  ├── 意图识别 (旅行/签证/预算)
  ├── 自然语言推理与多轮对话
  ↓
Azure AI Search
  ├── 查询实时签证政策数据库
  ├── 查询城市生活数据（预算/安全/网络）
  ↓
Azure Functions
  ├── 多步骤流程编排（如旅行计划➔签证时间线➔提醒）
  ↓
Azure CosmosDB
  ├── 存储用户兴趣、旅行历史、预算偏好
  ├── 个性化推荐学习
  ↓
返回到用户：完整推荐（城市列表+签证安排+预算建议+行动提醒）
```

## 技术栈

- **语言**: Python 3.10
- **框架**: Flask, FastAPI, Bot Framework SDK v4, Azure SDK for Python
- **Azure服务**: OpenAI Service (GPT-4o), AI Search, CosmosDB, Bot Service, Functions, App Service
- **数据库**: Azure CosmosDB (JSON文档存储)

## 安装与设置

### 本地开发环境

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/NomadNavigator.git
   cd NomadNavigator
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate  # Windows
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量
   ```bash
   cp ENV.example .env
   # 编辑.env文件，填入您的Azure服务凭据
   ```

5. 运行应用
   ```bash
   python -m app.app
   ```

应用将在 http://localhost:3978 上运行。

### 使用Docker运行

需要先安装Docker。

```bash
docker build -t nomad-navigator .
docker run -p 3978:3978 --env-file .env nomad-navigator
```

## 部署到Azure

### 使用GitHub Actions自动部署

1. 在GitHub仓库中设置以下Secrets：
   - `AZURE_APP_NAME`: Azure App Service的名称
   - `AZURE_WEBAPP_PUBLISH_PROFILE`: 从Azure门户下载的发布配置文件内容

2. 推送代码到main分支，GitHub Actions将自动部署到Azure App Service。

### 手动部署到Azure App Service

1. 在Azure门户创建App Service
2. 配置App Service的部署中心，连接到GitHub仓库
3. 在App Service的配置中添加所有环境变量
4. 启动部署

## 验证部署

部署完成后，可以使用以下命令验证服务是否正常运行：

```bash
pip install colorama
python deploy_test.py --url https://your-app-name.azurewebsites.net
```

## 许可

MIT License 