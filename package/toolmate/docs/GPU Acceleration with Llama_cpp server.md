# Configure Llama.cpp Server with GPU Acceleration

![llamacpp_with_gpu_offloading_compressed](https://github.com/eliranwong/toolmate/assets/25262722/2d607fc1-e6b5-4c62-be14-325d73866fce)

Run '.model' in ToolMate AI prompt and select 'llamacppserver' as LLM interface.  This option is designed for advanced users who want more control over the LLM backend, particularly useful for customisation like GPU acceleration.

# Requirements:

1. You need an access to a server that have llama.cpp running on it. If you don't, you may want to [build and run a llama.cpp server](https://github.com/ggerganov/llama.cpp?tab=readme-ov-file#build) on your device, to customise everything to suit your own needs.

2. Specify the llama.cpp server ip address and port in ToolMate AI settings.

# Examples to build a Llama.cpp server

## Example - macOS

On MacOS, Metal is enabled by default. Using Metal makes the computation run on the GPU.  Therefore, compiling source is a simple one:

To compile llama.cpp from source:

> cd ~

> git clone https://github.com/ggerganov/llama.cpp

> cd llama.cpp

> make

To configure ToolMate AI:

1. Run 'toolmate' in your environment

2. Enter '.model' in ToolMate AI prompt.

3. Follow the instructions to enter command line, server ip, port and timeout settings.

<img width="729" alt="Screenshot 2024-06-06 at 11 32 54" src="https://github.com/eliranwong/toolmate/assets/25262722/5004662d-03db-4f5b-a770-d0f16996a03c">

To start up the server, e.g.

> ~/llama.cpp/llama-server --host 127.0.0.1 --port 8080 --threads $(sysctl -n hw.physicalcpu) --ctx-size 0 --chat-template chatml --parallel 2 --model ~/models/wizardlm2.gguf

Make sure you have your LLM file in *.gguf format downloaded before starting up the server.

Brief description about the options:

```
--threads $(sysctl -n hw.physicalcpu): set the threads to the number of physical CPU cores
--ctx-size: size of the prompt context (default: 0, 0 = loaded from model)
--parallel 2: set number of slots for process requests to 2
```

For more options:

> cd llama.cpp

> ./server -h

## Example - Acceleration with AMD Integrated GPU

Inference result is roughly 1.5x faster.  Read https://github.com/eliranwong/MultiAMDGPU_AIDev_Ubuntu/blob/main/igpu_only/igpu_only.md

Tested device: Beelink GTR6 (Ryzen 9 6900HX CPU + integrated Radeon 680M GPU + 64GB RAM)

Followed https://github.com/eliranwong/MultiAMDGPU_AIDev_Ubuntu/blob/main/README.md for ROCm installation.

Environment variables:

```
export ROCM_HOME=/opt/rocm
export LD_LIBRARY_PATH=/opt/rocm/include:/opt/rocm/lib:$LD_LIBRARY_PATH
export PATH=$HOME/.local/bin:/opt/rocm/bin:/opt/rocm/llvm/bin:$PATH
export HSA_OVERRIDE_GFX_VERSION=10.3.0
```

Compile Llama.cpp from source:

> cd ~

> git clone https://github.com/ggerganov/llama.cpp

> make GGML_HIPBLAS=1 GGML_HIP_UMA=1 AMDGPU_TARGETS=gfx1030 -j$(lscpu | grep '^Core(s)' | awk '{print $NF}')

To start up the server, e.g.

> ~/llama.cpp/llama-server --host 127.0.0.1 --port 8080 --threads $(lscpu | grep '^Core(s)' | awk '{print $NF}') --ctx-size 0 --chat-template chatml --parallel 2 --gpu-layers 999 --model ~/models/wizardlm2.gguf

Please note we used `--gpu-layers` in the command above. You may want to change the its value 33 to suit your case.

```
--gpu-layers: number of layers to store in VRAM
```

Make sure you have your LLM file in *.gguf format downloaded before starting up the server.

## Example - Acceleration with Multiple Discrete AMD GPUs

Tested on Ubuntu with Dual AMD RX 7900 XTX. Full setup notes are documented at https://github.com/eliranwong/MultiAMDGPU_AIDev_Ubuntu/blob/main/README.md

Compile Llama.cpp from source:

> cd ~

> git clone https://github.com/ggerganov/llama.cpp

> make GGML_HIPBLAS=1 AMDGPU_TARGETS=gfx1100 -j$(lscpu | grep '^Core(s)' | awk '{print $NF}')

To start up the server, e.g.

> ~/llama.cpp/llama-server --host 127.0.0.1 --port 8080 --threads $(lscpu | grep '^Core(s)' | awk '{print $NF}') --ctx-size 0 --chat-template chatml --parallel 2 --gpu-layers 999 --model ~/models/wizardlm2.gguf

Make sure you have your LLM file in *.gguf format downloaded before starting up the server.

## Example - Acceleration with Nvidia GPUs

Compile Llama.cpp from source:

> cd ~

> git clone https://github.com/ggerganov/llama.cpp

> make GGML_CUDA=1 -j$(lscpu | grep '^Core(s)' | awk '{print $NF}')

To start up the server, e.g.

> ~/llama.cpp/llama-server --host 127.0.0.1 --port 8080 --threads $(lscpu | grep '^Core(s)' | awk '{print $NF}') --ctx-size 0 --chat-template chatml --parallel 2 --gpu-layers 999 --model ~/models/wizardlm2.gguf

Make sure you have your LLM file in *.gguf format downloaded before starting up the server.

# Enter IP Addresses and Port Numbers in ToolMate AI

![select_backend](https://github.com/user-attachments/assets/a2ae3751-8e39-4c03-991b-d7522176a00f)

1. Enter `.model` in ToolMate AI prompt.

2. Select `Llama.cpp Server [advanced]`.

3. Follow the dialogs to enter your Llama.cpp IP addresses and ports.

# Read more

https://github.com/ggerganov/llama.cpp?tab=readme-ov-file#build