### 后台键盘类
import string
import time
import platform
import subprocess

# 根据操作系统导入不同的库
system = platform.system()
if system == 'Windows':
    from ctypes import windll
    import win32api
    import win32con
    import win32gui
    from win32com import client
elif system == 'Darwin':  # macOS
    # 导入必要的模块
    pass
else:
    # Linux 或其他系统，这里暂时不处理
    pass

class Keyboard():
    def __init__(self, hwnd=None, serial=None, adb_path='adb') -> None:
        self.system = platform.system()
        self.serial = serial  # ADB设备序列号
        self.adb_path = adb_path  # ADB工具路径
        
        if self.system == 'Windows':
            self._init_windows(hwnd)
        elif self.system == 'Darwin':  # macOS
            self._init_macos(serial, adb_path)
        else:
            print(f"不支持的操作系统: {self.system}")
    
    def _init_windows(self, hwnd):
        import sys
        if not windll.shell32.IsUserAnAdmin():
            # 需要和目标窗口同一权限，游戏窗口通常是管理员权限
            # 不是管理员就提权
            windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, __file__, None, 1)
        self.handle = hwnd
        self.PostMessageW = windll.user32.PostMessageW
        self.MapVirtualKeyW = windll.user32.MapVirtualKeyW
        self.VkKeyScanA = windll.user32.VkKeyScanA

        self.WM_KEYDOWN = 0x100
        self.WM_KEYUP = 0x101

        # https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
        self.VkCode = {
            "back":  0x08,
            "tab":  0x09,
            "return":  0x0D,
            "shift":  0x10,
            "control":  0x11,
            "menu":  0x12,
            "pause":  0x13,
            "capital":  0x14,
            "esc":  0x1B,
            "space":  0x20,
            "end":  0x23,
            "home":  0x24,
            "left":  0x25,
            "up":  0x26,
            "right":  0x27,
            "down":  0x28,
            "print":  0x2A,
            "snapshot":  0x2C,
            "insert":  0x2D,
            "delete":  0x2E,
            "lwin":  0x5B,
            "rwin":  0x5C,
            "numpad0":  0x60,
            "numpad1":  0x61,
            "numpad2":  0x62,
            "numpad3":  0x63,
            "numpad4":  0x64,
            "numpad5":  0x65,
            "numpad6":  0x66,
            "numpad7":  0x67,
            "numpad8":  0x68,
            "numpad9":  0x69,
            "multiply":  0x6A,
            "add":  0x6B,
            "separator":  0x6C,
            "subtract":  0x6D,
            "decimal":  0x6E,
            "divide":  0x6F,
            "f1":  0x70,
            "f2":  0x71,
            "f3":  0x72,
            "f4":  0x73,
            "f5":  0x74,
            "f6":  0x75,
            "f7":  0x76,
            "f8":  0x77,
            "f9":  0x78,
            "f10":  0x79,
            "f11":  0x7A,
            "f12":  0x7B,
            "numlock":  0x90,
            "scroll":  0x91,
            "lshift":  0xA0,
            "rshift":  0xA1,
            "lcontrol":  0xA2,
            "rcontrol":  0xA3,
            "lmenu":  0xA4,
            "rmenu":  0XA5,
            "larrow": 0x37,     # 左箭头
            "rarrow": 0x39,     # 右箭头
        }
        
    def _init_macos(self, serial, adb_path):
        # macOS初始化，使用ADB控制模拟器
        self.serial = serial
        self.adb_path = adb_path
        # Android KeyEvent 映射表
        # 参考：https://developer.android.com/reference/android/view/KeyEvent
        self.key_mapping = {
            "back": "KEYCODE_BACK",
            "tab": "KEYCODE_TAB",
            "return": "KEYCODE_ENTER",
            "shift": "KEYCODE_SHIFT_LEFT",
            "control": "KEYCODE_CTRL_LEFT",
            "menu": "KEYCODE_MENU",
            "esc": "KEYCODE_ESCAPE",
            "space": "KEYCODE_SPACE",
            "end": "KEYCODE_MOVE_END",
            "home": "KEYCODE_MOVE_HOME",
            "left": "KEYCODE_DPAD_LEFT",
            "up": "KEYCODE_DPAD_UP",
            "right": "KEYCODE_DPAD_RIGHT",
            "down": "KEYCODE_DPAD_DOWN",
            "delete": "KEYCODE_DEL",
            "f1": "KEYCODE_F1",
            "f2": "KEYCODE_F2",
            "f3": "KEYCODE_F3",
            "f4": "KEYCODE_F4",
            "f5": "KEYCODE_F5",
            "f6": "KEYCODE_F6",
            "f7": "KEYCODE_F7",
            "f8": "KEYCODE_F8",
            "f9": "KEYCODE_F9",
            "f10": "KEYCODE_F10",
            "f11": "KEYCODE_F11",
            "f12": "KEYCODE_F12",
            "larrow": "KEYCODE_DPAD_LEFT",
            "rarrow": "KEYCODE_DPAD_RIGHT"
        }

    def get_virtual_keycode(self, key: str):
        """根据按键名获取虚拟按键码

        Args:
            key (str): 按键名

        Returns:
            int: 虚拟按键码
        """
        if self.system == 'Windows':
            if len(key) == 1 and key in string.printable:
                # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-vkkeyscana
                return self.VkKeyScanA(ord(key)) & 0xff
            else:
                return self.VkCode[key]
        elif self.system == 'Darwin':
            # 在macOS上，我们返回按键名本身，因为ADB命令使用的是键名
            return key

    def key_down(self, key: str):
        """按下指定按键

        Args:
            key (str): 按键名
        """
        if self.system == 'Windows':
            vk_code = self.get_virtual_keycode(key)
            scan_code = self.MapVirtualKeyW(vk_code, 0)
            wparam = vk_code
            lparam = (scan_code << 16) | 1
            self.PostMessageW(self.handle, self.WM_KEYDOWN, wparam, lparam)
        elif self.system == 'Darwin':
            # macOS上使用ADB命令发送按键按下事件
            if self.serial:
                try:
                    # 将key转换为Android按键名
                    android_key = self.key_mapping.get(key.lower(), key)
                    # 检查是否为单个字符
                    if len(key) == 1 and key in string.printable:
                        # 对于单个字符，使用input text命令
                        cmd = [self.adb_path, '-s', self.serial, 'shell', f'input text "{key}"']
                    else:
                        # 对于特殊按键，使用keyevent命令
                        cmd = [self.adb_path, '-s', self.serial, 'shell', f'input keyevent {android_key}']
                    subprocess.run(cmd, capture_output=True, text=True)
                except Exception as e:
                    print(f"ADB发送按键按下事件失败: {str(e)}")

    def key_up(self, key: str):
        """放开指定按键

        Args:
            key (str): 按键名
        """
        if self.system == 'Windows':
            vk_code = self.get_virtual_keycode(key)
            scan_code = self.MapVirtualKeyW(vk_code, 0)
            # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keyup
            wparam = vk_code
            lparam = (scan_code << 16) | 0XC0000001
            self.PostMessageW(self.handle, self.WM_KEYUP, wparam, lparam)
        elif self.system == 'Darwin':
            # 在macOS上，ADB命令本身就是一个完整的按键事件，不需要单独的key_up
            # 这里可以留空或添加日志
            pass

    def key_push(self, key: str, t=0.1):
        """按下并弹起按键

        Args:
            key (str): 按键名
            t (float): 按下时长
        """
        self.key_down(key)
        time.sleep(t)
        self.key_up(key)

    def key_push_front(self, key: str, t=0.1):
        """按下并弹起按键----前台
        Args:
            key (str): 按键名
            t (float): 按下时长
        """
        if self.system == 'Windows':
            vk_code = self.get_virtual_keycode(key)
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(t) 
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif self.system == 'Darwin':
            # macOS上使用ADB命令，这里调用key_down即可
            self.key_down(key)

    # 后台输入字符
    def input_character(self, key: str, t=0.05):
        if self.system == 'Windows':
            win32api.SendMessage(self.handle, win32con.WM_CHAR, ord(key), 0)    # 激活原先窗口
        elif self.system == 'Darwin':
            # macOS上使用ADB命令输入字符
            if self.serial:
                try:
                    cmd = [self.adb_path, '-s', self.serial, 'shell', f'input text "{key}"']
                    subprocess.run(cmd, capture_output=True, text=True)
                    time.sleep(t)
                except Exception as e:
                    print(f"ADB输入字符失败: {str(e)}")
        
    # 后台输入字符串
    def input_string(self, text: str, interval=0):
        """后台输入字符串
        
        Args:
            text (str): 要输入的字符串
            interval (float): 字符间的时间间隔
        """
        if self.system == 'Windows':
            for char in text:
                self.input_character(char)
                if interval:
                    time.sleep(interval)
        elif self.system == 'Darwin':
            # macOS上使用ADB命令输入字符串
            if self.serial:
                try:
                    # 对于简单的ASCII字符串，可以一次输入
                    cmd = [self.adb_path, '-s', self.serial, 'shell', f'input text "{text}"']
                    subprocess.run(cmd, capture_output=True, text=True)
                except Exception as e:
                    # 如果一次输入失败，尝试逐字符输入
                    print(f"ADB一次输入字符串失败，尝试逐字符输入: {str(e)}")
                    for char in text:
                        self.input_character(char)
                        if interval:
                            time.sleep(interval)

if __name__ == "__main__":
    if system == 'Windows':
        hwnd = win32gui.FindWindow(None, "Game")
        print(f"窗口句柄: {hwnd}")
        kb = Keyboard(hwnd)
        kb.input_string('测试文本')
    elif system == 'Darwin':
        # macOS测试
        # 请确保模拟器已启动并连接
        serial = "127.0.0.1:16384"  # 示例ADB设备序列号
        adb_path = "adb"  # 假设adb在PATH中
        kb = Keyboard(serial=serial, adb_path=adb_path)
        kb.input_string('测试文本')
        kb.key_push('enter')
