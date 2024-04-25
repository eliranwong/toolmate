from freegenius import config, isServerAlive, print2
import os, sys

def chat():
    if isServerAlive("127.0.0.1", config.llamacppMainModel_server_port):
        print2(f"A service is already running at 127.0.0.1:{config.llamacppMainModel_server_port}!")
        return None
    cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppMainModel_server_port} --model "{config.llamacppMainModel_model_path}" --verbose True --chat_format chatml --n_ctx {config.llamacppMainModel_n_ctx} --n_gpu_layers {config.llamacppMainModel_n_gpu_layers} --n_batch {config.llamacppMainModel_n_batch} {config.llamacppMainModel_additional_server_options}"""
    os.system(cmd)

def vision():
    if isServerAlive("127.0.0.1", config.llamacppVisionModel_server_port):
        print2(f"A service is already running at 127.0.0.1:{config.llamacppVisionModel_server_port}!")
        return None
    cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppVisionModel_server_port} --model "{config.llamacppVisionModel_model_path}" --clip_model_path {config.llamacppVisionModel_clip_model_path} --verbose True --chat_format llava-1-5 --n_ctx {config.llamacppVisionModel_n_ctx} --n_gpu_layers {config.llamacppVisionModel_n_gpu_layers} --n_batch {config.llamacppVisionModel_n_batch} {config.llamacppVisionModel_additional_server_options}"""
    os.system(cmd)