# NomadNavigator AI 安装与设置指南

本文档将指导您完成NomadNavigator AI项目的安装和设置过程，包括所需的Azure服务配置和本地开发环境设置。

## Azure服务配置

### 1. Azure OpenAI Service (GPT-4o)

**用途**: 自然语言理解、对话推理、规划生成

**设置步骤**:
1. 访问 [Azure Portal](https://portal.azure.com)
2. 搜索并选择 "Azure OpenAI"
3. 点击 "创建"
4. 选择订阅、资源组、区域和名称
5. 在创建后，部署GPT-4o模型
6. 记录API密钥和终结点URL

### 2. Azure AI Search

**用途**: 检索目的地数据（签证政策、生活费用、网络条件等）

**设置步骤**:
1. 在Azure Portal中搜索并选择 "Azure AI Search"
2. 点击 "创建"
3. 设置基本参数和定价层
4. 创建后，创建索引以存储目的地数据
5. 记录服务名称、管理密钥和查询密钥

### 3. Azure CosmosDB

**用途**: 存储用户画像、偏好、旅行历史

**设置步骤**:
1. 在Azure Portal中搜索并选择 "Azure Cosmos DB"
2. 点击 "创建"
3. 选择 "Core (SQL) API"
4. 设置资源组、账户名和位置
5. 创建后，创建数据库和容器
6. 记录连接字符串和密钥

### 4. Azure Bot Service

**用途**: 对话入口管理，支持Web / Mobile / Teams接入

**设置步骤**:
1. 在Azure Portal中搜索并选择 "Bot Services"
2. 点击 "创建"
3. 选择 "Azure Bot" 选项
4. 设置基本信息和应用ID
5. 配置消息终结点
6. 记录Microsoft App ID和密码

### 5. Azure Functions

**用途**: 处理多步骤自动化流程（如签证续签提醒）

**设置步骤**:
1. 在Azure Portal中搜索并选择 "Function App"
2. 点击 "创建"
3. 选择订阅、资源组并命名
4. 选择运行时堆栈为 Python 3.10
5. 选择区域和托管计划
6. 创建后，记录函数URL和密钥

### 6. Azure App Service

**用途**: 前端部署和API托管

**设置步骤**:
1. 在Azure Portal中搜索并选择 "App Services"
2. 点击 "创建"
3. 选择 "Web App"
4. 配置基本设置，选择Python 3.10运行时
5. 选择价格计划
6. 创建后，记录应用URL

## 配置文件设置

所有Azure服务的凭证和配置应存储在项目根目录下的 `.env` 文件中（请注意该文件不应提交到版本控制系统）。将以下模板复制到 `.env` 文件中，并填入您的实际值：

```
# Azure OpenAI
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_DEPLOYMENT=deployment_name

# Azure AI Search
AZURE_SEARCH_SERVICE=your_search_service_name
AZURE_SEARCH_KEY=your_search_key
AZURE_SEARCH_INDEX=your_search_index

# Azure CosmosDB
AZURE_COSMOS_ENDPOINT=your_cosmos_endpoint
AZURE_COSMOS_KEY=your_cosmos_key
AZURE_COSMOS_DATABASE=your_database_name
AZURE_COSMOS_CONTAINER=your_container_name

# Azure Bot Service
MICROSOFT_APP_ID=your_app_id
MICROSOFT_APP_PASSWORD=your_app_password

# Azure Functions
AZURE_FUNCTION_APP_NAME=your_function_app_name
AZURE_FUNCTION_KEY=your_function_key

# Azure App Service
AZURE_APP_SERVICE_NAME=your_app_service_name
```

## 本地开发环境设置

1. 确保已安装Python 3.10
2. 克隆项目仓库
3. 创建并激活虚拟环境：
   ```
   python -m venv venv
   source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
   ```
4. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
5. 在项目根目录创建 `.env` 文件并配置Azure服务凭证
6. 运行本地开发服务器：
   ```
   python app/app.py
   ```

## 测试验证

完成设置后，可以使用以下命令验证配置是否正确：

```
python app/utils/verify_azure_services.py
```

该脚本将验证所有Azure服务连接是否正常工作。 