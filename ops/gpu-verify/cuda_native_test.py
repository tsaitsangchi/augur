"""Compile a native CUDA C kernel at runtime with NVRTC and run it via the
CUDA Driver API (cuda-python). Proves the CUDA toolkit (NVRTC + ptxas + driver)
works end to end. Based on NVIDIA's canonical saxpy example."""
import numpy as np
from cuda.bindings import driver as cuda
from cuda.bindings import nvrtc

KERNEL_SRC = b"""
extern "C" __global__
void saxpy(float a, float *x, float *y, float *out, size_t n) {
    size_t tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n) out[tid] = a * x[tid] + y[tid];
}
"""


def _err_name(err):
    if isinstance(err, cuda.CUresult):
        return cuda.cuGetErrorString(err)[1]
    if isinstance(err, nvrtc.nvrtcResult):
        return nvrtc.nvrtcGetErrorString(err)[1]
    return str(err)


def ck(res):
    err, *vals = res
    ok = (err == cuda.CUresult.CUDA_SUCCESS if isinstance(err, cuda.CUresult)
          else err == nvrtc.nvrtcResult.NVRTC_SUCCESS)
    if not ok:
        raise RuntimeError(f"error: {_err_name(err)}")
    if not vals:
        return None
    return vals[0] if len(vals) == 1 else vals


# --- Device + context ---
ck(cuda.cuInit(0))
dev = ck(cuda.cuDeviceGet(0))
name = ck(cuda.cuDeviceGetName(128, dev)).split(b"\x00")[0].decode(errors="ignore").strip()
major = ck(cuda.cuDeviceGetAttribute(
    cuda.CUdevice_attribute.CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR, dev))
minor = ck(cuda.cuDeviceGetAttribute(
    cuda.CUdevice_attribute.CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR, dev))
print(f"device          : {name}  (sm_{major}{minor})")
ctx = ck(cuda.cuCtxCreate(0, dev))

# --- NVRTC compile for this GPU arch ---
prog = ck(nvrtc.nvrtcCreateProgram(KERNEL_SRC, b"saxpy.cu", 0, [], []))
opts = [bytes(f"--gpu-architecture=sm_{major}{minor}", "ascii")]
comp = nvrtc.nvrtcCompileProgram(prog, len(opts), opts)
log_size = ck(nvrtc.nvrtcGetProgramLogSize(prog))
if log_size > 1:
    buf = b" " * log_size
    nvrtc.nvrtcGetProgramLog(prog, buf)
    print("nvrtc log       :", buf.decode(errors="ignore").strip())
ck(comp)
ptx_size = ck(nvrtc.nvrtcGetPTXSize(prog))
ptx = b" " * ptx_size
ck(nvrtc.nvrtcGetPTX(prog, ptx))
ver = nvrtc.nvrtcVersion()[1:]
print(f"NVRTC compile   : {ptx_size} bytes PTX  (NVRTC {ver[0]}.{ver[1]})")

# --- Load module + kernel ---
ptx = np.char.array(ptx)
module = ck(cuda.cuModuleLoadData(ptx.ctypes.data))
kernel = ck(cuda.cuModuleGetFunction(module, b"saxpy"))

# --- Data ---
NUM_THREADS = 256
NUM_BLOCKS = 4096
n = np.array(NUM_THREADS * NUM_BLOCKS, dtype=np.uint64)  # ~1.05M
a = np.array([2.0], dtype=np.float32)
h_x = np.arange(int(n), dtype=np.float32)
h_y = np.ones(int(n), dtype=np.float32)
h_out = np.zeros(int(n), dtype=np.float32)
buf_size = int(n) * h_x.itemsize

d_x = ck(cuda.cuMemAlloc(buf_size))
d_y = ck(cuda.cuMemAlloc(buf_size))
d_out = ck(cuda.cuMemAlloc(buf_size))
ck(cuda.cuMemcpyHtoD(d_x, h_x.ctypes.data, buf_size))
ck(cuda.cuMemcpyHtoD(d_y, h_y.ctypes.data, buf_size))

# --- Kernel arg buffer: array of pointers to each arg ---
ax = np.array([int(d_x)], dtype=np.uint64)
ay = np.array([int(d_y)], dtype=np.uint64)
ao = np.array([int(d_out)], dtype=np.uint64)
args = [a, ax, ay, ao, n]
args = np.array([arg.ctypes.data for arg in args], dtype=np.uint64)

ck(cuda.cuLaunchKernel(kernel, NUM_BLOCKS, 1, 1, NUM_THREADS, 1, 1,
                       0, 0, args.ctypes.data, 0))
ck(cuda.cuCtxSynchronize())

ck(cuda.cuMemcpyDtoH(h_out.ctypes.data, d_out, buf_size))
expected = a[0] * h_x + h_y
max_err = float(np.max(np.abs(h_out - expected)))
print(f"kernel          : out = {a[0]} * x + y  on {int(n):,} elements")
print(f"sample          : out[123]={h_out[123]:.1f}  expected={expected[123]:.1f}")
print(f"max error       : {max_err:.3e}")
print("RESULT          :", "NATIVE CUDA KERNEL OK" if max_err == 0 else "MISMATCH")

for d in (d_x, d_y, d_out):
    cuda.cuMemFree(d)
cuda.cuModuleUnload(module)
cuda.cuCtxDestroy(ctx)
