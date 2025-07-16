"""
日志API模块，提供给前端显示日志的接口
"""
import logging
import time
from collections import deque

# 配置日志
logger = logging.getLogger(__name__)

class LogsAPI:
    """
    日志API类，提供给前端显示日志的接口
    """
    def __init__(self):
        """初始化日志API"""
        self.window = None
        # 使用双端队列存储日志，限制最大数量
        self.log_queue = deque(maxlen=500)
        # 日志级别映射
        self.log_levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        # 标记是否正在处理日志，防止无限循环
        self._processing_log = False
    
    def set_window(self, window):
        """设置窗口引用"""
        self.window = window
    
    def log(self, message, level="INFO"):
        """
        记录日志并发送到前端
        
        参数:
            message: 日志消息
            level: 日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        # 防止无限循环
        if self._processing_log:
            return False
            
        try:
            self._processing_log = True
            
            # 验证日志级别
            if level not in self.log_levels:
                level = "INFO"
            
            # 创建日志记录
            log_entry = {
                "timestamp": time.time(),
                "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": message,
                "level": level
            }
            
            # 添加到日志队列
            self.log_queue.append(log_entry)
            
            # 如果窗口已设置，发送到前端
            if self.window:
                self.window.evaluate_js(f"window.dispatchEvent(new CustomEvent('log-message', {{ detail: {self._to_js_object(log_entry)} }}))")
                
            return True
        except Exception as e:
            # 使用原始Python日志记录错误，避免无限循环
            print(f"发送日志到前端失败: {e}")
            return False
        finally:
            self._processing_log = False
    
    def debug(self, message):
        """发送DEBUG级别日志"""
        return self.log(message, "DEBUG")
    
    def info(self, message):
        """发送INFO级别日志"""
        return self.log(message, "INFO")
    
    def warning(self, message):
        """发送WARNING级别日志"""
        return self.log(message, "WARNING")
    
    def error(self, message):
        """发送ERROR级别日志"""
        return self.log(message, "ERROR")
    
    def critical(self, message):
        """发送CRITICAL级别日志"""
        return self.log(message, "CRITICAL")
    
    def get_logs(self, count=100, level=None):
        """
        获取最近的日志
        
        参数:
            count: 返回的日志数量，默认100条
            level: 过滤的日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        try:
            logs = list(self.log_queue)
            
            # 如果指定了日志级别，进行过滤
            if level and level in self.log_levels:
                level_value = self.log_levels[level]
                logs = [log for log in logs if self.log_levels.get(log["level"], 0) >= level_value]
            
            # 返回最近的n条日志
            return {
                "success": True,
                "data": logs[-count:] if count < len(logs) else logs
            }
        except Exception as e:
            print(f"获取日志失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_logs(self):
        """清空日志队列"""
        try:
            self.log_queue.clear()
            print("日志队列已清空")
            return {
                "success": True,
                "message": "日志已清空"
            }
        except Exception as e:
            print(f"清空日志失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _to_js_object(self, obj):
        """将Python对象转换为JavaScript对象字符串"""
        import json
        return json.dumps(obj, ensure_ascii=False)
    
    def setup_logging_redirect(self, min_level="INFO"):
        """
        设置日志重定向，将Python标准日志重定向到前端
        
        参数:
            min_level: 最小日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        class LogHandler(logging.Handler):
            def __init__(self, logs_api):
                super().__init__()
                self.logs_api = logs_api
                
            def emit(self, record):
                # 避免处理来自logs_api模块的日志，防止无限循环
                if record.name == __name__:
                    return
                    
                try:
                    # 获取日志级别名称
                    level_name = record.levelname
                    # 获取日志消息
                    message = self.format(record)
                    # 发送到前端
                    self.logs_api.log(message, level_name)
                except Exception:
                    pass
        
        try:
            # 创建日志处理器
            handler = LogHandler(self)
            
            # 设置日志格式
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            
            # 设置最小日志级别
            if min_level in self.log_levels:
                handler.setLevel(self.log_levels[min_level])
            else:
                handler.setLevel(logging.INFO)
            
            # 获取根日志记录器
            root_logger = logging.getLogger()
            
            # 添加处理器
            root_logger.addHandler(handler)
            
            print(f"日志重定向已设置，最小级别: {min_level}")
            return True
        except Exception as e:
            print(f"设置日志重定向失败: {e}")
            return False

# 创建全局日志API实例
# logs_api = LogsAPI() 