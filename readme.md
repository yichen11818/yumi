# YuMi QQ Bot

YuMi 是一个基于 Quart 的 QQ 机器人服务端框架，提供了丰富的功能和良好的扩展性。

## 主要功能

- 消息处理与回复
  - 群聊和私聊消息处理
  - @消息自动回复
  - ChatGPT 智能对话
  - 多 API 端点支持
  
- 群组管理
  - 群成员管理
  - 群消息撤回
  - 群公告发布
  
- 好友请求处理
  - 自动通过好友请求
  - 验证消息处理
  
- 新闻资讯推送
  - CS2 游戏更新推送
  - ChatGPT 更新日志推送
  - 自动翻译推送内容
  
- AI 功能集成
  - ChatGPT 对话
  - 多 API 端点负载均衡
  - 错误重试和故障转移
  
- 多语言支持
  - 百度翻译集成
  - 自动翻译外文内容

## 技术架构

- 后端框架: Quart (异步 Web 框架)
- 数据库: SQLite
- 第三方服务:
  - OpenAI API (ChatGPT)
  - 百度翻译 API
  - Google Search API
  - Replicate API

## 配置说明

主要配置项包括:

### QQ 机器人配置
```
qq_bot:
  cqhttp_url: "http://127.0.0.1:8600" # cqhttp地址
  bot_uid: "你的机器人QQ号" # 机器人QQ号
  admin_qq: "管理员QQ号" # 管理员QQ号
  host: "127.0.0.1" # 服务器地址
  port: 5555 # 服务器端口
  max_length: 4500 # 消息最大长度
  auto_confirm: false # 是否自动确认好友请求
  bot_name: "yumi" # 机器人昵称


openai:
  endpoints:
    - url: "https://api.openai.com/v1"  # 官方API
      api_key: "你的官方OpenAI API Key"
      priority: 1
    - url: "https://your-proxy1.com/v1"  # 代理1
      api_key: "代理1的API Key"
      priority: 2
    - url: "https://your-proxy2.com/v1"  # 代理2
      api_key: "代理2的API Key"
      priority: 3
  img_size: "1024x1024"

chatgpt:
  model: "gpt-3.5-turbo-0613" # 模型
  max_tokens: 4000
  preset: "你是一个智能助手..." # 预设
  functions_enabled: true # 是否启用函数

baidu:
  appid: "你的百度翻译APPID" # 百度翻译APPID
  secret_key: "你的百度翻译密钥" # 百度翻译密钥

replicate:
  api_token: "你的Replicate API Token" # Replicate API Token

electricity:
  api_url: "电费查询API地址" # 电费查询API地址
  api_key: "电费查询API密钥" # 电费查询API密钥

news:
  gid:
    cs2: "CS2新闻推送群号,多个群用逗号分隔" # CS2新闻推送群号,多个群用逗号分隔
    gpt: "GPT新闻推送群号,多个群用逗号分隔" # GPT新闻推送群号,多个群用逗号分隔

database:
  path: "data/bot.db" # 数据库路径

google:
  api_key: "你的Google API密钥" # Google API密钥
  cx_id: "你的自定义搜索引擎ID" # 自定义搜索引擎ID
  serper_api_key: "your Serper API密钥" # Serper API密钥
```
## 项目结构
```
src/
├── main.py # 应用入口
├── handlers/ # 事件处理器
│ ├── message_handler.py
│ ├── notice_handler.py
│ └── request_handler.py
├── services/ # 业务服务层
│ ├── qq_service.py
│ ├── chat_service.py
│ ├── news_service.py
│ └── ...
└── utils/ # 工具类
├── config.py
└── logger.py
```

## 快速开始

1. 安装依赖:
```
bash
pip install -r requirements.txt
```
2. 配置文件:
- 复制 `config/config.yaml.example` 为 `config/config.yaml`
- 填写必要的配置项:
  - QQ 机器人配置
  - OpenAI API 密钥
  - 百度翻译 API 密钥
  - 其他第三方服务配置

3. 启动服务:
bash
```
python src/main.py

```
## 功能扩展

1. 添加新的消息处理器:
- 在 handlers/ 目录下创建新的处理器类
- 在 main.py 中注册处理器

2. 添加新的服务:
- 在 services/ 目录下创建新的服务类
- 在需要使用的地方注入服务

## 开发规范

- 使用 Python 类型注解
- 异常需要合理处理和日志记录
- 配置项变更需要同步更新示例配置文件

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- 问题反馈: 创建 Issue
- 功能建议: 创建 Issue 或 Pull Request