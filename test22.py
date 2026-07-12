import subprocess
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # 请求管理员权限
    script = sys.argv[0]
    if " " in script:
        script = f'"{script}"'  # 路径含空格时添加引号
    print(f"ss:{script}")
    # 请求管理员权限并重新启动脚本
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, script, None, 1
    )
    sys.exit()
    #sys.exit()
process_name = "躺平王服务端.exe"  # 注意检查名称是否包含空格或特殊符号
matp_name = "matp.exe"  # 注意检查名称是否包含空格或特殊符号

try:
    print("开始命令执行成功")
    subprocess.run(
        ["taskkill", "/F", "/IM", matp_name],
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="gbk"  # Windows 中文系统默认编码为 GBK
    )
    print("命令执行成功")
except subprocess.CalledProcessError as e:
    # 使用 GBK 编码解码错误信息
    error_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode("gbk", errors="replace")
    print(f"命令执行失败：{error_msg}")
    print(f"详细原因：可能是进程不存在，或没有权限终止进程")
except Exception as e:
    print(f"其他错误：{str(e)}")


try:
    print("开始命令执行成功")
    subprocess.run(
        ["taskkill", "/F", "/IM", process_name],
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="gbk"  # Windows 中文系统默认编码为 GBK
    )
    print("命令执行成功")
except subprocess.CalledProcessError as e:
    # 使用 GBK 编码解码错误信息
    error_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode("gbk", errors="replace")
    print(f"命令执行失败：{error_msg}")
    print(f"详细原因：可能是进程不存在，或没有权限终止进程")
except Exception as e:
    print(f"其他错误：{str(e)}")