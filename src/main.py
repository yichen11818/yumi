import sys
import os

# 设置环境编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, request, jsonify
from handlers.message_handler import MessageHandler
from handlers.notice_handler import NoticeHandler
from handlers.request_handler import RequestHandler
from services.scheduler_service import SchedulerService
from utils.config import Config
from utils.logger import Logger

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    config = Config()
    logger = Logger()
    
    # 初始化服务和处理器
    message_handler = MessageHandler()
    notice_handler = NoticeHandler()
    request_handler = RequestHandler()
    scheduler_service = SchedulerService()
    
    # 启动调度器
    scheduler_service.start()
    
    @app.route("/", methods=["GET"])
    def index():
        """健康检查接口"""
        return "QQ Bot Service is running!"
    
    @app.route("/", methods=["POST"])
    def handle_post():
        """处理go-cqhttp的事件上报"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "No data received"})
                
            post_type = data.get("post_type")
            
            # 根据post_type分发到不同的处理器
            if post_type == "message":
                message_handler.handle_message(data)
            elif post_type == "notice":
                notice_handler.handle_notice(data)
            elif post_type == "request":
                request_handler.handle_request(data)
            elif post_type == "meta_event":  # 心跳包等元事件
                logger.debug(f"Received meta event: {data}")
            else:
                logger.warning(f"Unknown post type: {post_type}")
                
            return jsonify({"status": "ok"})
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return jsonify({"status": "error", "message": str(e)})
            
    return app, config, logger

def main():
    """应用程序入口点"""
    logger = Logger()
    try:
        app, config, _ = create_app()
        logger.info("正在启动 QQ Bot 服务...")
        app.run(
            host=config.qq_bot.get('host'),
            port=config.qq_bot.get('port')
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"QQ Bot 服务启动失败: {error_msg}")

if __name__ == "__main__":
    main()