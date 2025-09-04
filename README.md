# Prompt Manager System

一个基于 **FastAPI + PostgreSQL + SQLAlchemy + Alembic** 的提示词管理系统（Prompt Manager System）。  
支持用户注册/登录、提示词的创建与管理、MCP 工具接口扩展。  

---

## 🚀 功能概览

- **用户管理**：注册、登录、鉴权 `/api/v1/users`
- **提示词管理**：创建、查询、后续支持更新/删除 `/api/v1/prompts`
- **标签系统**：多对多标签关联，支持搜索与分类
- **版本控制**：`PromptVersion` 支持提示词版本追踪
- **认证机制**：JWT + API Key 双重认证
- **MCP 服务**：预留工具接口（如 `list_available_prompts`、`get_prompt_content`）

---

## 📂 项目结构

```bash
projects/prompt-manager-system/
└─ backend/
├─ .env - 运行环境配置（生产/本地变量）
├─ .env.test - 测试环境配置（可选）
├─ requirements.txt - Python 依赖列表
├─ .gitignore - Git 忽略规则
│
├─ alembic/
│ ├─ versions/ - 数据库迁移脚本目录
│ └─ env.py - Alembic 环境配置
├─ alembic.ini - Alembic 主配置文件
│
└─ app/
├─ main.py - FastAPI 应用入口
│
├─ core/
│ ├─ config.py - 配置中心（读取环境变量）
│ └─ security.py - 安全逻辑（JWT、API Key）
│
├─ db/
│ └─ session.py - 数据库会话工厂
│
├─ api/
│ ├─ routes.py - 路由注册
│ └─ v1/
│ ├─ users.py - 用户接口
│ ├─ prompts.py - 提示词接口
│ ├─ mcp.py - MCP 接口（预留）
│ └─ deps.py - 依赖注入
│
├─ models/
│ ├─ user.py - 用户模型
│ ├─ prompt.py - 提示词 & 版本模型
│ └─ tag.py - 标签模型
│
├─ schemas/
│ ├─ user.py - 用户 Schema
│ └─ prompt.py - 提示词 Schema
│
└─ services/
├─ user_service.py - 用户服务
└─ prompt_service.py - 提示词服务
```

---

## ⚙️ 环境配置

### 1. 安装依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 .env

包含一个example.env的环境文件，直接在 backend/.env 文件中配置：

### 3. 数据库迁移

```bash
alembic revision --autogenerate -m "init tables"
alembic upgrade head
```

### 4. 启动项目

```bash
PYTHONPATH=./backend uvicorn app.main:app --reload --port 8000
```
服务启动后，访问：
API 文档 (Swagger): http://localhost:8000/docs
健康检查: http://localhost:8000/health



### 🧪 示例请求

#### 1. 注册用户
```bash
curl -sS -X POST http://localhost:8000/api/v1/users/register \
  -H 'Content-Type: application/json' \
  --data '{"username":"test","email":"test@example.com"}'
```
<img width="1381" height="106" alt="edca3482cc9be9ff4b2009b731ecfd0" src="https://github.com/user-attachments/assets/787956d8-6f0e-4c16-bea4-cc737f47b03a" />
// 自动生成随机ID储存user name


#### 2. 用户登录（使用邮箱）
```bash
curl -i -sS -X POST http://localhost:8000/api/v1/users/login \
  -H 'Content-Type: application/json' \
  --data '{"email":"test@example.com"}'
```
<img width="1376" height="366" alt="image" src="https://github.com/user-attachments/assets/561951fc-84fd-4076-917a-bd9b0456bc91" />
// 自动生成access token


#### 3. 检查API Key和Token的设置

根据.env文件中的API_KEY的全局变量方便测试（可自行修改）：
```bash
export API_KEY=“your_test_key”
```

登录返回 {"access_token":"XXX","token_type":"bearer"}存到环境变量：
```bash
export TOKEN="XXX"
```


#### 3. 创建提示词（需要api key和token）

```bash
curl -sS -X POST http://localhost:8000/api/v1/prompts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "title": "测试用",
    "content": "请以{{theme}}为主题创作",
    "tags": ["中药"],
    "category": "医学",
    "variables": ["theme"]
  }'
```
<img width="1445" height="264" alt="image" src="https://github.com/user-attachments/assets/17df12a0-205e-4ab3-bdeb-bc7cbd2933aa" />



### 检查postgreSQL数据库

<img width="1880" height="789" alt="1756998842969" src="https://github.com/user-attachments/assets/7fa30211-bf0b-4b34-8ee7-f0a2cb7c9ffe" />

连接成功已储存

//测试与开发阶段使用本地postgreSQL进行调试，可在.env环境设置文件中进行修改。

