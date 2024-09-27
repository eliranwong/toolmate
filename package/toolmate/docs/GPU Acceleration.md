# Speed Up with GPU Acceleration

It applies to backends 'llamacpp' and 'ollama' only. Speed of online API inference, e.g. ChatGPT or Gemini, does not depend on local hardware.

# Llama.cpp

Llama.cpp supports several GPU backends, read https://llama-cpp-python.readthedocs.io/en/latest/.

1. Use the cmake arguments that support your GPU backend to reinstall llama-cpp-python.

For example, to [accelerate with ADM RX 7900 XTX via ROCM](https://github.com/eliranwong/MultiAMDGPU_AIDev_Ubuntu#toolmate):

```
pip install --upgrade --force-reinstall --no-cache-dir toolmate numpy==1.26.4 llama-cpp-python[server] -C cmake.args="-DGGML_HIPBLAS=on" stable-diffusion-cpp-python -C cmake.args="-DSD_HIPBLAS=ON -DCMAKE_BUILD_TYPE=Release -DAMDGPU_TARGETS=gfx1100"
```

2. [Edit config.py](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Edit%20Config%20Manually.md):

```
llamacppToolModel_n_gpu_layers = -1
llamacppChatModel_n_gpu_layers = -1
llamacppVisionModel_n_gpu_layers = -1
```

# Llama.cpp Server

For full control, we recommend advanced users to use llama.cpp server

Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/GPU%20Acceleration%20with%20Llama_cpp%20server.md

# Ollama

For easy setup, ollama is a nice choice.
 
Automatic hardware detection when you install ollama.

# Groq / ChatGPT / Gemini

Not applicable.

# Stable-diffusion-cpp-python

Reinstall stable-diffusion-cpp-python, to accelerate with GPU for image generation, e.g. with ROCM:

```
pip install --upgrade --force-reinstall --no-cache-dir stable-diffusion-cpp-python -C cmake.args="-DSD_HIPBLAS=ON -DCMAKE_BUILD_TYPE=Release -DAMDGPU_TARGETS=gfx1100"
```

For GPUs other than AMD, read https://github.com/william-murray1204/stable-diffusion-cpp-python#supported-backends