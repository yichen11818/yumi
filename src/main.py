import sys
import os
import locale
from quart import Quart, request, jsonify
import asyncio
import time

# 设置环境编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

from handlers.message_handler import MessageHandler
from handlers.notice_handler import NoticeHandler
from handlers.request_handler import RequestHandler
from services.scheduler_service import SchedulerService
from utils.config import Config
from utils.logger import Logger
from services.qq_service import QQService

# 初始化
config = Config()
logger = Logger()
app = Quart(__name__)
message_handler = MessageHandler()
notice_handler = NoticeHandler()
request_handler = RequestHandler()
scheduler = SchedulerService()

async def init_bot():
    """初始化机器人信息"""
    try:
        qq_service = QQService()
        # 获取登录信息
        login_info = qq_service.get_login_info()
        if not login_info:
            logger.error("获取登录信息失败")
            return False
            
        # 获取用户信息
        user_info = qq_service.get_user_info(int(login_info['user_id']))
        if not user_info:
            logger.error("获取用户信息失败")
            return False
            
        # 更新配置文件
        config = Config()
        config.update_bot_info(
            str(login_info['user_id']),
            user_info['nickname']
        )
        
        logger.info(f"机器人信息已更新: {login_info['user_id']} - {user_info['nickname']}")
        return True
        
    except Exception as e:
        logger.error(f"初始化机器人信息失败: {e}")
        return False

@app.route('/', methods=['POST'])
async def handle_post():
    try:
        start_time = time.time()
        data = await request.get_json()
        post_type = data.get('post_type')
        
        # 详细的日志记录
        if post_type == 'message':
            message_type = data.get('message_type')
            sender = data.get('sender', {})
            message = data.get('message', [])
            
            logger.info(
                f"\n收到{message_type}消息:"
                f"\n- 发送者: {sender.get('nickname')}({sender.get('user_id')})"
                f"\n- 内容: {message}"
            )
            
        elif post_type == 'notice':
            notice_type = data.get('notice_type')
            logger.info(f"\n收到通知: {notice_type}\n- 详情: {data}")
            
        elif post_type == 'request':
            request_type = data.get('request_type')
            logger.info(f"\n收到请求: {request_type}\n- 详情: {data}")

        if post_type == 'message':
            await message_handler.handle(data)
        elif post_type == 'notice':
            await notice_handler.handle(data)
        elif post_type == 'request':
            await request_handler.handle(data)
            
        process_time = (time.time() - start_time) * 1000
        logger.info(f"请求处理完成，耗时: {process_time:.2f}ms\n{'-'*50}")
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"请求处理失败: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # 初始化机器人信息
    if not asyncio.run(init_bot()):
        logger.error("机器人初始化失败,服务启动失败")
        exit(1)
    
    # 启动调度器
    scheduler.start()
    
    # 启动服务器
    logger.info("正在启动 QQ Bot 服务...")
    app.run(
        host=config.qq_bot['host'],
        port=config.qq_bot['port']
    )