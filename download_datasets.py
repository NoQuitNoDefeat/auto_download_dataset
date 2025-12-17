import os
import requests
import shutil
from tqdm import tqdm

# ================= 1. 数据集下载链接配置 =================

DOWNLOAD_DIR = "datasets_downloaded"

DATASET_URLS = {
    # --- RATM (TII Racing) ---
    # 自动
    "ratm_autonomous": [
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/autonomous_zipchunk01",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/autonomous_zipchunk02",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/autonomous_zipchunk03"
    ],
    # 人工
    "ratm_piloted": [
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/piloted_zipchunk01",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/piloted_zipchunk02",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/piloted_zipchunk03",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/piloted_zipchunk04",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/piloted_zipchunk05",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/piloted_zipchunk06",
        "https://github.com/tii-racing/drone-racing-dataset/releases/download/v3.0.0/piloted_zipchunk07"
    ],

    # --- UZH FPV (Indoor Forward Facing) ---
    # 包含图像、IMU 和 Ground Truth
    "uzh_indoor_forward": [
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_forward_3_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_forward_5_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_forward_6_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_forward_7_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_forward_9_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_forward_10_snapdragon_with_gt.zip"
    ],

    # --- UZH FPV (Indoor 45 Degree Facing) ---
    "uzh_indoor_45": [
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_45_2_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_45_4_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_45_9_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_45_12_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_45_13_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/indoor_45_14_snapdragon_with_gt.zip"
    ],

    # --- UZH FPV (Outdoor Forward Facing) ---
    "uzh_outdoor_forward": [
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/outdoor_forward_1_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/outdoor_forward_3_snapdragon_with_gt.zip",
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/outdoor_forward_5_snapdragon_with_gt.zip"
    ],

    # --- UZH FPV (Outdoor 45 Degree Facing) ---
    "uzh_outdoor_45": [
        "http://rpg.ifi.uzh.ch/datasets/uzh-fpv/outdoor_45_1_snapdragon_with_gt.zip"
    ]
    #
    # # --- GRASP (UPenn)失效 ---
    # "grasp": [
    #     "http://mrsl.grasp.upenn.edu/ke/dataset/fla_wg_10.bag"
    # ],
    #
    # # --- Blackbird (MIT)也失效 ---
    # # 注意: 下载的是 .torrent 种子文件
    # "blackbird": [
    #     "https://academictorrents.com/download/eb542a231dbeb2125e4ec88ddd18841a867c2656.torrent"
    # ]
}


# ================= 2. 高速下载模块 =================

def download_file_fast(url, folder_path):
    """
    使用 requests 和 tqdm 实现带有进度条的流式下载
    """
    # 从 URL 提取文件名
    local_filename = url.split('/')[-1].split('?')[0]
    local_path = os.path.join(folder_path, local_filename)

    # 简单的断点续传检测：如果文件已存在且大小匹配（这里暂不校验Hash），则跳过
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
    except Exception as e:
        print(f"❌ 无法连接到服务器: {url}\n错误: {e}")
        return None

    if os.path.exists(local_path):
        existing_size = os.path.getsize(local_path)
        if existing_size == total_size and total_size > 0:
            print(f"  [跳过] 文件已存在且完整: {local_filename}")
            return local_path
        elif existing_size > 0:
            print(f"  [覆盖] 文件不完整，重新下载: {local_filename}")

    # 开始下载
    block_size = 1024 * 1024  # 1MB 缓冲区
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=local_filename, ncols=100)

    try:
        with open(local_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        return local_path
    except Exception as e:
        progress_bar.close()
        print(f"❌ 下载中断: {e}")
        return None


# ================= 3. 合并与清理模块 =================

def merge_ratm_files(dataset_name, folder_path, file_list):
    """
    专门处理 RATM 的分卷合并逻辑
    """
    # 确定合并后的目标文件名
    if "autonomous" in dataset_name:
        target_name = "autonomous.zip"
    elif "piloted" in dataset_name:
        target_name = "piloted.zip"
    else:
        return  # 不是 RATM 数据集，无需合并

    target_path = os.path.join(folder_path, target_name)

    if os.path.exists(target_path):
        print(f"  ✅ 合并目标已存在 ({target_name})，跳过合并。")
        return

    print(f"  ⚙️ 正在合并 {len(file_list)} 个分卷文件... (请勿关闭)")

    try:
        # 按顺序合并文件
        # 这里的 file_list 顺序很重要，代码逻辑依赖于 DATASET_URLS 里的列表顺序
        with open(target_path, 'wb') as outfile:
            for chunk_path in file_list:
                if not chunk_path or not os.path.exists(chunk_path):
                    print(f"  ❌ 错误: 缺少分卷 {chunk_path}，无法合并。")
                    return

                # 流式复制，避免内存溢出
                with open(chunk_path, 'rb') as infile:
                    shutil.copyfileobj(infile, outfile)

        print(f"  ✅ 合并成功: {target_name}")

        # 删除原始分卷
        print(f"  🧹 正在删除原始分卷以释放空间...")
        for chunk_path in file_list:
            os.remove(chunk_path)
        print("  ✅ 清理完成。")

    except Exception as e:
        print(f"  ❌ 合并失败: {e}")


# ================= 4. 主程序入口 =================

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    print(f"{'=' * 40}")
    print("   自动驾驶数据集下载管理器 (Python完整版)")
    print(f"{'=' * 40}")
    print(f"下载目录: {os.path.abspath(DOWNLOAD_DIR)}\n")

    for name, urls in DATASET_URLS.items():
        print(f"🚀 正在处理数据集: [{name}]")

        dataset_path = os.path.join(DOWNLOAD_DIR, name)
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)

        downloaded_files = []
        all_success = True

        # 1. 下载阶段
        for url in urls:
            file_path = download_file_fast(url, dataset_path)
            if file_path:
                downloaded_files.append(file_path)
            else:
                all_success = False

        # 2. 合并阶段 (仅当下载全部成功且是 RATM 时)
        if all_success and "ratm" in name:
            merge_ratm_files(name, dataset_path, downloaded_files)

        print("-" * 40)

    print("\n🎉 所有任务处理完毕！")
    # print("注意: Blackbird 下载的是种子文件，请使用迅雷/BT软件打开下载实际数据。")


if __name__ == "__main__":
    main()