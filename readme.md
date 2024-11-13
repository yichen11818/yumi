# YuMi QQ Bot

YuMi 是一个基于 Flask 的 QQ 机器人服务端框架,提供了丰富的功能和良好的扩展性。

## 主要功能

- 消息处理与回复
- 群组管理
- 好友请求处理 
- 新闻资讯推送
- ChatGPT 对话
- 百度翻译集成
- 音乐搜索与分享
- 图片生成
- 验证码验证
- 定时任务调度

## 技术架构

- 后端框架: Flask
- 数据库: SQLite
- 第三方服务:
  - OpenAI API (ChatGPT)
  - 百度翻译 API
  - Google Search API
  - Replicate API

## 项目结构

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


## 快速开始

1. 安装依赖:
bash
pip install -r requirements.txt

2. 配置文件:
- 复制 `config/config.yaml.example` 为 `config/config.yaml`
- 填写必要的配置项:
  - QQ 机器人配置
  - OpenAI API 密钥
  - 百度翻译 API 密钥
  - 其他第三方服务配置

3. 启动服务:
bash
python src/main.py


## 配置说明

主要配置项包括:

- qq_bot: QQ 机器人相关配置
- openai: OpenAI API 配置
- chatgpt: ChatGPT 模型配置
- baidu: 百度翻译 API 配置
- news: 新闻推送群组配置
- database: 数据库配置

详细配置说明请参考 `config/config.yaml.example`

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