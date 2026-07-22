#!/usr/bin/env bash
# 一鍵 GPU 驗證腳本
# 依序執行三項測試：
#   1) nvidia-smi          - 驅動 / GPU 直通可見性
#   2) nvcc 原生 CUDA C    - 系統 nvcc 編譯 saxpy.cu 並在 GPU 執行
#   3) PyTorch (cu126)     - 框架層 CUDA 可用性 + fp32 matmul
#   4) NVRTC (cuda-python) - 執行期編譯原生 kernel 並執行
#
# 用法:
#   ./gpu_verify.sh              # 執行全部
#   ./gpu_verify.sh --arch sm_86 # 指定 GPU 架構 (預設 sm_75, 對應 GTX 1650)
#   SKIP_PYTORCH=1 ./gpu_verify.sh   # 跳過 PyTorch/NVRTC (只測 nvidia-smi + nvcc)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ARCH="sm_75"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --arch) ARCH="$2"; shift 2 ;;
        *) echo "未知參數: $1"; exit 2 ;;
    esac
done

VENV="$SCRIPT_DIR/.gpu-test-venv"
PY="$VENV/bin/python"

# 顏色 (若非 TTY 則停用)
if [[ -t 1 ]]; then
    G='\033[0;32m'; R='\033[0;31m'; Y='\033[1;33m'; B='\033[1;34m'; N='\033[0m'
else
    G=''; R=''; Y=''; B=''; N=''
fi

PASS=0
FAIL=0
declare -a RESULTS

section() { echo -e "\n${B}==== $1 ====${N}"; }
ok()   { echo -e "${G}[PASS]${N} $1"; PASS=$((PASS+1)); RESULTS+=("PASS  $1"); }
bad()  { echo -e "${R}[FAIL]${N} $1"; FAIL=$((FAIL+1)); RESULTS+=("FAIL  $1"); }
skip() { echo -e "${Y}[SKIP]${N} $1"; RESULTS+=("SKIP  $1"); }

# ---------- 1. nvidia-smi ----------
section "1/4  nvidia-smi (驅動 / 直通)"
if command -v nvidia-smi >/dev/null 2>&1; then
    if nvidia-smi --query-gpu=name,driver_version,memory.total,utilization.gpu \
                  --format=csv,noheader 2>/dev/null; then
        ok "nvidia-smi: GPU 可見"
    else
        bad "nvidia-smi 存在但無法存取 GPU (可能被 sandbox 或權限擋住)"
    fi
else
    bad "找不到 nvidia-smi"
fi

# ---------- 2. nvcc 原生 CUDA ----------
section "2/4  nvcc 原生 CUDA (arch=$ARCH)"
if command -v nvcc >/dev/null 2>&1; then
    nvcc --version | grep -i "release" || true
    if [[ -f "$SCRIPT_DIR/saxpy.cu" ]]; then
        if nvcc -O2 -arch="$ARCH" "$SCRIPT_DIR/saxpy.cu" -o "$SCRIPT_DIR/saxpy" 2>&1; then
            if OUT=$("$SCRIPT_DIR/saxpy" 2>&1); then
                echo "$OUT"
                if echo "$OUT" | grep -q "NATIVE nvcc CUDA OK"; then
                    ok "nvcc 原生 CUDA kernel"
                else
                    bad "nvcc 程式執行但結果不符"
                fi
            else
                echo "$OUT"; bad "nvcc 程式執行失敗 (GPU 存取?)"
            fi
        else
            bad "nvcc 編譯失敗"
        fi
    else
        bad "找不到 saxpy.cu"
    fi
else
    bad "找不到 nvcc (需: sudo apt install nvidia-cuda-toolkit)"
fi

# ---------- venv 準備 (PyTorch / NVRTC 共用) ----------
NEED_PY=1
if [[ "${SKIP_PYTORCH:-0}" == "1" ]]; then
    NEED_PY=0
fi

if [[ "$NEED_PY" == "1" ]]; then
    if [[ ! -x "$PY" ]]; then
        section "建立測試用 venv"
        if python3 -m venv "$VENV" 2>&1; then
            echo "已建立 $VENV，安裝 torch (cu126) + numpy + cuda-python ..."
            "$VENV/bin/pip" install --disable-pip-version-check -q \
                --index-url https://download.pytorch.org/whl/cu126 torch numpy 2>&1 | tail -n 3
            "$VENV/bin/pip" install --disable-pip-version-check -q cuda-python 2>&1 | tail -n 2
        else
            echo -e "${Y}無法建立 venv，將跳過 PyTorch / NVRTC${N}"
            NEED_PY=0
        fi
    fi
fi

# ---------- 3. PyTorch ----------
section "3/4  PyTorch (框架層 CUDA)"
if [[ "$NEED_PY" == "1" && -x "$PY" && -f "$SCRIPT_DIR/gpu_test.py" ]]; then
    if OUT=$("$PY" "$SCRIPT_DIR/gpu_test.py" 2>&1); then
        echo "$OUT"
        if echo "$OUT" | grep -q "GPU compute OK"; then
            ok "PyTorch CUDA"
        else
            bad "PyTorch 執行但未通過"
        fi
    else
        echo "$OUT"; bad "PyTorch 測試失敗"
    fi
else
    skip "PyTorch (venv 未就緒或缺 gpu_test.py 或 SKIP_PYTORCH=1)"
fi

# ---------- 4. NVRTC ----------
section "4/4  NVRTC (執行期編譯原生 kernel)"
if [[ "$NEED_PY" == "1" && -x "$PY" && -f "$SCRIPT_DIR/cuda_native_test.py" ]]; then
    if OUT=$("$PY" "$SCRIPT_DIR/cuda_native_test.py" 2>&1); then
        echo "$OUT"
        if echo "$OUT" | grep -q "NATIVE CUDA KERNEL OK"; then
            ok "NVRTC 原生 kernel"
        else
            bad "NVRTC 執行但結果不符"
        fi
    else
        echo "$OUT"; bad "NVRTC 測試失敗"
    fi
else
    skip "NVRTC (venv 未就緒或缺 cuda_native_test.py 或 SKIP_PYTORCH=1)"
fi

# ---------- 總結 ----------
section "總結"
for r in "${RESULTS[@]}"; do
    case "$r" in
        PASS*) echo -e "  ${G}$r${N}" ;;
        FAIL*) echo -e "  ${R}$r${N}" ;;
        *)     echo -e "  ${Y}$r${N}" ;;
    esac
done
echo -e "\n通過: ${G}${PASS}${N}   失敗: ${R}${FAIL}${N}"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
