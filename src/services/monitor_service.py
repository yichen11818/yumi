import psutil
import time
from typing import Dict, Any
from utils.config import Config
from utils.logger import Logger

class MonitorService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'percent': disk.percent
                },
                'network': self._get_network_info(),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
            
    def _get_network_info(self) -> Dict[str, float]:
        """获取网络信息"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            return {}
            
    def check_system_health(self):
        """检查系统健康状态并发送告警"""
        system_info = self.get_system_info()
        if system_info['cpu']['percent'] > 90:
            self.alert_high_cpu_usage()