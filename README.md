# Drone Dataset Downloader (Auto_code4)

这是一个用于自动下载、合并和管理无人机竞速（Drone Racing）数据集的 Python 工具。

该脚本主要解决了 **RATM (Race Against The Machine)** 数据集的分卷下载与自动合并问题，同时也记录了其他相关数据集的链接有效性。

## 📊 数据集状态 (Dataset Status)

截止目前，代码配置 (`download_datasets.py`) 中的数据集可用情况如下：

| 数据集名称 | 内容描述 | 状态 | 备注 |
| :--- | :--- | :---: | :--- |
| **RATM (Autonomous)** | TII Racing 自动驾驶数据 | ✅ **可用** | 包含 v3.0.0 的 3 个分卷。脚本会自动下载、合并为 zip 并清理分卷。 |
| **RATM (Piloted)** | TII Racing 人工驾驶数据 | ✅ **可用** | 包含 v3.0.0 的 7 个分卷。脚本会自动下载、合并为 zip 并清理分卷。 |
| **UZH FPV** | Zurich 室内前视数据 | ⏸️ **暂停** | 链接有效，但在代码中默认被注释掉 (Commented out)。 |
| **GRASP** | UPenn Fast Flight | ❌ **失效** | 原始下载链接无法访问或服务器已关闭。 |
| **Blackbird** | MIT Torrent 种子 | ❌ **失效** | 原始种子链接无法访问。 |

## 🛠️ 安装环境 (Installation)

本项目依赖 Python 3。在运行之前，请确保已安装必要的依赖库。

1. **激活虚拟环境** (如果已创建 `.venv`):
   - Windows: `.\.venv\Scripts\Activate`
   - Mac/Linux: `source .venv/bin/activate`

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt

 ## 🚀 使用方法 (Usage)
 直接运行主脚本即可开始任务：
```bash
python download_datasets.py
