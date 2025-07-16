import threading
import logging
import time
from backend.script.gather import Gather
from backend.data.gather_info import gather_info  # 导入采集物品信息
from backend.global_var import paras as Gva  # 导入全局变量

logger = logging.getLogger(__name__)

class GatheringApi:
    def __init__(self):
        self.window = None
        self.gather = Gather()
        self.gather_thread = None
        self.is_gathering = False
    
    def set_window(self, window):
        self.window = window
    
    def toggle_gathering(self):
        """切换采集状态：开始或停止采集"""
        if not self.is_gathering:
            return self.start_gathering()
        else:
            return self.stop_gathering()
    
    def start_gathering(self):
        """开始采集"""
        if time.time() > Gva.over:
            return
        if Gva.emulator_info['state'] == False:
            return {"error": True, "message": "模拟器未连接"}
        if self.is_gathering:
            return {"success": False, "message": "采集已在进行中"}
        
        try:
            self.gather = Gather()
            self.gather_thread = threading.Thread(target=self.gather.run)
            self.gather_thread.daemon = True
            self.gather_thread.start()
            self.is_gathering = True
            logger.info("采集已开始")
            return {"success": True, "message": "采集已开始", "is_gathering": True}
        except Exception as e:
            logger.error(f"启动采集失败: {e}")
            return {"success": False, "message": f"启动采集失败: {e}", "is_gathering": False}
    
    def stop_gathering(self):
        """停止采集"""
        if not self.is_gathering:
            return {"success": False, "message": "采集未在进行中"}
        
        try:
            # 使用Gather类的stop方法停止采集
            self.gather.stop()
            if self.gather_thread and self.gather_thread.is_alive():
                self.gather_thread.join(timeout=2)
            self.is_gathering = False
            logger.info("采集已停止")
            return {"success": True, "message": "采集已停止", "is_gathering": False}
        except Exception as e:
            logger.error(f"停止采集失败: {e}")
            return {"success": False, "message": f"停止采集失败: {e}", "is_gathering": True}
    
    def get_gathering_status(self):
        """获取当前采集状态"""
        return {
            "is_gathering": self.is_gathering
        }
        
    def get_gathering_items(self):
        """获取可采集物品列表"""
        try:
            # 将字典转换为前端需要的格式
            items = []
            for item_name, item_info in gather_info.items():
                items.append({
                    "value": item_name,  # 使用物品名称作为唯一值
                    "label": item_name,  # 显示名称
                    "job": item_info["job"],  # 职业
                    "level": item_info["level"]  # 等级
                })
            
            # 按等级排序
            items.sort(key=lambda x: x["level"])
            
            return {"success": True, "items": items}
        except Exception as e:
            logger.error(f"获取采集物品列表失败: {e}")
            return {"success": False, "message": f"获取采集物品列表失败: {e}"}

    def get_gathering_progress(self):
        """获取采集进度数据"""
        try:
            # 为每个采集项添加额外信息
            items_with_info = {}
            current_time = time.time()
            
            for item_name, item_data in Gva.gathering_items.items():
                # 复制基本数据
                item_info = dict(item_data)
                
                # 添加默认值，确保所有必要字段都存在
                if "need" not in item_info:
                    item_info["need"] = 0
                if "complete" not in item_info:
                    item_info["complete"] = 0
                if "num_per_min" not in item_info:
                    item_info["num_per_min"] = 0
                
                # 添加开始和结束时间（如果存在）
                if "start_time" not in item_info and item_info.get("complete", 0) > 0:
                    # 如果已经开始采集但没有记录开始时间，设置一个估计值
                    item_info["start_time"] = current_time - 60  # 假设一分钟前开始
                
                if "end_time" not in item_info and item_info.get("complete", 0) >= item_info.get("need", 0) > 0:
                    # 如果已经完成但没有记录结束时间，设置为当前时间
                    item_info["end_time"] = current_time
                
                # 添加来自gather_info的信息
                if item_name in gather_info:
                    item_info["job"] = gather_info[item_name].get("job", "")
                    item_info["level"] = gather_info[item_name].get("level", 0)
                
                items_with_info[item_name] = item_info
            
            return {"success": True, "items": items_with_info}
        except Exception as e:
            logger.error(f"获取采集进度失败: {e}")
            return {"success": False, "message": f"获取采集进度失败: {e}"}

    def update_gathering_items(self, items):
        """更新采集物品列表"""
        try:
            # 清空旧数据并更新为新数据
            Gva.gathering_items.clear()
            Gva.gathering_items.update(items)
            
            logger.info(f"采集列表已更新: {Gva.gathering_items}")
            return {"success": True, "message": "采集列表更新成功"}
        except Exception as e:
            logger.error(f"更新采集列表失败: {e}")
            return {"success": False, "message": f"更新采集列表失败: {e}"}

# 创建API实例
# gathering_api = GatheringApi() 