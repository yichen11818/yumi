import sqlite3
from typing import Optional, List, Dict, Any
from utils.logger import Logger

class DBService:
    def __init__(self, db_path: str = "data/bot.db"):
        self.db_path = db_path
        self.logger = Logger()
        self._init_db()
        
    def _init_db(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建用户表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    uid INTEGER PRIMARY KEY,
                    nickname TEXT,
                    last_active DATETIME,
                    chat_count INTEGER DEFAULT 0
                )
                """)
                
                # 创建群组表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    gid INTEGER PRIMARY KEY,
                    name TEXT,
                    join_time DATETIME
                )
                """)
                
                # 创建会话历史表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid INTEGER,
                    gid INTEGER,
                    message TEXT,
                    response TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            
    def add_chat_history(self, uid: int, gid: Optional[int], message: str, response: str):
        """添加聊天历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO chat_history (uid, gid, message, response) VALUES (?, ?, ?, ?)",
                    (uid, gid, message, response)
                )
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error adding chat history: {e}")
            
    def get_user_chat_count(self, uid: int) -> int:
        """获取用户聊天次数"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT chat_count FROM users WHERE uid = ?", (uid,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            self.logger.error(f"Error getting user chat count: {e}")
            return 0