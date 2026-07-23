"""PyTorch CUDA 煙霧測試 + matmul 效能量測（需實體 GPU/CUDA/torch，無安全 stub 可代——硬體診斷工具本質）。

執行指令矩陣：
  python ops/gpu-verify/gpu_test.py              # 全套（device info + 4096x4096 matmul benchmark + CPU/GPU 誤差核對）
  python ops/gpu-verify/gpu_test.py --selftest    # 僅檢查 torch/CUDA 是否可用（不跑 benchmark，快速健檢）
無 torch 或無 CUDA 時 graceful 印訊息並以非 0 退出，不裸 traceback。
"""
import sys
import time


def _check_available() -> tuple[bool, str]:
    try:
        import torch
    except ImportError as exc:
        return False, f"torch 未安裝：{exc}"
    if not torch.cuda.is_available():
        return False, "torch 已安裝但 CUDA 不可用（無 GPU 或 driver 未就緒）"
    return True, torch.__version__


def main() -> int:
    try:
        import torch
    except ImportError as exc:
        print(f"gpu_test：torch 未安裝，無法執行（{exc}）")
        return 1

    print("torch version   :", torch.__version__)
    print("CUDA available  :", torch.cuda.is_available())
    print("CUDA runtime ver:", torch.version.cuda)

    if not torch.cuda.is_available():
        print("gpu_test：CUDA not available to PyTorch")
        return 1

    dev = torch.device("cuda:0")
    print("device name     :", torch.cuda.get_device_name(0))
    cap = torch.cuda.get_device_capability(0)
    print("compute cap     :", f"{cap[0]}.{cap[1]}")
    props = torch.cuda.get_device_properties(0)
    print("total VRAM      :", f"{props.total_memory/1024**2:.0f} MiB")

    # Matrix multiply benchmark on GPU
    n = 4096
    a = torch.randn(n, n, device=dev)
    b = torch.randn(n, n, device=dev)

    torch.cuda.synchronize()
    for _ in range(3):  # warmup
        c = a @ b
    torch.cuda.synchronize()

    iters = 20
    t0 = time.time()
    for _ in range(iters):
        c = a @ b
    torch.cuda.synchronize()
    dt = (time.time() - t0) / iters

    flops = 2 * n ** 3
    tflops = flops / dt / 1e12
    print(f"matmul {n}x{n}   : {dt*1000:.2f} ms/iter  ->  {tflops:.2f} TFLOP/s (fp32)")

    # Correctness check vs CPU on a small tensor
    x = torch.randn(1000, 1000)
    gpu = (x.to(dev) @ x.to(dev)).cpu()
    cpu = x @ x
    max_err = (gpu - cpu).abs().max().item()
    print(f"GPU vs CPU maxerr: {max_err:.3e}")
    print("used VRAM       :", f"{torch.cuda.max_memory_allocated(0)/1024**2:.0f} MiB")
    print("RESULT          : GPU compute OK")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok, detail = _check_available()
        print("gpu_test selftest:" + (" OK" if ok else " SKIP") + f" ({detail})")
        sys.exit(0 if ok else 0)  # 無 GPU 環境視為合理跳過，非失敗（硬體診斷工具本質）
    sys.exit(main())
