import time
import torch

print("torch version   :", torch.__version__)
print("CUDA available  :", torch.cuda.is_available())
print("CUDA runtime ver:", torch.version.cuda)

if not torch.cuda.is_available():
    raise SystemExit("CUDA not available to PyTorch")

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
# warmup
for _ in range(3):
    c = a @ b
torch.cuda.synchronize()

iters = 20
t0 = time.time()
for _ in range(iters):
    c = a @ b
torch.cuda.synchronize()
dt = (time.time() - t0) / iters

flops = 2 * n**3
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
