import subprocess
import sys
import time
import os
import re
import signal

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_progress(line):
    # 修改正则表达式以更准确地匹配日志格式
    pattern = r'.*?(\d+)%.*?(\d+(?:\.\d+)?)\s*(MB|GB)/\s*(\d+(?:\.\d+)?)\s*(GB)\s*([\d.]+)\s*([KMG]B)/s'
    match = re.search(pattern, line)
    if match:
        percentage = match.group(1)
        downloaded = float(match.group(2))
        downloaded_unit = match.group(3)
        total = float(match.group(4))
        total_unit = match.group(5)
        speed_value = float(match.group(6))
        speed_unit = match.group(7)
        speed_unit = re.sub(r'/s+$', '', speed_unit).strip()
        
        # 转换下载大小为MB
        if downloaded_unit == 'GB':
            downloaded_mb = downloaded * 1024
        else:
            downloaded_mb = downloaded
            
        # 转换总大小为MB
        total_mb = total * 1024  # GB to MB
        
        # 统一速度单位为MB/s
        if 'KB' in speed_unit:
            speed_mb = speed_value / 1024
        elif 'GB' in speed_unit:
            speed_mb = speed_value * 1024
        else:
            speed_mb = speed_value
            
        return {
            'percentage': percentage,
            'downloaded': f"{downloaded_mb:.1f} MB",
            'total': f"{total_mb:.1f} MB",
            'speed': f"{speed_value} {speed_unit}/s",
            'speed_mb': speed_mb
        }
    return None

def show_progress(line):
    try:
        line = line.strip()
        if not line:
            return None

        if 'pulling' in line.lower():  # 使用小写比较
            if 'manifest' not in line.lower():  # 只有不包含manifest的pulling日志才打印
                sys.stdout.flush()
            progress_info = parse_progress(line)
            if progress_info:
                progress_str = (
                    f"\r下载进度: {progress_info['percentage']}% "
                    f"({progress_info['downloaded']}/{progress_info['total']}) "
                    f"速度: {progress_info['speed']}"
                )
                print(progress_str, end='')
                sys.stdout.flush()
            return progress_info
    except Exception as e:
        print(f"\r处理进度信息时出错: {str(e)}", end='')
        sys.stdout.flush()
    return None

def extract_model_name(input_text):
    """从用户输入中提取模型名称"""
    # 匹配 "ollama run/pull 模型名" 格式
    match = re.search(r'ollama\s+(run|pull)\s+([^\s]+)', input_text)
    if match:
        return match.group(2)  # 返回模型名称部分
    
    # 如果不是完整命令，则假设输入的就是模型名称
    return input_text.strip()

def pull_model(model_name):
    print(f"开始下载模型: {model_name}")
    
    # 检查ollama是否已安装
    try:
        subprocess.run(['ollama', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误：未检测到ollama程序，请确保已安装ollama并添加到系统环境变量中。")
        input("按回车键退出...")
        return 1
        
    while True:  # 持续尝试下载，直到成功
        try:
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )

            low_speed_count = 0  # 用于记录低速度的持续次数
            last_check_time = time.time()

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                progress_info = show_progress(line)
                
                if progress_info:
                    # 检查速度是否低于3MB/s
                    current_time = time.time()
                    if current_time - last_check_time >= 30:  # 每30秒检查一次
                        last_check_time = current_time
                        if progress_info['speed_mb'] < 3.0:
                            low_speed_count += 1
                            print(f"\n当前速度 {progress_info['speed_mb']:.2f} MB/s 低于3MB/s!")
                            if low_speed_count >= 1:  # 如果速度持续低于阈值
                                print("\n速度持续低于3MB/s，正在重新启动下载...")
                                # 在Windows上使用taskkill强制结束进程
                                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                            stdout=subprocess.DEVNULL, 
                                            stderr=subprocess.DEVNULL)
                                time.sleep(2)  # 等待进程完全结束
                                break
                        else:
                            low_speed_count = 0

                # 检查进程是否还在运行
                if process.poll() is not None:
                    break

            # 如果进程正常结束（不是因为低速度被终止）
            if process.poll() == 0:
                print(f"\n下载完成！")
                return 0
            elif low_speed_count >= 1:
                print("正在重新尝试下载...")
                continue
            else:
                print(f"\n下载异常终止，返回码: {process.poll()}")
                return 1

        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            retry = input("是否重试？(y/n): ")
            if retry.lower() != 'y':
                return 1
            print("正在重新尝试下载...")

def main():
    clear_console()
    try:
        user_input = input("请输入需要下载的模型名称: ")
        model_name = extract_model_name(user_input)
        print(f"将下载模型: {model_name}")
        return_code = pull_model(model_name)
        
        if return_code == 0:
            print("模型下载成功！")
        else:
            print("模型下载失败！")
        
        input("按回车键退出...") # 添加这行以防止程序立即关闭
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        input("按回车键退出...")

if __name__ == "__main__":
    main()