"""
模拟器连接模块
提供模拟器连接、获取列表等功能
"""
import logging
import os
import platform
import subprocess
import time
from backend.global_var import paras
from backend.emulators.Get_emulators_list import Get_emulators_list
from backend.emulators.MuMuCap import MuMuCap
from backend.emulators.Mouse import MouseController
from backend.img_api.Ocr import Ocr
from backend.emulators.Keyboard import Keyboard

# 导入平台特定的库
if platform.system() == 'Windows':
    import win32gui
    import ctypes

class EmulatorConnect:
    """模拟器连接类，提供模拟器连接相关功能"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化模拟器连接模块")
        self.emulators_list = []
        self.current_emulator = None
        self.platform = platform.system()
        self.adb_path = None
    
    def get_emulator_list(self):
        """
        获取模拟器列表，增强Windows系统支持和兼容性
        :return: 包含模拟器列表和状态的字典
        """
        mumu_path = paras.sys_settings.get('mumuPath', '')
        
        try:
            # 如果路径未设置或无效，尝试自动查找（Windows系统优化）
            if not mumu_path or not os.path.exists(mumu_path):
                if self.platform == 'Windows':
                    self.logger.info("尝试自动查找MuMu模拟器路径")
                    # 创建不带路径参数的实例，让它自动查找
                    emulators_auto = Get_emulators_list()
                    mumu_path = emulators_auto.MuMu_path
                    if mumu_path and os.path.exists(mumu_path):
                        self.logger.info(f"自动找到了MuMu模拟器路径: {mumu_path}")
                        # 更新全局设置
                        paras.sys_settings['mumuPath'] = mumu_path
                    else:
                        self.logger.warning("MuMu模拟器路径未设置或路径无效")
                        return {
                            'status': False,
                            'message': '请在设置中选择MuMu模拟器路径',
                            'data': []
                        }
                else:
                    self.logger.warning("MuMu模拟器路径未设置或路径无效")
                    return {
                        'status': False,
                        'message': '请在设置中选择MuMu模拟器路径',
                        'data': []
                    }
            
            # 尝试获取ADB路径
            emulators_adb = Get_emulators_list(mumu_path)
            self.adb_path = emulators_adb.adb_path
            
            # 针对Windows系统的特殊优化
            if self.platform == 'Windows':
                attempts = 0
                max_attempts = 2
                while attempts < max_attempts and not self.emulators_list:
                    attempts += 1
                    try:
                        emulators = Get_emulators_list(mumu_path)
                        self.emulators_list = emulators.get_mumu_list()
                        
                        # 如果列表为空，尝试重启ADB服务
                        if not self.emulators_list and self.adb_path and attempts == 1:
                            self.logger.info("尝试重启ADB服务以获取更多模拟器...")
                            try:
                                subprocess.run([self.adb_path, 'kill-server'], capture_output=True, timeout=2)
                                subprocess.run([self.adb_path, 'start-server'], capture_output=True, timeout=2)
                                time.sleep(1)  # 等待ADB服务启动
                            except Exception as e:
                                self.logger.error(f"重启ADB服务失败: {str(e)}")
                    except Exception as e:
                        self.logger.error(f"获取模拟器列表第{attempts}次尝试失败: {str(e)}")
            else:
                # 非Windows系统直接获取
                emulators = Get_emulators_list(mumu_path)
                self.emulators_list = emulators.get_mumu_list()
            
            if not self.emulators_list:
                # 再次尝试直接使用ADB命令获取
                try:
                    self.logger.info("尝试直接使用ADB命令获取模拟器列表...")
                    emulators = Get_emulators_list(mumu_path)
                    self.emulators_list = emulators._get_mumu_list_by_adb()
                except Exception as e:
                    self.logger.error(f"直接使用ADB命令获取失败: {str(e)}")
                
                if not self.emulators_list:
                    self.logger.warning("未检测到MuMu模拟器实例")
                    return {
                        'status': False,
                        'message': '未检测到MuMu模拟器实例，请确认模拟器已启动且ADB服务正常',
                        'data': []
                    }
            
            self.logger.info(f"成功获取到{len(self.emulators_list)}个模拟器实例")
            return {
                'status': True,
                'message': '成功获取模拟器列表',
                'data': self.emulators_list,
                'adb_path': self.adb_path  # 返回ADB路径，方便后续使用
            }
        
        except Exception as e:
            self.logger.error(f"获取模拟器列表时发生错误: {str(e)}")
            error_msg = f'获取模拟器列表失败: {str(e)}'
            # 提供更具体的错误提示
            if "找不到ADB" in str(e) or "adb.exe" in str(e):
                error_msg += "，请确认模拟器已安装且ADB路径正确"
            elif "权限" in str(e) or "AccessDenied" in str(e):
                error_msg += "，请以管理员权限运行程序"
            
            return {
                'status': False,
                'message': error_msg,
                'data': []
            }
    
    def connect_emulator(self, index):
        """
        连接指定的模拟器，增强Windows系统支持和兼容性
        :param index: 模拟器索引
        :return: 连接结果
        """
        try:
            if hasattr(paras, 'over') and time.time() > paras.over:
                return
            
            # 查找指定索引的模拟器
            target_emulator = None
            for emulator in self.emulators_list:
                if emulator['编号'] == index:
                    target_emulator = emulator
                    break
            
            if not target_emulator:
                # 如果通过索引未找到，尝试直接通过名称或ADB ID查找
                for emulator in self.emulators_list:
                    if str(index) in str(emulator.get('名称', '')) or str(index) in str(emulator.get('ADB', '')):
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
                self.logger.warning(f"模拟器 {target_emulator['名称']} 未处于开启状态")
                # 尝试重新连接该模拟器
                try:
                    if not self.adb_path:
                        # 重新获取ADB路径
                        emulators = Get_emulators_list(paras.sys_settings['mumuPath'])
                        self.adb_path = emulators.adb_path
                    
                    if self.adb_path and 'ADB' in target_emulator:
                        serial = target_emulator['ADB']
                        self.logger.info(f"尝试连接模拟器: {serial}")
                        subprocess.run([self.adb_path, 'connect', serial], capture_output=True, timeout=2)
                        time.sleep(0.5)  # 等待连接
                        
                        # 再次检查设备状态
                        result = subprocess.run([self.adb_path, 'devices'], capture_output=True, text=True, timeout=2)
                        if serial in result.stdout and 'device' in result.stdout:
                            target_emulator['状态'] = 'M-开启'
                            self.logger.info(f"成功连接到模拟器: {serial}")
                        else:
                            self.logger.warning(f"模拟器连接失败: {serial}")
                            return {
                                'status': False,
                                'message': f'模拟器 {target_emulator["名称"]} 未启动或连接异常，尝试手动连接后再试'
                            }
                except Exception as e:
                    self.logger.error(f"尝试重新连接模拟器失败: {str(e)}")
                    return {
                        'status': False,
                        'message': f'模拟器 {target_emulator["名称"]} 未启动或连接异常，尝试手动连接后再试'
                    }
            
            # 更新全局变量中的模拟器信息
            paras.emulator_info['name'] = target_emulator['名称']
            paras.emulator_info['index'] = target_emulator['编号']
            paras.emulator_info['adb_port'] = target_emulator['ADB']
            paras.emulator_info['state'] = True
            
            # 保存当前模拟器信息
            self.current_emulator = target_emulator
            
            # 加载模拟器api
            paras.emulator_api['cap'] = MuMuCap(target_emulator['编号'], paras.sys_settings['mumuPath'])
            paras.emulator_api['cap'].set_fps(paras.sys_settings.get('screenshot_fps', 10))
            
            # 根据操作系统初始化鼠标控制器（Windows系统特殊优化）
            connection_attempts = 0
            max_attempts = 2
            mouse_controller_success = False
            
            while connection_attempts < max_attempts and not mouse_controller_success:
                connection_attempts += 1
                try:
                    if self.platform == 'Windows':
                        # Windows平台优先使用mumu模式
                        self.logger.info(f"尝试使用mumu模式连接模拟器（第{connection_attempts}次尝试）")
                        paras.emulator_api['mouse'] = MouseController(
                            emulator_type='mumu',
                            emulator_install_path=paras.sys_settings['mumuPath'],
                            instance_index=paras.emulator_info['index']
                        )
                        
                        # 验证鼠标控制器是否正常工作
                        if hasattr(paras.emulator_api['mouse'], 'mumu_api') and hasattr(paras.emulator_api['mouse'].mumu_api, 'hwnd'):
                            if paras.emulator_api['mouse'].mumu_api.hwnd:
                                mouse_controller_success = True
                                self.logger.info(f"成功使用mumu模式连接，窗口句柄: {paras.emulator_api['mouse'].mumu_api.hwnd}")
                                break
                            else:
                                self.logger.warning("mumu模式连接成功，但未获取到窗口句柄")
                        else:
                            self.logger.warning("mumu模式连接成功，但不包含预期的API属性")
                    
                    # 如果mumu模式失败或不是Windows系统，使用maa模式作为备选
                    if not mouse_controller_success:
                        if not self.adb_path:
                            # 重新获取ADB路径
                            emulators = Get_emulators_list(paras.sys_settings['mumuPath'])
                            self.adb_path = emulators.adb_path
                        
                        self.logger.info(f"尝试使用maa模式连接模拟器（第{connection_attempts}次尝试）")
                        paras.emulator_api['mouse'] = MouseController(
                            emulator_type='maa',
                            mumupath=paras.sys_settings['mumuPath'],
                            serial=paras.emulator_info['adb_port'],
                            adb_path=self.adb_path
                        )
                        
                        # 验证ADB连接
                        if self.adb_path and paras.emulator_info['adb_port']:
                            try:
                                result = subprocess.run(
                                    [self.adb_path, '-s', paras.emulator_info['adb_port'], 'shell', 'echo', 'alive'],
                                    capture_output=True,
                                    text=True,
                                    timeout=2
                                )
                                if result.returncode == 0 and 'alive' in result.stdout:
                                    mouse_controller_success = True
                                    self.logger.info("成功通过ADB验证模拟器连接")
                                    break
                                else:
                                    self.logger.warning("ADB连接验证失败")
                            except Exception as e:
                                self.logger.error(f"ADB验证命令执行失败: {str(e)}")
                except Exception as e:
                    self.logger.error(f"初始化鼠标控制器失败: {str(e)}")
                    if connection_attempts >= max_attempts:
                        raise e
                    time.sleep(0.5)
            
            # 如果鼠标控制器初始化失败，抛出异常
            if not mouse_controller_success:
                raise Exception("鼠标控制器初始化失败，无法连接到模拟器")
            
            # 根据操作系统初始化键盘控制器
            if self.platform == 'Windows':
                # Windows平台使用窗口句柄
                try:
                    window_handle = win32gui.FindWindow(None, paras.emulator_info['name'])
                    if not window_handle and hasattr(paras.emulator_api['mouse'], 'mumu_api') and hasattr(paras.emulator_api['mouse'].mumu_api, 'hwnd'):
                        window_handle = paras.emulator_api['mouse'].mumu_api.hwnd
                    
                    if window_handle:
                        paras.emulator_api['keyboard'] = Keyboard(window_handle)
                        self.logger.info(f"成功初始化键盘控制器，窗口句柄: {window_handle}")
                    else:
                        # 如果无法获取窗口句柄，使用ADB作为备选
                        self.logger.warning("无法获取窗口句柄，尝试使用ADB键盘控制器")
                        if not self.adb_path:
                            emulators = Get_emulators_list(paras.sys_settings['mumuPath'])
                            self.adb_path = emulators.adb_path
                        
                        paras.emulator_api['keyboard'] = Keyboard(
                            serial=paras.emulator_info['adb_port'],
                            adb_path=self.adb_path
                        )
                except Exception as e:
                    self.logger.error(f"初始化Windows键盘控制器失败: {str(e)}")
                    # 降级使用ADB键盘控制器
                    if not self.adb_path:
                        emulators = Get_emulators_list(paras.sys_settings['mumuPath'])
                        self.adb_path = emulators.adb_path
                    
                    paras.emulator_api['keyboard'] = Keyboard(
                        serial=paras.emulator_info['adb_port'],
                        adb_path=self.adb_path
                    )
            else:
                # 非Windows平台使用ADB设备序列号
                if not self.adb_path:
                    emulators = Get_emulators_list(paras.sys_settings['mumuPath'])
                    self.adb_path = emulators.adb_path
                
                paras.emulator_api['keyboard'] = Keyboard(
                    serial=paras.emulator_info['adb_port'],
                    adb_path=self.adb_path
                )
            
            # 初始化OCR
            try:
                paras.emulator_api['ocr'] = Ocr()
            except Exception as e:
                self.logger.warning(f"OCR初始化失败: {str(e)}")
            
            # 保存连接信息
            paras.emulator_info['connection_type'] = 'mumu_api' if self.platform == 'Windows' and hasattr(paras.emulator_api['mouse'], 'mumu_api') else 'adb'
            paras.emulator_info['adb_path'] = self.adb_path
            
            self.logger.info(f"成功连接到模拟器: {target_emulator['名称']}")
            return {
                'status': True,
                'message': f'成功连接到模拟器: {target_emulator["名称"]}',
                'emulatorInfo': paras.emulator_info,
                'connection_type': paras.emulator_info['connection_type']
            }
        
        except Exception as e:
            self.logger.error(f"连接模拟器时发生错误: {str(e)}")
            error_msg = f'连接模拟器失败: {str(e)}'
            # 提供更详细的错误信息和解决方案
            if "找不到ADB" in str(e) or "adb.exe" in str(e):
                error_msg += "，请确认模拟器已安装且ADB路径正确"
            elif "权限" in str(e) or "AccessDenied" in str(e):
                error_msg += "，请以管理员权限运行程序"
            elif "连接超时" in str(e) or "timeout" in str(e).lower():
                error_msg += "，请检查网络连接和防火墙设置"
            elif "窗口句柄" in str(e) or "hwnd" in str(e).lower():
                error_msg += "，请确认模拟器窗口已打开"
            
            return {
                'status': False,
                'message': error_msg
            }
    
    def disconnect_emulator(self):
        """
        断开当前模拟器连接
        :return: 断开结果
        """
        try:
            if self.current_emulator or (hasattr(paras, 'emulator_info') and paras.emulator_info.get('state', False)):
                # 释放资源
                if hasattr(paras, 'emulator_api'):
                    # 断开鼠标控制器
                    if 'mouse' in paras.emulator_api and paras.emulator_api['mouse']:
                        if hasattr(paras.emulator_api['mouse'], 'mumu_api') and hasattr(paras.emulator_api['mouse'].mumu_api, 'disconnect'):
                            try:
                                paras.emulator_api['mouse'].mumu_api.disconnect()
                            except Exception as e:
                                self.logger.warning(f"断开鼠标控制器失败: {str(e)}")
                        paras.emulator_api['mouse'] = None
                    
                    # 断开键盘控制器
                    if 'keyboard' in paras.emulator_api:
                        paras.emulator_api['keyboard'] = None
                    
                    # 断开截图组件
                    if 'cap' in paras.emulator_api:
                        paras.emulator_api['cap'] = None
                    
                    # 断开OCR
                    if 'ocr' in paras.emulator_api:
                        paras.emulator_api['ocr'] = None
                
                # 重置模拟器信息
                if hasattr(paras, 'emulator_info'):
                    paras.emulator_info['state'] = False
                    paras.emulator_info['name'] = ''
                    paras.emulator_info['index'] = -1
                    paras.emulator_info['adb_port'] = ''
                
                self.current_emulator = None
                
                self.logger.info("成功断开模拟器连接")
                return {
                    'status': True,
                    'message': '成功断开模拟器连接'
                }
            else:
                return {
                    'status': True,
                    'message': '当前未连接任何模拟器'
                }
        except Exception as e:
            self.logger.error(f"断开模拟器连接时发生错误: {str(e)}")
            return {
                'status': False,
                'message': f'断开模拟器连接失败: {str(e)}'
            }
    
    def get_connection_status(self):
        """
        获取当前连接状态
        :return: 连接状态信息
        """
        try:
            if hasattr(paras, 'emulator_info') and paras.emulator_info.get('state', False):
                # 检查连接是否仍然有效
                is_connected = False
                
                if self.platform == 'Windows' and hasattr(paras, 'emulator_api') and 'mouse' in paras.emulator_api:
                    # 检查窗口是否存在
                    try:
                        if hasattr(paras.emulator_api['mouse'], 'mumu_api') and hasattr(paras.emulator_api['mouse'].mumu_api, 'hwnd'):
                            hwnd = paras.emulator_api['mouse'].mumu_api.hwnd
                            if hwnd:
                                is_connected = ctypes.windll.user32.IsWindow(hwnd)
                    except Exception as e:
                        self.logger.warning(f"检查窗口状态失败: {str(e)}")
                
                # 如果窗口检查失败或不是Windows系统，使用ADB检查
                if not is_connected and hasattr(paras, 'emulator_info') and paras.emulator_info.get('adb_port') and self.adb_path:
                    try:
                        result = subprocess.run(
                            [self.adb_path, '-s', paras.emulator_info['adb_port'], 'shell', 'echo', 'alive'],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        is_connected = result.returncode == 0 and 'alive' in result.stdout
                    except Exception as e:
                        self.logger.warning(f"使用ADB检查连接状态失败: {str(e)}")
                
                if is_connected:
                    return {
                        'status': True,
                        'connected': True,
                        'emulator_info': paras.emulator_info,
                        'connection_type': paras.emulator_info.get('connection_type', 'unknown')
                    }
                else:
                    # 如果连接失效，自动断开
                    self.disconnect_emulator()
                    return {
                        'status': True,
                        'connected': False,
                        'reason': '连接已失效'
                    }
            else:
                return {
                    'status': True,
                    'connected': False
                }
        except Exception as e:
            self.logger.error(f"获取连接状态时发生错误: {str(e)}")
            return {
                'status': False,
                'message': f'获取连接状态失败: {str(e)}'
            }