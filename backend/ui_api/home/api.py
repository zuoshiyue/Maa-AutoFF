"""
主页API模块
提供主页相关的功能接口
"""
import logging
from backend.global_var import paras
from .emulator_connect import EmulatorConnect

class HomeAPI:
    """主页API类，提供主页相关的功能接口"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化主页API")
        self.emulator_connect = EmulatorConnect()
        self.window = None
    
    def set_window(self, window):
        """
        设置窗口引用
        :param window: pywebview窗口对象
        """
        self.logger.info("设置主页API窗口引用")
        self.window = window
    
    def get_emulator_status(self):
        """
        获取模拟器连接状态和相关信息
        :return: 包含模拟器路径和连接状态的字典
        """
        return {
            'mumuPath': paras.sys_settings['mumuPath'],
            'emulatorInfo': paras.emulator_info
        }
    
    def get_emulator_list(self):
        """
        获取模拟器列表
        :return: 模拟器列表和状态
        """
        return self.emulator_connect.get_emulator_list()
    
    def connect_emulator(self, index):
        """
        连接指定的模拟器
        :param index: 模拟器索引
        :return: 连接结果
        """
        return self.emulator_connect.connect_emulator(index) 