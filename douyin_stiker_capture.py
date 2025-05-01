import os
import json
import logging
import winreg
from mitmproxy import http
import sys

# 配置日志
LOG_DIR = os.path.expanduser("~/.douyin_sticker_capture/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 配置部分
IMAGE_TYPES = ('jpeg', 'jpg', 'png', 'gif', 'webp')
LINK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "link.json")
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080


def ensure_file_exists():
    """确保保存链接的文件存在并初始化为空列表"""
    if not os.path.exists(LINK_FILE):
        with open(LINK_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)


def save_link_to_file(url):
    """将链接保存到link.json文件中"""
    try:
        with open(LINK_FILE, 'r', encoding='utf-8') as f:
            links = json.load(f)
        links.append(url)
        with open(LINK_FILE, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=4)
        logger.info(f"链接已保存: {url}")
    except Exception as e:
        logger.error(f"保存链接失败: {str(e)}")


def set_system_proxy(enable=True):
    """配置系统代理"""
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{PROXY_HOST}:{PROXY_PORT}")
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
        winreg.CloseKey(key)
        winreg.CloseKey(reg)
        logger.info(f"系统代理已{'启用' if enable else '禁用'}: {PROXY_HOST}:{PROXY_PORT}")
    except Exception as e:
        logger.error(f"配置系统代理失败: {str(e)}")
        raise


def response(flow: http.HTTPFlow):
    """拦截响应"""
    content_type = flow.response.headers.get('Content-Type', '').lower()
    if any(img_type in content_type for img_type in IMAGE_TYPES):
        url = flow.request.url
        logger.info(f"发现图片资源: {url}")
        save_link_to_file(url)
    else:
        logger.info(f"非图片资源: {flow.request.url}")


def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理函数"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("程序发生未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))


def main():
    """主程序入口"""
    print("""
抖音表情包抓取程序v1.1 By.Mete0r (修改版)

使用说明:
1. 确保已安装Python和mitmproxy (pip install mitmproxy)
2. 程序会自动配置系统代理为: 127.0.0.1:8080
3. 在电脑上打开抖音客户端或网页版
4. 程序会记录所有发现的图片链接并保存到当前目录下的link.json文件

按Ctrl+C停止程序
""")
    print("启动程序...")
    ensure_file_exists()
    set_system_proxy(enable=True)
    from mitmproxy.tools.main import mitmdump
    mitmdump(['-s', __file__])
    input("按 Enter 键退出...")


if __name__ == "__main__":
    sys.excepthook = handle_exception
    try:
        main()
    finally:
        set_system_proxy(enable=False)