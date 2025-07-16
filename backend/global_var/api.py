"""
全局变量模块，用于集中管理系统中的全局变量和API实例
便于其他模块直接导入使用
"""
import logging

# 导入API类
from ..ui_api.logs.tips import TipsAPI
from ..ui_api.logs.logs import LogsAPI
from ..ui_api.gathering.api import GatheringApi
from ..ui_api.fishing.api import FishingApi
from ..ui_api.home import HomeAPI
from ..ui_api.goldsaucer.api import GoldSaucerApi


# 配置日志
logger = logging.getLogger(__name__)
logger.info("初始化全局变量模块")

# 创建UI_API实例
tips_api = TipsAPI()
logs_api = LogsAPI()
gathering_api = GatheringApi()
fishing_api = FishingApi()
home_api = HomeAPI()
goldsaucer_api = GoldSaucerApi()

