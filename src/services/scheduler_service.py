from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.news_service import NewsService
from services.monitor_service import MonitorService
from services.verification_service import VerificationService
from utils.config import Config
from utils.logger import Logger
import atexit

class SchedulerService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = Config()
            self.logger = Logger()
            self.news_service = NewsService()
            self.monitor_service = MonitorService()
            self.verification_service = VerificationService()
            self.scheduler = BackgroundScheduler(
                timezone='Asia/Shanghai',  # 设置时区
                job_defaults={
                    'coalesce': True,  # 错过的任务只运行一次
                    'max_instances': 1  # 同一个任务同时只能有一个实例
                }
            )
            self.initialized = True
            
            # 注册退出时的清理函数
            atexit.register(self.stop)
        
    def start(self):
        """启动所有定时任务"""
        try:
            if self.scheduler.running:
                self.logger.warning("Scheduler is already running")
                return
                
            # 每小时检查新闻
            self.scheduler.add_job(
                self.news_service.get_cs2_news,
                CronTrigger(hour='*/1'),
                id='cs2_news',
                replace_existing=True  # 如果任务已存在则替换
            )
            
            self.scheduler.add_job(
                self.news_service.get_gpt_news,
                CronTrigger(hour='*/1'),
                id='gpt_news',
                replace_existing=True
            )
            
            # 每5分钟监控系统状态
            self.scheduler.add_job(
                self._monitor_system,  # 使用包装函数
                CronTrigger(minute='*/5'),
                id='system_monitor',
                replace_existing=True
            )
            
            # 每分钟检查验证超时
            self.scheduler.add_job(
                self._check_verification_timeout,
                'interval',
                seconds=60
            )
            
            self.scheduler.start()
            self.logger.info("Scheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
            raise
            
    def stop(self):
        """停止所有定时任务"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.logger.info("Scheduler stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
            
    def _monitor_system(self):
        """系统监控包装函数"""
        try:
            info = self.monitor_service.get_system_info()
            if info:
                # 可以添加阈值检查
                if info['cpu']['percent'] > 80:
                    self.logger.warning(f"High CPU usage: {info['cpu']['percent']}%")
                if info['memory']['percent'] > 80:
                    self.logger.warning(f"High memory usage: {info['memory']['percent']}%")
        except Exception as e:
            self.logger.error(f"Error in system monitoring: {e}")
            
    def _check_verification_timeout(self):
        """检查验证超时"""
        timeout_users = self.verification_service.check_timeout()
        for group_id, user_id in timeout_users:
            self.qq_service.set_group_kick(group_id, user_id, "验证超时")
            message = [
                self.qq_service.text(f"用户 {user_id} 验证超时,已被移出群聊")
            ]
            self.qq_service.send_message(group_id, message)