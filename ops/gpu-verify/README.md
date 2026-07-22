# GPU 驗證工具（ops/gpu-verify/）

本機開發環境的一鍵 GPU/CUDA 驗證工具，依序檢查驅動直通、原生 CUDA 編譯、以及框架層可用性。

> ℹ️ **範圍界定**：這是**開發機本機**驗證用途。生效部署環境為 GB10 / ARM64（見
> [`../../infrastructure/ENVIRONMENT-SPEC.md`](../../infrastructure/ENVIRONMENT-SPEC.md)）；
> 本工具驗證的是 x86_64 + NVIDIA GPU（WSL2）開發機，與部署環境架構不同，僅供本機工具鏈健檢。

## 用法

```bash
cd ops/gpu-verify
./gpu_verify.sh                 # 執行全部四項
./gpu_verify.sh --arch sm_86    # 指定 GPU 架構（預設 sm_75，對應 GTX 1650 / Turing）
SKIP_PYTORCH=1 ./gpu_verify.sh  # 只測 nvidia-smi + nvcc（不需 Python 環境）
```

首次執行若 `.gpu-test-venv/` 不存在，腳本會自動建立並安裝 `torch (cu126)`、`numpy`、`cuda-python`。全部通過時 exit code 為 0（可接 CI）。

## 四項測試

| # | 測試 | 檔案 | 驗證內容 |
|---|------|------|----------|
| 1 | `nvidia-smi` | —（系統工具） | 驅動 / GPU 直通可見性 |
| 2 | nvcc 原生 CUDA C | `saxpy.cu` | 系統 `nvcc` 編譯 → GPU 執行 → 結果正確 |
| 3 | PyTorch (cu126) | `gpu_test.py` | 框架層 `torch.cuda`，含 fp32 matmul 效能 |
| 4 | NVRTC (cuda-python) | `cuda_native_test.py` | 執行期編譯原生 kernel（NVRTC + Driver API） |

## 檔案

| 檔案 | 版控 | 說明 |
|------|------|------|
| `gpu_verify.sh` | ✅ | 一鍵驗證主腳本 |
| `saxpy.cu` | ✅ | nvcc 原生 CUDA C 測試源碼 |
| `gpu_test.py` | ✅ | PyTorch 框架層測試 |
| `cuda_native_test.py` | ✅ | NVRTC 執行期編譯測試 |
| `.gpu-test-venv/` | ❌（gitignore） | 測試用 Python 環境，各機自動重建 |
| `saxpy` | ❌（gitignore） | nvcc 編譯產物 |

## 前置需求

- NVIDIA GPU + WSL2 GPU 直通（`/dev/dxg` 存在、`nvidia-smi` 可見）
- 系統 CUDA Toolkit：`sudo apt install nvidia-cuda-toolkit`（提供 `nvcc`）
- `python3-venv`（建立測試環境用）

## 已知環境備註

- 本機實測基準：NVIDIA GeForce GTX 1650（sm_75, 4 GB）、驅動 CUDA 12.6、系統 nvcc 12.0。
- 在 Cursor agent 的預設 sandbox 內執行時，GPU 步驟會因 `/dev/dxg` 被沙箱阻擋而 FAIL；請於**一般終端機**執行。
