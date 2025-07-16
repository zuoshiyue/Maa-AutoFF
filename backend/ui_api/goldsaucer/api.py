import threading
import logging
import time
from backend.script.goldsaucer import GoldSaucer
from backend.global_var import paras as Gva

logger = logging.getLogger(__name__)

class GoldSaucerApi:
    def __init__(self):
        self.window = None
        self.goldsaucer = None
        self.goldsaucer_thread = None
        self.is_running = False
    
    def set_window(self, window):
        self.window = window

    def toggle_mog_catch(self):
        """切换莫古抓球状态"""
        if not self.is_running:
            return self.start_mog_catch()
        else:
            return self.stop_mog_catch()

    def start_mog_catch(self):
        """开始莫古抓球"""
        if time.time() > Gva.over:
            return {"success": False, "message": "已超时"}
        if not Gva.emulator_info.get('state', False):
            return {"success": False, "message": "模拟器未连接"}
        if self.is_running:
            return {"success": False, "message": "任务已在运行中"}
        
        try:
            self.goldsaucer = GoldSaucer()
            self.goldsaucer_thread = threading.Thread(target=self.goldsaucer.run)
            self.goldsaucer_thread.daemon = True
            self.goldsaucer_thread.start()
            self.is_running = True
            logger.info("开始莫古抓球")
            return {"success": True, "message": "开始莫古抓球", "is_running": self.is_running}
        except Exception as e:
            logger.error(f"启动莫古抓球失败: {e}")
            return {"success": False, "message": f"启动莫古抓球失败: {e}", "is_running": self.is_running}
    
    def stop_mog_catch(self):
        """停止莫古抓球"""
        if not self.is_running:
            return {"success": False, "message": "任务未在进行中"}
        
        try:
            if self.goldsaucer:
                self.goldsaucer.stop()
            if self.goldsaucer_thread and self.goldsaucer_thread.is_alive():
                self.goldsaucer_thread.join(timeout=2)
            self.is_running = False
            logger.info("停止莫古抓球")
            return {"success": True, "message": "停止莫古抓球", "is_running": self.is_running}
        except Exception as e:
            logger.error(f"停止莫古抓球失败: {e}")
            return {"success": False, "message": f"停止莫古抓球失败: {e}", "is_running": self.is_running}
    
    def get_goldsaucer_status(self):
        """获取当前状态"""
        if self.goldsaucer:
            self.is_running = self.goldsaucer.running
        else:
            self.is_running = False
        return {"is_running": self.is_running} 