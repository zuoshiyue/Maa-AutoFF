import os
import subprocess
import sys
import shutil
import os

# 设置标准输出编码为UTF-8，防止Windows环境下打印中文字符时出现编码错误
sys.stdout.reconfigure(encoding='utf-8')

# 在GitHub Actions中通过环境变量控制GCC下载行为
if 'GITHUB_ACTIONS' in os.environ:
    os.environ['NUITKA_DOWNLOAD_GCC'] = 'yes'
    
    # 改进的GCC路径查找逻辑，避免硬编码版本号
    try:
        # 尝试动态查找GCC路径
        import glob
        cache_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Nuitka', 'Nuitka', 'Cache', 'downloads', 'gcc', 'x86_64')
        if os.path.exists(cache_dir):
            gcc_versions = glob.glob(os.path.join(cache_dir, '*'))
            if gcc_versions:
                # 使用最新版本的GCC
                gcc_version = max(gcc_versions)
                nuitka_gcc_path = os.path.join(gcc_version, 'mingw64', 'bin')
                if os.path.exists(nuitka_gcc_path):
                    os.environ['PATH'] = nuitka_gcc_path + ';' + os.environ['PATH']
                    os.environ['CC'] = os.path.join(nuitka_gcc_path, 'gcc.exe')
                    os.environ['CXX'] = os.path.join(nuitka_gcc_path, 'g++.exe')
                    print(f"已设置GCC路径: {nuitka_gcc_path}")
    except Exception as e:
        print(f"动态设置GCC路径时出错: {e}")
        # 保留备用的硬编码路径作为回退
        nuitka_gcc_path = os.path.join(os.environ['LOCALAPPDATA'], 'Nuitka', 'Nuitka', 'Cache', 'downloads', 'gcc', 'x86_64', '13.2.0-16.0.6-11.0.1-msvcrt-r1', 'mingw64', 'bin')
        os.environ['PATH'] = nuitka_gcc_path + ';' + os.environ['PATH']
        os.environ['CC'] = os.path.join(nuitka_gcc_path, 'gcc.exe')
        os.environ['CXX'] = os.path.join(nuitka_gcc_path, 'g++.exe')

def main():
    """
    使用 Nuitka 打包项目的主函数。
    """
    # --- 配置 ---    
    main_script = 'AutoFF.py'
    output_dir = 'out'
    output_exe_name = 'AutoFF.exe'
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # --- 动态查找依赖包路径 ---    
    print("正在查找依赖包路径...")
    try:
        import webview
        import rapidocr
        
        webview_path = os.path.dirname(webview.__file__)
        rapidocr_path = os.path.dirname(rapidocr.__file__)
        print(f"找到 webview 路径: {webview_path}")
        print(f"找到 rapidocr 路径: {rapidocr_path}")
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保 'pywebview' 和 'rapidocr' 已经安装在当前 Python 环境中。")
        sys.exit(1)
    
    webview_js_path = os.path.join(webview_path, 'js')
    rapidocr_config_path = os.path.join(rapidocr_path, 'config.yaml')
    rapidocr_default_models_path = os.path.join(rapidocr_path, 'default_models.yaml')
    rapidocr_models_path = os.path.join(rapidocr_path, 'models')
    
    # 确保前端构建已完成
    frontend_dist_path = os.path.join('frontend', 'dist')
    if not os.path.exists(frontend_dist_path):
        print(f"错误: 前端构建目录 {frontend_dist_path} 不存在，请先运行 'npm run build' 构建前端。")
        sys.exit(1)
    
    # 确保资源目录存在
    res_path = 'res'
    if not os.path.exists(res_path):
        print(f"警告: 资源目录 {res_path} 不存在，将创建空目录。")
        os.makedirs(res_path)
    
    # --- 构建打包命令字符串 ---    
    cmd_str = (
        f'nuitka --mingw64 --standalone --show-progress '  # 移除 --windows-disable-console 以方便调试
        f'--output-dir={output_dir} ' 
        f'--output-filename={output_exe_name} ' 
        f'--include-data-dir={frontend_dist_path}=frontend/dist ' 
        f'--include-data-dir={res_path}=res ' 
        f'--include-data-dir={webview_js_path}=webview/js ' 
        f'--include-data-dir={rapidocr_models_path}=rapidocr/models ' 
        f'--include-data-file={rapidocr_config_path}=rapidocr/config.yaml ' 
        f'--include-data-file={rapidocr_default_models_path}=rapidocr/default_models.yaml ' 
        f'--enable-plugin=multiprocessing '  # 添加多进程支持
        f'--follow-imports '  # 自动跟踪导入
        f'--nofollow-import-to=numpy,onnxruntime,opencv_python '  # 这些包通常有自己的二进制文件处理方式
    )
    
    # 检查图标文件是否存在，如果存在则添加
    icon_path = os.path.join('res', 'icon.ico')
    if os.path.exists(icon_path):
        cmd_str += f' --windows-icon-from-ico={icon_path} '
    else:
        print(f"警告: 图标文件 {icon_path} 不存在，将使用默认图标。")
    
    # 添加主脚本
    cmd_str += f' {main_script}'
    
    print("\n" + "="*50)
    print("准备执行以下 Nuitka 打包命令:")
    print(cmd_str)
    print("="*50 + "\n")
    
    # --- 执行打包命令 ---    
    try:
        # 直接使用 shell=True 执行完整的命令字符串
        result = subprocess.run(cmd_str, shell=True, check=True, text=True, encoding='utf-8', errors='replace')
        
        # 检查输出目录和exe文件是否存在
        output_dist_dir = os.path.join(output_dir, 'AutoFF.dist')
        output_file_path = os.path.join(output_dist_dir, output_exe_name)
        
        if os.path.exists(output_file_path):
            print("\n" + "="*50)
            print("打包成功！")
            print(f"输出文件位于: {os.path.abspath(output_file_path)}")
            
            # 验证打包内容
            print("\n打包内容验证:")
            print(f"- 前端文件: {'存在' if os.path.exists(os.path.join(output_dist_dir, 'frontend', 'dist', 'index.html')) else '缺失'}")
            print(f"- Webview JS: {'存在' if os.path.exists(os.path.join(output_dist_dir, 'webview', 'js')) else '缺失'}")
            print(f"- RapidOCR 模型: {'存在' if os.path.exists(os.path.join(output_dist_dir, 'rapidocr', 'models')) else '缺失'}")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("打包失败：未找到生成的exe文件")
            print(f"期望文件路径: {os.path.abspath(output_file_path)}")
            print("="*50)
            sys.exit(1)
    
    except FileNotFoundError:
        print("\n错误: 'nuitka' 命令未找到。")
        print("请确保 Nuitka 已经通过 'pip install nuitka' 安装，并且 Python 的 Scripts 目录已添加到系统的 PATH 环境变量中。")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("\n" + "="*50)
        print(f"打包失败，退出代码: {e.returncode}")
        print("请检查上面的日志输出以获取详细错误信息。")
        print("="*50)
        sys.exit(1)
    except Exception as e:
        print(f"\n执行打包命令时发生未知错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
