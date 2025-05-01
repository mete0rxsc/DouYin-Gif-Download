import os
import json
import requests

# 根据 Content-Type 获取文件扩展名
def get_file_extension_from_content_type(content_type):
    extension_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
        "image/svg+xml": ".svg",
    }
    return extension_map.get(content_type, ".unknown")  # 如果无法识别，使用 .unknown

# 读取 JSON 文件中的链接
def read_links_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        links = json.load(file)
    return links

# 下载文件到指定目录
def download_files(links, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)  # 如果文件夹不存在，则创建

    for i, link in enumerate(links):
        try:
            response = requests.get(link, stream=True)
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                file_extension = get_file_extension_from_content_type(content_type)
                file_name = f"file_{i}{file_extension}"  # 自定义文件名
                file_path = os.path.join(save_dir, file_name)

                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Downloaded: {file_path}")
            else:
                print(f"Failed to download: {link}, Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading {link}: {e}")

if __name__ == "__main__":
# 获取当前目录，并拼接 JSON 文件路径
    json_file_path = os.path.join(os.getcwd(), "link.json")  # JSON 文件路径
    save_directory = "save"  # 保存文件的文件夹名称

    links = read_links_from_json(json_file_path)
    download_files(links, save_directory)