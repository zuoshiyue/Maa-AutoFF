# 获取所有MuMu模拟器实例的信息
import os
import subprocess
import json
import platform
import re

class Get_emulators_list:
    def __init__(self, MuMu_path=''):
        self.MuMu_path = MuMu_path
        # 根据操作系统设置不同的路径分隔符
        self.sep = ';' if platform.system() == 'Windows' else ':'
        self._initialize_paths()
        
    def _initialize_paths(self):
        """
        初始化模拟器相关路径
        """
        if not self.MuMu_path:
            # 尝试从系统环境变量或默认位置获取
            if platform.system() == 'Windows':
                self.MuMu_path = os.environ.get('MUMU_PATH', r'C:\Program Files\MuMuPlayer-12.0')
            elif platform.system() == 'Darwin':  # macOS
                self.MuMu_path = os.environ.get('MUMU_PATH', '/Applications/MuMuPlayer-12.app/Contents/MacOS')
            else:  # Linux
                self.MuMu_path = os.environ.get('MUMU_PATH', '/opt/mumuhyperv')
        
        # 根据不同版本的MuMu模拟器设置路径
        self.shell_dir = os.path.join(self.MuMu_path, "shell")
        # MuMu模拟器5
        self.nx_main_dir = os.path.join(self.MuMu_path, "nx_main")
        # MacOS下的路径
        self.mac_app_path = os.path.join(self.MuMu_path, "vms")
        
        # 设置shell路径
        if os.path.exists(self.shell_dir) and os.path.isdir(self.shell_dir):
            self.shell_path = self.shell_dir
        elif os.path.exists(self.nx_main_dir) and os.path.isdir(self.nx_main_dir):
            self.shell_path = self.nx_main_dir
        elif os.path.exists(self.mac_app_path) and os.path.isdir(self.mac_app_path):
            self.shell_path = self.mac_app_path
        else:
            # 不抛出异常，尝试使用ADB命令获取列表
            print(f"无法找到MuMu模拟器的shell文件夹，但仍会尝试通过ADB获取模拟器列表")
            self.shell_path = None
        
        # 设置管理器路径
        if self.shell_path and os.path.exists(os.path.join(self.shell_path, 'MuMuManager.exe')):
            self.mumu_manager = os.path.join(self.shell_path, 'MuMuManager.exe')
        else:
            self.mumu_manager = None
            
        # 设置ADB路径（优先使用模拟器自带的ADB）
        self.adb_path = self._find_adb()
        
    def _find_adb(self):
        """
        查找ADB可执行文件路径
        """
        # 尝试从模拟器路径中查找ADB
        if self.shell_path:
            # 不同版本和平台的ADB路径
            possible_adb_paths = [
                os.path.join(self.shell_path, 'adb.exe'),  # Windows
                os.path.join(self.shell_path, 'adb'),      # Mac/Linux
                os.path.join(self.MuMu_path, 'adb.exe'),   # 其他可能的路径
                os.path.join(self.MuMu_path, 'adb')        # 其他可能的路径
            ]
            
            for path in possible_adb_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    return path
        
        # 尝试从系统PATH中查找ADB
        try:
            # Windows下使用where命令
            if platform.system() == 'Windows':
                result = subprocess.run(['where', 'adb'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip().split('\n')[0]
            # Mac/Linux下使用which命令
            else:
                result = subprocess.run(['which', 'adb'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip()
        except:
            pass
        
        # 默认返回adb命令（希望系统能找到）
        return 'adb.exe' if platform.system() == 'Windows' else 'adb'

    def get_mumu_list(self):
        """
        获取所有MuMu模拟器实例的信息，优先使用MuMuManager，失败则尝试ADB命令
        :return: 包含模拟器信息的列表
        """
        # 1. 首先尝试使用MuMuManager获取模拟器信息
        if self.mumu_manager and os.path.exists(self.mumu_manager):
            result = self._get_mumu_list_by_manager()
            if result:
                return result
        
        # 2. 如果MuMuManager不可用或失败，尝试使用ADB命令获取
        result = self._get_mumu_list_by_adb()
        if result:
            return result
        
        # 3. 如果所有方法都失败，返回空列表
        return []
    
    def _get_mumu_list_by_manager(self):
        """
        使用MuMuManager获取模拟器列表
        """
        try:
            # 设置Qt插件路径环境变量
            env = os.environ.copy()
            qt_plugin_path = os.path.join(self.MuMu_path, 'shell', 'plugins')

            # MuMu模拟器5
            if not os.path.exists(qt_plugin_path):
                qt_plugin_path = os.path.join(self.MuMu_path, 'nx_main', 'plugins')
            
            if 'QT_PLUGIN_PATH' not in env:
                env['QT_PLUGIN_PATH'] = qt_plugin_path
            else:
                env['QT_PLUGIN_PATH'] = f"{qt_plugin_path}{self.sep}{env['QT_PLUGIN_PATH']}"
            
            # 设置启动信息，不显示命令行窗口（仅Windows）
            startupinfo = None
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # 执行命令获取模拟器信息
            result = subprocess.run(
                [self.mumu_manager, 'info', '-v', 'all'],
                capture_output=True,
                encoding='utf-8',
                errors='ignore',  # 忽略无法解码的字符
                startupinfo=startupinfo,
                env=env
            )

            if result.returncode == 0 and result.stdout:
                # 解析输出信息
                emulators_info = []
                try:
                    result_json = json.loads(result.stdout)

                    # 处理不同格式的返回结果
                    # 检查是否为单个模拟器的情况（没有嵌套的字典）
                    if "index" in result_json:
                        # 单个模拟器的情况，将其转换为多个模拟器的格式
                        result_json = {result_json["index"]: result_json}
                        
                    # 处理所有模拟器
                    for item, value in result_json.items():
                        # 模拟器开启状态
                        if value.get('is_process_started', False):
                            json_cash = {
                                '状态': 'M-开启', 
                                '编号': int(value['index']), 
                                '名称': value['name'], 
                                'ADB': f"{value.get('adb_host_ip', '127.0.0.1')}:{value.get('adb_port', '0')}"
                            }
                        else:
                            json_cash = {
                                '状态': 'M-关闭', 
                                '编号': int(value['index']), 
                                '名称': value['name']
                            }
                        emulators_info.append(json_cash)
                    return emulators_info
                except json.JSONDecodeError:
                    print(f"解析MuMuManager输出失败: {result.stdout}")
                    return []
            else:
                error_msg = result.stderr if result.stderr else "未知错误"
                print(f"MuMuManager获取模拟器信息失败: {error_msg}")
                return []

        except Exception as e:
            print(f"执行MuMuManager命令时发生错误: {str(e)}")
            return []
    
    def _get_mumu_list_by_adb(self):
        """
        使用ADB命令获取模拟器列表，支持Mumu V5.4.0多开情况
        基于官方文档：https://mumu.163.com/help/20240807/40912_1073151.html
        """
        try:
            # 执行adb devices命令获取已连接的设备
            result = subprocess.run(
                [self.adb_path, 'devices'],
                capture_output=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                print(f"ADB命令执行失败: {result.stderr}")
                return []
            
            # 解析adb devices命令的输出
            emulators_info = []
            lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
            
            # 如果没有设备，尝试扫描默认端口范围
            if not lines:
                print("没有发现已连接的设备，尝试扫描Mumu默认端口...")
                # 尝试连接Mumu模拟器的默认端口范围
                # Mumu 5.0: 5555, 5557, 5559... (间隔2)
                # Mumu 12: 16384, 16416, 16448... (间隔32)
                default_ports = []
                # 生成Mumu 5.0的默认端口（5555开始，间隔2，共10个）
                for i in range(10):
                    default_ports.append(5555 + i * 2)
                # 生成Mumu 12的默认端口（16384开始，间隔32，共10个）
                for i in range(10):
                    default_ports.append(16384 + i * 32)
                
                # 尝试连接这些端口
                for port in default_ports:
                    try:
                        # 连接端口
                        subprocess.run(
                            [self.adb_path, 'connect', f'127.0.0.1:{port}'],
                            capture_output=True,
                            timeout=1  # 超时1秒
                        )
                    except:
                        continue
                
                # 再次执行adb devices获取已连接的设备
                result = subprocess.run(
                    [self.adb_path, 'devices'],
                    capture_output=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                lines = result.stdout.strip().split('\n')[1:]
            
            # 处理发现的设备
            for line in lines:
                line = line.strip()
                if line and 'device' in line:
                    device_info = line.split('\t')
                    if len(device_info) >= 2:
                        device_id = device_info[0]
                        device_status = device_info[1]
                        
                        # 判断是否为MuMu模拟器
                        is_mumu = False
                        emulator_name = 'MuMu模拟器'
                        index = 0
                        
                        # 根据设备ID判断模拟器类型和端口
                        # Mumu 5.0: 通常是emulator-端口号或127.0.0.1:端口号
                        # Mumu 12: 通常是127.0.0.1:端口号
                        if device_id.startswith('127.0.0.1:'):
                            port_str = device_id.split(':')[1]
                            try:
                                port = int(port_str)
                                # Mumu 5.0端口通常在5555附近，间隔2
                                if 5550 <= port <= 5600 and (port - 5555) % 2 == 0:
                                    is_mumu = True
                                    index = (port - 5555) // 2
                                    emulator_name = f'MuMu模拟器5.0({index})'
                                # Mumu 12端口通常在16384附近，间隔32
                                elif 16300 <= port <= 17000 and (port - 16384) % 32 == 0:
                                    is_mumu = True
                                    index = (port - 16384) // 32
                                    emulator_name = f'MuMu模拟器12({index})'
                                # 其他端口也可能是Mumu模拟器
                                else:
                                    is_mumu = True
                                    emulator_name = f'MuMu模拟器({port})'
                            except:
                                is_mumu = True
                                emulator_name = f'MuMu模拟器({device_id})'
                        elif device_id.startswith('emulator-'):
                            # 标准Android模拟器命名格式，但也可能是MuMu
                            is_mumu = True
                            emulator_name = f'MuMu模拟器({device_id})'
                            # 尝试从设备ID中提取端口信息
                            match = re.search(r'emulator-(\d+)', device_id)
                            if match:
                                try:
                                    port = int(match.group(1))
                                    # Android模拟器通常使用偶数端口号作为控制台端口，奇数作为ADB端口
                                    # Mumu 5.0通常使用奇数端口作为ADB端口
                                    if port % 2 == 1 and 5550 <= port <= 5600:
                                        index = (port - 5555) // 2
                                        emulator_name = f'MuMu模拟器5.0({index})'
                                except:
                                    pass
                        
                        if is_mumu:
                            status = 'M-开启' if device_status == 'device' else 'M-连接异常'
                            emulators_info.append({
                                '状态': status,
                                '编号': index,
                                '名称': emulator_name,
                                'ADB': device_id
                            })
            
            return emulators_info
        except Exception as e:
            print(f"执行ADB命令获取模拟器列表时发生错误: {str(e)}")
            return []


if __name__ == '__main__':
    # 测试获取模拟器列表功能
    get_emulators_list = Get_emulators_list()
    print(f"使用的ADB路径: {get_emulators_list.adb_path}")
    result = get_emulators_list.get_mumu_list()
    print("模拟器列表：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 如果找到模拟器，可以测试连接
    if result:
        print("\n尝试连接第一个模拟器...")
        first_emulator = result[0]
        if 'ADB' in first_emulator:
            try:
                # 执行adb命令查看设备状态
                test_cmd = [get_emulators_list.adb_path, '-s', first_emulator['ADB'], 'shell', 'getprop', 'ro.product.model']
                print(f"执行命令: {' '.join(test_cmd)}")
                test_result = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=3
                )
                if test_result.returncode == 0:
                    print(f"连接成功，设备型号: {test_result.stdout.strip()}")
                else:
                    print(f"连接测试失败: {test_result.stderr}")
            except Exception as e:
                print(f"连接测试异常: {str(e)}")

