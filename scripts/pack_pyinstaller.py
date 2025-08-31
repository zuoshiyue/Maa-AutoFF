import os
import subprocess
import sys
import shutil

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
    
    # --- 构建打包命令字符串 ---
    cmd_str = (
        f'pyinstaller --noconfirm --onedir --windowed '
        f'--distpath {output_dir} '
        f'--name {output_exe_name[:-4]} '  # PyInstaller uses name without .exe
        f'--add-data "frontend/dist;frontend/dist" '
        f'--add-data "res;res" '
        f'{main_script}'
    )
    
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
            print("="*50)
        else:
            print("\n" + "="*50)
            print("打包失败：未找到生成的exe文件")
            print(f"期望文件路径: {os.path.abspath(output_file_path)}")
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