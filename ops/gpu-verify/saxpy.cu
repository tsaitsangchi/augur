// Native CUDA C test compiled with the system nvcc.
// SAXPY: out = a*x + y, plus a small fp32 matmul-style throughput check.
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cuda_runtime.h>

#define CK(call)                                                             \
    do {                                                                     \
        cudaError_t _e = (call);                                             \
        if (_e != cudaSuccess) {                                             \
            fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__,    \
                    cudaGetErrorString(_e));                                 \
            exit(1);                                                         \
        }                                                                    \
    } while (0)

__global__ void saxpy(float a, const float *x, const float *y, float *out, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) out[i] = a * x[i] + y[i];
}

int main() {
    int dev = 0;
    cudaDeviceProp prop;
    CK(cudaGetDevice(&dev));
    CK(cudaGetDeviceProperties(&prop, dev));
    printf("device        : %s (sm_%d%d, %.0f MiB, %d SMs)\n",
           prop.name, prop.major, prop.minor,
           prop.totalGlobalMem / 1048576.0, prop.multiProcessorCount);

    const int n = 1 << 20;           // 1,048,576 elements
    const size_t bytes = n * sizeof(float);
    float a = 2.0f;
    float *hx = (float *)malloc(bytes);
    float *hy = (float *)malloc(bytes);
    float *ho = (float *)malloc(bytes);
    for (int i = 0; i < n; ++i) { hx[i] = (float)i; hy[i] = 1.0f; }

    float *dx, *dy, *dout;
    CK(cudaMalloc(&dx, bytes));
    CK(cudaMalloc(&dy, bytes));
    CK(cudaMalloc(&dout, bytes));
    CK(cudaMemcpy(dx, hx, bytes, cudaMemcpyHostToDevice));
    CK(cudaMemcpy(dy, hy, bytes, cudaMemcpyHostToDevice));

    int threads = 256;
    int blocks = (n + threads - 1) / threads;

    // Timed run
    cudaEvent_t t0, t1;
    CK(cudaEventCreate(&t0));
    CK(cudaEventCreate(&t1));
    const int iters = 100;
    CK(cudaEventRecord(t0));
    for (int it = 0; it < iters; ++it)
        saxpy<<<blocks, threads>>>(a, dx, dy, dout, n);
    CK(cudaEventRecord(t1));
    CK(cudaEventSynchronize(t1));
    float ms = 0.0f;
    CK(cudaEventElapsedTime(&ms, t0, t1));
    CK(cudaGetLastError());

    CK(cudaMemcpy(ho, dout, bytes, cudaMemcpyDeviceToHost));
    double max_err = 0.0;
    for (int i = 0; i < n; ++i)
        max_err = fmax(max_err, fabs(ho[i] - (a * hx[i] + hy[i])));

    double gbps = (3.0 * bytes * iters) / (ms / 1000.0) / 1e9;
    printf("kernel        : out = %.1f*x + y  on %d elements\n", a, n);
    printf("sample        : out[123] = %.1f (expected %.1f)\n", ho[123], a * hx[123] + hy[123]);
    printf("throughput    : %.2f ms / %d iters -> %.1f GB/s effective\n", ms, iters, gbps);
    printf("max error     : %.3e\n", max_err);
    printf("RESULT        : %s\n", max_err == 0.0 ? "NATIVE nvcc CUDA OK" : "MISMATCH");

    cudaFree(dx); cudaFree(dy); cudaFree(dout);
    free(hx); free(hy); free(ho);
    return 0;
}
