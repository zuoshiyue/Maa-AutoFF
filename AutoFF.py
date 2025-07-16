import os
import sys
import webview
import threading
import time
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial
import socketserver

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器，支持指定静态文件目录"""
    # 显式定义MIME类型映射，修复在打包后可能出现的MIME类型错误
    # 特别是对于JS模块，需要确保 'application/javascript' 类型
    extensions_map = {
        '': 'application/octet-stream',
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.mjs': 'application/javascript',
        '.json': 'application/json',
        '.wasm': 'application/wasm',
        '.xml': 'application/xml',
        '.pdf': 'application/pdf',
        '.zip': 'application/zip',
        '.gz': 'application/gzip',
        '.tar': 'application/x-tar',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
        '.ttf': 'font/ttf',
        '.otf': 'font/otf',
    }
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        """重写日志方法，减少日志输出频率"""
        # 只记录错误和警告信息，减少日志输出
        if args[1].startswith('4') or args[1].startswith('5'):
            logger.warning(f"[HTTP] {self.address_string()} - {format%args}")
    
    def end_headers(self):
        """添加缓存控制头，提高静态资源加载效率"""
        # 针对不同类型的资源设置不同的缓存策略
        path = self.path.split('?')[0]
        if path.endswith(('.js', '.css')):
            self.send_header('Cache-Control', 'max-age=604800')  # 脚本和样式表缓存7天
        elif path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico')):
            self.send_header('Cache-Control', 'max-age=2592000')  # 图片缓存30天
        else:
            self.send_header('Cache-Control', 'max-age=3600')  # 其他资源缓存1小时
        
        # 添加性能优化相关的头
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Connection', 'keep-alive')
        super().end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """使用多线程处理HTTP请求"""
    daemon_threads = True
    # 增加队列大小提高并发处理能力
    request_queue_size = 10

class StaticServer:
    """静态文件服务器类"""
    def __init__(self, host='localhost', port=8000, directory=None):
        self.host = host
        self.port = port
        self.directory = directory
        self.server = None
        self.thread = None
    
    def start(self):
        """启动HTTP服务器"""
        try:
            # 创建HTTP服务器，使用自定义处理器指定静态文件目录
            handler = partial(CustomHTTPRequestHandler, directory=self.directory)
            # 使用多线程服务器提高并发性能
            self.server = ThreadedHTTPServer((self.host, self.port), handler)
            
            logger.info(f"启动HTTP服务器在 http://{self.host}:{self.port}")
            logger.info(f"静态文件目录: {self.directory}")
            
            # 在新线程中启动服务器
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            
            return f'http://{self.host}:{self.port}'
        except Exception as e:
            logger.error(f"启动HTTP服务器失败: {e}")
            raise
    
    def stop(self):
        """停止HTTP服务器"""
        if self.server:
            self.server.shutdown()
            logger.info("HTTP服务器已停止")

# JS脚本，用于检查页面加载状态
js_check_loaded = """
if (document.readyState === 'complete') {
    true;
} else {
    false;
}
"""

class Api:
    """API类，用于暴露给前端的接口"""
    def __init__(self):
        self.window = None
    
    def set_window(self, window):
        self.window = window
        # 设置settings_api的窗口引用
        from backend.ui_api.settings.api import settings_api
        settings_api.set_window(window)
    
    def get_app_info(self):
        """获取应用信息"""
        return {
            'version': '1.0.0',
            'platform': sys.platform,
            'cwd': os.getcwd()
        }

def main():
    """
    主函数：初始化窗口并显示网页
    """
    try:
        # 获取项目根目录路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"项目根目录: {base_dir}")
        
        # 获取dist目录的绝对路径
        dist_dir = os.path.join(base_dir, 'frontend', 'dist')
        logger.info(f"dist目录: {dist_dir}")
        
        # 检查dist目录是否存在
        if not os.path.exists(dist_dir):
            logger.error(f"dist目录不存在: {dist_dir}")
            logger.info("请确保已运行 npm run build")
            return
        
        # 预加载检查index.html和关键资源
        index_path = os.path.join(dist_dir, 'index.html')
        if not os.path.exists(index_path):
            logger.error(f"index.html不存在: {index_path}")
            return

        # 使用静态文件服务器加载构建好的应用
        server = StaticServer(port=8000, directory=dist_dir)
        base_url = server.start()
        
        # 加载Vue应用的index.html   
        url = f"{base_url}"  # 默认会加载index.html
        logger.info(f"启动pywebview窗口，加载Vue应用: {url}")
        
        # 创建API实例
        api = Api()
        
        # 创建窗口并展示
        window = webview.create_window(
            'AutoFF-0706.1', 
            url, 
            min_size=(1280, 720), 
            width=1280, 
            height=720,
            frameless=False,  # 设置为True可以创建无边框窗口
            easy_drag=True,   # 允许拖拽窗口
            text_select=True, # 允许文本选择
            zoomable=True,    # 允许缩放
            transparent=False,# 透明背景会消耗更多资源，设为False
            resizable=True,   # 允许调整大小
            on_top=False,     # 不需要总在最前
            background_color='#FFFFFF'  # 设置背景色
        )
        
        # 设置API的window引用
        api.set_window(window)
        
        # 暴露API函数
        window.expose(api.get_app_info)
        
        # 暴露设置API函数
        from backend.ui_api.settings.api import settings_api
        from backend.ui_api.settings.settings_manager import settings_manager
        
        # 确保设置文件存在
        if not os.path.exists(settings_manager.settings_file):
            logger.info("初次启动，创建默认设置文件")
            settings_manager.save_settings()
            
        window.expose(settings_api.get_all_settings)
        window.expose(settings_api.update_setting)
        window.expose(settings_api.update_settings)
        # 注册select_directory方法，允许传递validate_shell_folder参数
        window.expose(settings_api.select_directory)
        
        # 暴露日志API函数
        from backend.global_var import api as Gv_api
        Gv_api.logs_api.set_window(window)
        window.expose(Gv_api.logs_api.log)
        window.expose(Gv_api.logs_api.debug)
        window.expose(Gv_api.logs_api.info)
        window.expose(Gv_api.logs_api.warning)
        window.expose(Gv_api.logs_api.error)
        window.expose(Gv_api.logs_api.critical)
        window.expose(Gv_api.logs_api.get_logs)
        window.expose(Gv_api.logs_api.clear_logs)
        window.expose(Gv_api.logs_api.setup_logging_redirect)
        
        # 暴露提示信息API函数
        Gv_api.tips_api.set_window(window)
        window.expose(Gv_api.tips_api.show_tip)
        window.expose(Gv_api.tips_api.info)
        window.expose(Gv_api.tips_api.success)
        window.expose(Gv_api.tips_api.warning)
        window.expose(Gv_api.tips_api.error)
        window.expose(Gv_api.tips_api.confirm)
        
        # 暴露采集API函数
        gathering_api = Gv_api.gathering_api
        gathering_api.set_window(window)
        window.expose(gathering_api.toggle_gathering)
        window.expose(gathering_api.start_gathering)
        window.expose(gathering_api.stop_gathering)
        window.expose(gathering_api.get_gathering_status)
        window.expose(gathering_api.get_gathering_items)
        window.expose(gathering_api.update_gathering_items)
        window.expose(gathering_api.get_gathering_progress)
        
        # 暴露钓鱼API函数
        fishing_api = Gv_api.fishing_api
        fishing_api.set_window(window)
        window.expose(fishing_api.toggle_fishing)
        window.expose(fishing_api.start_fishing)
        window.expose(fishing_api.stop_fishing)
        window.expose(fishing_api.get_fishing_status)
        window.expose(fishing_api.get_fishing_settings)
        window.expose(fishing_api.update_fishing_setting)
        
        # 暴露金碟游乐场API函数
        goldsaucer_api = Gv_api.goldsaucer_api
        goldsaucer_api.set_window(window)
        window.expose(goldsaucer_api.toggle_mog_catch)
        window.expose(goldsaucer_api.start_mog_catch)
        window.expose(goldsaucer_api.stop_mog_catch)
        window.expose(goldsaucer_api.get_goldsaucer_status)
        
        # 暴露主页API函数（模拟器连接相关）
        home_api = Gv_api.home_api
        home_api.set_window(window)
        window.expose(home_api.get_emulator_status)
        window.expose(home_api.get_emulator_list)
        window.expose(home_api.connect_emulator)
        
        # 启动前的预热处理
        def on_loaded():
            logger.info("页面已加载，开始预热应用...")
            # 等待页面完全加载
            timeout = 10  # 10秒超时
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if window.evaluate_js(js_check_loaded):
                    logger.info("页面加载完成")
                    break
                time.sleep(0.1)
            
            # 页面加载完成后，设置日志重定向
            try:
                # 延迟1秒后再设置日志重定向，确保前端已准备好接收日志
                time.sleep(1)
                Gv_api.logs_api.setup_logging_redirect("INFO")
            except Exception as e:
                logger.error(f"设置日志重定向失败: {e}")
                
            logger.info("应用启动完成")
        
        # 在新线程中执行预热以避免阻塞主UI线程
        threading.Thread(target=on_loaded, daemon=True).start()
        
        # 设置调试模式（生产环境关闭debug模式）
        webview.start(debug=False, gui='default', localization={})
        
    except Exception as e:
        logger.error(f"程序出错: {e}")
        raise

if __name__ == '__main__':
    main()
