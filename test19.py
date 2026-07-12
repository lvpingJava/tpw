import os

# 使用cmd的rmdir命令（注意：rmdir只能删除空文件夹）
#os.system(f'rmdir /s /q "path/to/directory"')  # 注意：/s 递归删除，/q 安静模式

# 或者使用PowerShell
#os.system(f'powershell -Command "Remove-Item -Recurse -Force \\"""')

import subprocess


def find_and_kill_process_by_file(file_path):
    # 构造PowerShell命令
    ps_command = f"""  
    Get-Process | Where-Object {{  
        $_.Modules.FileName -like '*{os.path.basename(file_path)}*'  
    }} | Stop-Process -Force  
    """
    print(ps_command)
    # 执行PowerShell命令
    try:
        subprocess.run(["powershell", "-Command", ps_command], check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
        print(f"Processes using {file_path} have been killed.")
    except subprocess.CalledProcessError as e:
        print(f"Error killing processes using {file_path}: {e.stderr}")

    # 示例使用


file_path = "I:\\tpw2\\tpw6.1.9\\notepad.exe"  # 替换为你的文件路径
find_and_kill_process_by_file(file_path)