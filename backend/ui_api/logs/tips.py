"""
提示信息API模块，提供给前端显示提示信息的接口
"""
import logging
import json

# 配置日志
logger = logging.getLogger(__name__)

class TipsAPI:
    """
    提示信息API类，提供给前端显示提示信息的接口
    """
    def __init__(self):
        """初始化提示信息API"""
        self.window = None
    
    def set_window(self, window):
        """设置窗口引用"""
        self.window = window
    
    def show_tip(self, message, type="info", duration=3000, position="top-right"):
        """
        显示提示信息
        
        参数:
            message: 提示消息
            type: 提示类型，可选值：info, success, warning, error
            duration: 显示时长，单位毫秒，默认3000毫秒
            position: 显示位置，可选值：top-right, top-left, top-center, bottom-right, bottom-left, bottom-center
        """
        try:
            # 验证提示类型
            valid_types = ["info", "success", "warning", "error"]
            if type not in valid_types:
                type = "info"
            
            # 验证显示位置
            valid_positions = ["top-right", "top-left", "top-center", "bottom-right", "bottom-left", "bottom-center"]
            if position not in valid_positions:
                position = "top-right"
            
            # 创建提示信息
            tip = {
                "message": message,
                "type": type,
                "duration": duration,
                "position": position
            }
            
            # 记录到系统日志
            # logger.info(f"显示提示信息: {message} (类型: {type})")
            
            # 如果窗口已设置，发送到前端
            if self.window:
                self.window.evaluate_js(f"window.dispatchEvent(new CustomEvent('show-tip', {{ detail: {json.dumps(tip, ensure_ascii=False)} }}))")
                return True
            return False
        except Exception as e:
            logger.error(f"发送提示信息到前端失败: {e}")
            return False
    
    def info(self, message, duration=3000, position="top-right"):
        """显示信息提示"""
        return self.show_tip(message, "info", duration, position)
    
    def success(self, message, duration=3000, position="top-right"):
        """显示成功提示"""
        return self.show_tip(message, "success", duration, position)
    
    def warning(self, message, duration=3000, position="top-right"):
        """显示警告提示"""
        return self.show_tip(message, "warning", duration, position)
    
    def error(self, message, duration=3000, position="top-right"):
        """显示错误提示"""
        return self.show_tip(message, "error", duration, position)
    
    def confirm(self, message, title="确认", confirm_text="确定", cancel_text="取消"):
        """
        显示确认对话框
        
        参数:
            message: 对话框消息
            title: 对话框标题
            confirm_text: 确认按钮文本
            cancel_text: 取消按钮文本
        
        返回:
            Promise对象，用户确认返回True，取消返回False
        """
        try:
            if self.window:
                # 创建确认对话框配置
                confirm_config = {
                    "message": message,
                    "title": title,
                    "confirmText": confirm_text,
                    "cancelText": cancel_text
                }
                
                # 调用前端确认对话框
                result = self.window.evaluate_js(f"""
                    new Promise((resolve) => {{
                        window.dispatchEvent(new CustomEvent('show-confirm', {{ 
                            detail: {{
                                ...{json.dumps(confirm_config, ensure_ascii=False)},
                                callback: (result) => resolve(result)
                            }}
                        }}));
                    }})
                """)
                
                return result
            return False
        except Exception as e:
            logger.error(f"显示确认对话框失败: {e}")
            return False

# 创建全局提示信息API实例
# tips_api = TipsAPI() 