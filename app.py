import tkinter as tk
from tkinter import messagebox
import tkinter.messagebox as mbox
import subprocess
import os
import sys
from PIL import Image, ImageTk
import winreg
import ctypes

# 检测 Python 是否已安装


def is_python_installed():
    try:
        # 尝试调用 python --version
        subprocess.run(["python", "--version"], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# 检测运行库是否已安装（根据你的脚本执行后的结果判断）
def is_dependencies_installed():
    # 假设依赖安装后会在当前目录生成一个标记文件 installed_deps.flag
    flag_file = os.path.join(os.getcwd(), "installed_deps.flag")
    return os.path.exists(flag_file)


# 检测证书是否已安装（可以简单判断注册表中是否存在对应证书）
def is_certificate_installed():
    try:
        certutil_output = subprocess.run(
            ["certutil", "-user", "-viewstore", "-p", "mitmproxy", "Root"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return "mitmproxy" in certutil_output.stdout
    except subprocess.CalledProcessError:
        return False


class InstallButton:
    def __init__(self, parent, text, command, status_check_func, install_name):
        self.parent = parent
        self.text = text
        self.command = command
        self.status_check_func = status_check_func
        self.install_name = install_name

        self.is_installed = self.status_check_func()

        # 显示带勾选标记的文本（如果已安装）
        display_text = f"{self.text}  ✔" if self.is_installed else self.text

        self.button = tk.Button(parent, text=display_text, width=25,
                                command=self.on_click, anchor="w", justify="left")

    def pack(self, **kwargs):
        self.button.pack(**kwargs)

    def on_click(self):
        if self.is_installed:
            result = mbox.askyesno("提示", f"{self.install_name} 已存在，是否继续安装？")
            if result:
                self.command()
        else:
            self.command()

# 检查文件是否存在


def check_file_exists(file_path, file_type):
    if not os.path.exists(file_path):
        messagebox.showerror("错误", f"{file_type} 文件不存在，请确认路径是否正确。")
        return False
    return True


# 安装 Python
def install_python():
    python_installer = os.path.join(os.getcwd(), "python-3.12.5-amd64.exe")
    if check_file_exists(python_installer, "Python 安装包"):
        subprocess.Popen([python_installer], shell=True)


# 安装运行库
def install_dependencies():
    cmd_script = os.path.join(os.getcwd(), "下载运行库.cmd")
    if check_file_exists(cmd_script, "运行库安装脚本"):
        subprocess.Popen(
            ["cmd.exe", "/k", cmd_script],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )


# 安装证书到“受信任的根证书颁发机构”
def install_certificate():
    cert_path = resource_path("mitmproxy-ca-cert.p12")  # 使用 resource_path
    if not check_file_exists(cert_path, "证书文件"):
        return

    try:
        subprocess.run([
            "certutil", "-user", "-importPFX", "-p", "mitmproxy", cert_path, "Root"
        ], check=True)
        messagebox.showinfo("成功", "证书已成功安装到受信任的根证书颁发机构！")
    except Exception as e:
        messagebox.showerror("错误", f"安装证书失败: {e} ， 请自己手动按文档安装证书文件")


# 运行抓包程序
def run_proxy():
    proxy_script = os.path.join(os.getcwd(), "运行抓包程序.cmd")
    if check_file_exists(proxy_script, "抓包程序脚本"):
        subprocess.Popen(
            ["cmd.exe", "/k", proxy_script],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )


# 开始下载表情包
def start_download():
    download_script = os.path.join(os.getcwd(), "运行下载程序.cmd")
    if check_file_exists(download_script, "表情包下载脚本"):
        subprocess.Popen(
            ["cmd.exe", "/k", download_script],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )


# 创建主窗口
def create_gui():
    window = tk.Tk()
    window.title("抖音表情包抓取工具")
    window.geometry("400x300")

    icon_path = resource_path("favicon.ico")
    if os.path.exists(icon_path):
        window.iconbitmap(icon_path)

    # 设置背景图片
    bg_image_path = resource_path("bg.png")  # 支持 jpg/png 格式
    if os.path.exists(bg_image_path):
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((400, 300), Image.LANCZOS)  # 调整尺寸与窗口一致
        bg_photo = ImageTk.PhotoImage(bg_image)

        # 使用 Label 显示背景图
        bg_label = tk.Label(window, image=bg_photo)
        bg_label.image = bg_photo  # 防止被垃圾回收
        bg_label.place(relwidth=1, relheight=1)  # 填满整个窗口
    else:
        tk.Label(window, text="抖音表情包抓取工具", font=("Arial", 16)).pack(pady=10)

    # 按钮容器（透明背景）
    button_frame = tk.Frame(window, bg='')  # 使用空字符串保持透明
    button_frame.pack(pady=50)

    python_button = InstallButton(
        button_frame,
        text="安装 Python",
        command=install_python,
        status_check_func=is_python_installed,
        install_name="Python"
    ).pack(pady=5)

    dependencies_button = InstallButton(
        button_frame,
        text="安装运行库",
        command=install_dependencies,
        status_check_func=is_dependencies_installed,
        install_name="运行库"
    ).pack(pady=5)

    certificate_button = InstallButton(
        button_frame,
        text="安装证书",
        command=install_certificate,
        status_check_func=is_certificate_installed,
        install_name="MITMProxy 证书"
    ).pack(pady=5)

    InstallButton(
        button_frame,
        text="运行抓包程序",
        command=run_proxy,
        status_check_func=lambda: False,
        install_name=""
    ).pack(pady=5)

    InstallButton(
        button_frame,
        text="开始下载表情包",
        command=start_download,
        status_check_func=lambda: False,
        install_name=""
    ).pack(pady=5)

    # 定时刷新按钮状态
    def refresh_buttons():
        try:
            for btn in [python_button, dependencies_button, certificate_button]:
                try:
                    new_status = btn.status_check_func()
                    if new_status != btn.is_installed:
                        btn.is_installed = new_status
                        btn.button.config(
                            text=f"{btn.text}  ✔" if new_status else btn.text)
                except Exception as e:
                    print(f"状态检测失败: {btn.text}, 错误: {e}")
                    # 可以选择跳过该按钮继续刷新其他按钮
                    continue
            window.after(3000, refresh_buttons)
        except Exception as e:
            print("刷新按钮时发生严重错误:", e)
            window.after(5000, refresh_buttons)  # 出错后稍晚再试

    window.mainloop()


def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发环境和 PyInstaller 打包后的环境 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    create_gui()
