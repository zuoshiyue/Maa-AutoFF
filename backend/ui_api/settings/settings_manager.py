"""
设置管理器模块，用于处理用户设置的加载、保存和更新
"""
import os
import json
import logging
from pathlib import Path
import sys
from importlib import import_module

# 添加项目根目录到系统路径，确保可以导入backend模块
root_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# 导入全局变量模块
from backend.global_var import paras as Gv_paras

# 配置日志
logger = logging.getLogger(__name__)

class SettingsManager:
    """
    设置管理器类，负责处理用户设置的加载、保存和更新
    """
    def __init__(self):
        """初始化设置管理器"""
        # 获取项目根目录
        self.root_dir = root_dir
        # 设置文件路径
        self.user_dir = self.root_dir / "user"
        self.settings_file = self.user_dir / "settings.json"
        
        # 默认设置
        self.default_settings = {
            "mumuPath": "",
            "logRetentionCount": 300,
            "screenshotFps": 15
        }
        
        # 当前设置
        self.settings = self.load_settings()
        
        # 初始化时同步设置到Global_var
        self._sync_to_global_var()
    
    def ensure_user_dir(self):
        """确保用户目录存在"""
        if not self.user_dir.exists():
            try:
                self.user_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建用户目录: {self.user_dir}")
            except Exception as e:
                logger.error(f"创建用户目录失败: {e}")
                return False
        return True
    
    def load_settings(self):
        """加载设置，如果文件不存在则使用默认设置"""
        if not self.ensure_user_dir():
            return self.default_settings.copy()
            
        if not self.settings_file.exists():
            logger.info(f"设置文件不存在，使用默认设置")
            return self.default_settings.copy()
            
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                logger.info(f"成功加载设置文件: {self.settings_file}")
                
                # 确保所有默认设置项都存在
                for key, value in self.default_settings.items():
                    if key not in settings:
                        settings[key] = value
                        
                return settings
        except Exception as e:
            logger.error(f"加载设置文件失败: {e}")
            return self.default_settings.copy()
    
    def save_settings(self):
        """保存当前设置到文件"""
        if not self.ensure_user_dir():
            logger.error("无法保存设置：用户目录创建失败")
            return False
            
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                logger.info(f"成功保存设置到文件: {self.settings_file}")
            
            # 同步设置到Global_var
            self._sync_to_global_var()
            return True
        except Exception as e:
            logger.error(f"保存设置文件失败: {e}")
            return False
    
    def _sync_to_global_var(self):
        """同步设置到Gv_paras.sys_settings"""
        try:
            # 映射设置键名到Gv_paras.sys_settings中的键名
            mapping = {
                "mumuPath": "mumuPath",
                "logRetentionCount": "log_retention_count",
                "screenshotFps": "screenshot_fps"
            }
            
            for settings_key, global_key in mapping.items():
                if settings_key in self.settings:
                    Gv_paras.sys_settings[global_key] = self.settings[settings_key]
                    
            logger.info("成功同步设置到Gv_paras.sys_settings")
        except Exception as e:
            logger.error(f"同步设置到Gv_paras失败: {e}")
    
    def get_settings(self):
        """获取当前所有设置"""
        return self.settings
    
    def update_setting(self, key, value):
        """更新单个设置项并保存"""
        if key in self.settings:
            self.settings[key] = value
            logger.info(f"更新设置 {key}: {value}")
            result = self.save_settings()
            return result
        else:
            logger.warning(f"尝试更新未知设置项: {key}")
            return False
    
    def update_settings(self, settings_dict):
        """批量更新多个设置项并保存"""
        updated = False
        for key, value in settings_dict.items():
            if key in self.settings:
                self.settings[key] = value
                updated = True
                logger.info(f"更新设置 {key}: {value}")
            else:
                logger.warning(f"尝试更新未知设置项: {key}")
        
        if updated:
            return self.save_settings()
        return False

# 创建全局设置管理器实例
settings_manager = SettingsManager() 