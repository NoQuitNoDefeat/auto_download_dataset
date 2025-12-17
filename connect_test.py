import requests


def check_link_status(url):
    print(f"正在检测链接: {url} ...")
    try:
        # 发送 HEAD 请求 (只获取头信息，不下载内容)
        response = requests.head(url, timeout=10)

        if response.status_code == 200:
            file_size = response.headers.get('Content-Length', '未知')
            print(f"✅ [有效] 链接正常。")
            print(f"   文件大小: {int(file_size) / 1024 / 1024:.2f} MB" if file_size != '未知' else "   文件大小: 未知")
            return True
        elif response.status_code == 404:
            print(f"❌ [失效] 文件不存在 (404 Not Found)。")
            print("   可能原因: 文件已被服务器移除，或文件名变更。")
        elif response.status_code == 403:
            print(f"🚫 [禁止] 没有权限访问 (403 Forbidden)。")
        else:
            print(f"⚠️ [其他] 服务器返回状态码: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"❌ [连接失败] 无法连接到服务器 mrsl.grasp.upenn.edu。")
        print("   可能原因: 学校服务器宕机，或者你需要挂/关代理。")
    except requests.exceptions.Timeout:
        print(f"⏳ [超时] 连接超时。服务器响应太慢。")
    except Exception as e:
        print(f"❌ 检测出错: {e}")
    return False


# 官方文档列出的所有相关数据集链接
links_to_check = [
    "http://mrsl.grasp.upenn.edu/ke/dataset/fla_wg_15.bag",  # 你询问的 (15m/s)
    "http://mrsl.grasp.upenn.edu/ke/dataset/fla_wg_10.bag",  # 10m/s (之前能用的)
    "http://mrsl.grasp.upenn.edu/ke/dataset/fla_wg_175.bag",  # 17.5m/s (极速)
]

print("=== GRASP 数据集状态检测 ===")
for link in links_to_check:
    check_link_status(link)
    print("-" * 30)