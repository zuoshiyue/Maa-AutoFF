import os
import subprocess
import sys
import shutil

# 设置标准输出编码为UTF-8，防止Windows环境下打印中文字符时出现编码错误
sys.stdout.reconfigure(encoding='utf-8')

# 在GitHub Actions中通过环境变量控制GCC下载行为
os.environ['NUITKA_DOWNLOAD_GCC'] = 'yes'

# 将Nuitka下载的GCC路径添加到PATH环境变量中
nuitka_gcc_path = os.path.join(os.environ['LOCALAPPDATA'], 'Nuitka', 'Nuitka', 'Cache', 'downloads', 'gcc', 'x86_64', '13.2.0-16.0.6-11.0.1-msvcrt-r1', 'mingw64', 'bin')
os.environ['PATH'] = nuitka_gcc_path + ';' + os.environ['PATH']

# 在GitHub Actions中设置正确的GCC路径
if 'GITHUB_ACTIONS' in os.environ:
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
    
    # --- 构建打包命令字符串 (使用与成功命令行相同的格式) ---
    cmd_str = (
        # f'nuitka --mingw64 --standalone --show-progress '
        f'nuitka --mingw64 --standalone --show-progress --windows-disable-console '
        f'--output-dir={output_dir} '
        f'--output-filename={output_exe_name} '
        f'--include-data-dir=frontend/dist=frontend/dist '
        f'--include-data-dir=res=res '
        f'--include-data-dir={webview_js_path}=webview/js '
        f'--include-data-dir={rapidocr_models_path}=rapidocr/models '
        f'--include-data-file={rapidocr_config_path}=rapidocr/config.yaml '
        f'--include-data-file={rapidocr_default_models_path}=rapidocr/default_models.yaml '
        f'{main_script}'
    )
    
    print("\n" + "="*50)
    print("准备执行以下 Nuitka 打包命令:")
    print(cmd_str)
    print("="*50 + "\n")

    # --- 执行打包命令 ---
    try:
        # 直接使用 shell=True 执行完整的命令字符串，就像在命令行中直接输入那样
        result = subprocess.run(cmd_str, shell=True, check=True, text=True, encoding='utf-8', errors='replace')
        
        # 检查输出目录和exe文件是否存在
        output_file_path = os.path.join(output_dir, 'AutoFF.dist', output_exe_name)
        if os.path.exists(output_file_path):
            print("\n" + "="*50)
            print("打包成功！")
            print(f"输出文件位于: {os.path.abspath(output_file_path)}")
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
