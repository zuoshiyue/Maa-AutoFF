import os
import subprocess
import sys
import shutil
import os

# 设置标准输出编码为UTF-8，防止Windows环境下打印中文字符时出现编码错误
sys.stdout.reconfigure(encoding='utf-8')

def main():
    """
    使用 PyInstaller 打包项目的主函数。
    """
    # --- 配置 ---
    main_script = 'AutoFF.py'
    output_dir = 'out'
    output_exe_name = 'AutoFF.exe'
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
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
        # 创建bin子目录
        if not os.path.exists(os.path.join(res_path, 'bin')):
            os.makedirs(os.path.join(res_path, 'bin'))
    
    # --- 构建打包命令字符串 ---    
    # 基础PyInstaller命令
    cmd_str = (
        f'pyinstaller --noconfirm --onefile --windowed '  # 使用--windowed以隐藏控制台
        f'--distpath {output_dir} ' 
        f'--name {output_exe_name[:-4]} '  # PyInstaller uses name without .exe
    )
    
    # 添加数据文件
    cmd_str += (
        f'--add-data "{frontend_dist_path};frontend/dist" ' 
        f'--add-data "{res_path};res" ' 
        f'--add-data "{webview_js_path};webview/js" ' 
        f'--add-data "{rapidocr_models_path};rapidocr/models" ' 
        f'--add-data "{rapidocr_config_path};rapidocr" ' 
        f'--add-data "{rapidocr_default_models_path};rapidocr" ' 
    )
    
    # 检查图标文件是否存在，如果存在则添加
    icon_path = os.path.join('res', 'icon.ico')
    if os.path.exists(icon_path):
        cmd_str += f'--icon "{icon_path}" '
    else:
        print(f"警告: 图标文件 {icon_path} 不存在，将使用默认图标。")
    
    # 添加主脚本
    cmd_str += f'{main_script}'
    
    print("="*50)
    print("准备执行以下 PyInstaller 打包命令:")
    print(cmd_str)
    print("="*50 + "\n")
    
    # --- 执行打包命令 ---
    try:
        # 直接使用 shell=True 执行完整的命令字符串
        result = subprocess.run(cmd_str, shell=True, check=True, text=True, encoding='utf-8', errors='replace')
        
        # 检查输出目录和exe文件是否存在
        output_file_path = os.path.join(output_dir, output_exe_name)
        if os.path.exists(output_file_path):
            print("\n" + "="*50)
            print("打包成功！")
            print(f"输出文件位于: {os.path.abspath(output_file_path)}")
            
            # 显示文件大小信息
            file_size = os.path.getsize(output_file_path) / (1024 * 1024)  # MB
            print(f"打包文件大小: {file_size:.2f} MB")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("打包失败：未找到生成的exe文件")
            print(f"期望文件路径: {os.path.abspath(output_file_path)}")
            # 列出dist目录内容以帮助调试
            if os.path.exists(output_dir):
                print(f"\n{output_dir}目录内容:")
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        print(os.path.join(root, file))
            print("="*50)
            sys.exit(1)
            
    except FileNotFoundError:
        print("\n错误: 'pyinstaller' 命令未找到。")
        print("请确保 PyInstaller 已经通过 'pip install pyinstaller' 安装，并且 Python 的 Scripts 目录已添加到系统的 PATH 环境变量中。")
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