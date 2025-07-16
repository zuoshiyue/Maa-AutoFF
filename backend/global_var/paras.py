"""
全局变量模块，用于集中管理系统中的全局变量和API实例
便于其他模块直接导入使用
"""
import logging

# 配置日志
logger = logging.getLogger(__name__)
logger.info("初始化全局变量模块")

# 系统设置
sys_settings = {  
    'mumuPath': '',             # 模拟器路径
    'log_retention_count': 300, # 日志清空数
    'screenshot_fps': 15,       # 截图频率
}   

# 连接的模拟器信息
emulator_info = {
    'name': None,
    'index': 1,
    'adb_port': '127.0.0.1:0000',
    'state': False
}

# 模拟器API类变量
emulator_api = {
    'cap': None,  # 截图对象
    'mouse': None,  # 鼠标对象
    'keyboard': None,  # 键盘对象
    'yolo': None,  # YOLO对象
    'ocr': None  # OCR对象
}

# 采集列表
gathering_items = {
    # 物品名称: {
        # 'need': 99, # 需要数量
        # 'complete': 0, # 完成数量
        # 'num_per_min': 10, # 每分钟采集数量
    #},
}

fish_settings = {
    'need_repair': False,     # 是否需要修理
    'need_submit': False,     # 是否需要提交收藏品
    'small_to_big': False,    # 是否以小钓大
}

over = 1753111482