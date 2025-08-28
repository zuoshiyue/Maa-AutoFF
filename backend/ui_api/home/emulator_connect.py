"""
模拟器连接模块
提供模拟器连接、获取列表等功能
"""
import logging
import os
import platform
from backend.global_var import paras
from backend.emulators.Get_emulators_list import Get_emulators_list
from backend.emulators.MuMuCap import MuMuCap
from backend.emulators.Mouse import MouseController
from backend.img_api.Ocr import Ocr
from backend.emulators.Keyboard import Keyboard
import time

# 导入平台特定的库
if platform.system() == 'Windows':
    import win32gui

class EmulatorConnect:
    """模拟器连接类，提供模拟器连接相关功能"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化模拟器连接模块")
        self.emulators_list = []
    
    def get_emulator_list(self):
        """
        获取模拟器列表
        :return: 包含模拟器列表和状态的字典
        """
        mumu_path = paras.sys_settings['mumuPath']
        
        # 检查模拟器路径是否设置
        if not mumu_path or not os.path.exists(mumu_path):
            self.logger.warning("MuMu模拟器路径未设置或路径无效")
            return {
                'status': False,
                'message': '请在设置中选择MuMu模拟器路径',
                'data': []
            }
        
        try:
            # 获取模拟器列表
            emulators = Get_emulators_list(mumu_path)
            self.emulators_list = emulators.get_mumu_list()
            
            if not self.emulators_list:
                self.logger.warning("未检测到MuMu模拟器实例")
                return {
                    'status': False,
                    'message': '未检测到MuMu模拟器实例',
                    'data': []
                }
            
            self.logger.info(f"成功获取到{len(self.emulators_list)}个模拟器实例")
            return {
                'status': True,
                'message': '成功获取模拟器列表',
                'data': self.emulators_list
            }
        
        except Exception as e:
            self.logger.error(f"获取模拟器列表时发生错误: {str(e)}")
            return {
                'status': False,
                'message': f'获取模拟器列表失败: {str(e)}',
                'data': []
            }
    
    def connect_emulator(self, index):
        """
        连接指定的模拟器
        :param index: 模拟器索引
        :return: 连接结果
        """
        try:
            if time.time() > paras.over:
                return
            # 查找指定索引的模拟器
            target_emulator = None
            for emulator in self.emulators_list:
                if emulator['编号'] == index:
                    target_emulator = emulator
                    break
            
            if not target_emulator:
                self.logger.warning(f"未找到索引为{index}的模拟器")
                return {
                    'status': False,
                    'message': f'未找到索引为{index}的模拟器'
                }
            
            # 检查模拟器状态
            if target_emulator['状态'] != 'M-开启':
                self.logger.warning(f"模拟器 {target_emulator['名称']} 未启动")
                return {
                    'status': False,
                    'message': f'模拟器 {target_emulator["名称"]} 未启动，请先启动模拟器'
                }
            
            # 更新全局变量中的模拟器信息
            paras.emulator_info['name'] = target_emulator['名称']
            paras.emulator_info['index'] = target_emulator['编号']
            paras.emulator_info['adb_port'] = target_emulator['ADB']
            paras.emulator_info['state'] = True
            
            # 加载模拟器api
            paras.emulator_api['cap'] = MuMuCap(target_emulator['编号'], paras.sys_settings['mumuPath'])
            paras.emulator_api['cap'].set_fps(paras.sys_settings['screenshot_fps'])
            
            # 根据操作系统初始化鼠标控制器
            if platform.system() == 'Windows':
                # Windows平台使用mumu模式
                paras.emulator_api['mouse'] = MouseController(
                    emulator_type='mumu',
                    emulator_install_path=paras.sys_settings['mumuPath'],
                    instance_index=paras.emulator_info['index']
                )
            else:
                # 非Windows平台使用maa模式（通过ADB控制）
                paras.emulator_api['mouse'] = MouseController(
                    emulator_type='maa',
                    mumupath=paras.sys_settings['mumuPath'],
                    serial=paras.emulator_info['adb_port'],
                    adb_path=adb_path  # 传递之前获取的ADB路径
                )
            
            # 根据操作系统初始化键盘控制器
            if platform.system() == 'Windows':
                # Windows平台使用窗口句柄
                window_handle = win32gui.FindWindow(None, paras.emulator_info['name'])
                paras.emulator_api['keyboard'] = Keyboard(window_handle)
            else:
                # Mac平台使用ADB设备序列号
                # 获取ADB路径（从Get_emulators_list类中可以找到）
                emulators = Get_emulators_list(paras.sys_settings['mumuPath'])
                adb_path = emulators.adb_path
                # 使用ADB设备序列号初始化键盘控制器
                paras.emulator_api['keyboard'] = Keyboard(
                    serial=paras.emulator_info['adb_port'],
                    adb_path=adb_path
                )
            
            paras.emulator_api['ocr'] = Ocr()
            
            
            self.logger.info(f"成功连接到模拟器: {target_emulator['名称']}")
            return {
                'status': True,
                'message': f'成功连接到模拟器: {target_emulator["名称"]}',
                'emulatorInfo': paras.emulator_info
            }
        
        except Exception as e:
            self.logger.error(f"连接模拟器时发生错误: {str(e)}")
            return {
                'status': False,
                'message': f'连接模拟器失败: {str(e)}'
            }