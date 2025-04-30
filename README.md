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

详见 `docs/setup.md` 