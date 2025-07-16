import threading
import logging
import time
from backend.script.fish import Fish
from backend.global_var import paras as Gva

logger = logging.getLogger(__name__)

class FishingApi:
    def __init__(self):
        self.window = None
        self.fish = None
        self.fish_thread = None
        self.is_fishing = False
    
    def set_window(self, window):
        self.window = window

    def toggle_fishing(self):
        """切换钓鱼状态"""
        if not self.is_fishing:
            return self.start_fishing()
        else:
            return self.stop_fishing()

    def start_fishing(self):
        """开始钓鱼"""
        if time.time() > Gva.over:
            return {"success": False, "message": "已超时"}
        if not Gva.emulator_info.get('state', False):
            return {"success": False, "message": "模拟器未连接"}
        if self.is_fishing:
            return {"success": False, "message": "已在钓鱼中"}
        
        try:
            self.fish = Fish()
            self.fish_thread = threading.Thread(target=self.fish.run)
            self.fish_thread.daemon = True
            self.fish_thread.start()
            self.is_fishing = True
            logger.info("开始钓鱼")
            return {"success": True, "message": "开始钓鱼", "is_fishing": self.is_fishing}
        except Exception as e:
            logger.error(f"启动钓鱼失败: {e}")
            return {"success": False, "message": f"启动钓鱼失败: {e}", "is_fishing": self.is_fishing}
    
    def stop_fishing(self):
        """停止钓鱼"""
        if not self.is_fishing:
            return {"success": False, "message": "钓鱼未在进行中"}
        
        try:
            if self.fish:
                self.fish.stop()
            if self.fish_thread and self.fish_thread.is_alive():
                self.fish_thread.join(timeout=2)
            self.is_fishing = False
            logger.info("停止钓鱼")
            return {"success": True, "message": "停止钓鱼", "is_fishing": self.is_fishing}
        except Exception as e:
            logger.error(f"停止钓鱼失败: {e}")
            return {"success": False, "message": f"停止钓鱼失败: {e}", "is_fishing": self.is_fishing}
    
    def get_fishing_status(self):
        """获取当前钓鱼状态"""
        return {"is_fishing": self.is_fishing}

    def get_fishing_settings(self):
        """获取钓鱼设置"""
        try:
            return {
                "success": True,
                "settings": Gva.fish_settings
            }
        except Exception as e:
            logger.error(f"获取钓鱼设置失败: {e}")
            return {
                "success": False,
                "message": f"获取钓鱼设置失败: {e}"
            }

    def update_fishing_setting(self, key, value):
        """更新单个钓鱼设置"""
        try:
            if key in Gva.fish_settings:
                Gva.fish_settings[key] = value
                logger.info(f"更新钓鱼设置 {key}: {value}")
                return {
                    "success": True,
                    "message": f"设置 {key} 已更新"
                }
            else:
                logger.warning(f"尝试更新未知钓鱼设置项: {key}")
                return {
                    "success": False,
                    "message": f"未知设置项: {key}"
                }
        except Exception as e:
            logger.error(f"更新钓鱼设置失败: {e}")
            return {
                "success": False,
                "message": f"更新钓鱼设置失败: {e}"
            }