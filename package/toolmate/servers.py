from toolmate import config, isServerAlive, print2
import os, sys

def main():
    if isServerAlive("127.0.0.1", config.llamacppToolModel_server_port):
        print2(f"A service is already running at 127.0.0.1:{config.llamacppToolModel_server_port}!")
        return None
    cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppToolModel_server_port} --model "{config.llamacppToolModel_model_path}" --verbose True --chat_format chatml --n_ctx {config.llamacppToolModel_n_ctx} --n_gpu_layers {config.llamacppToolModel_n_gpu_layers} --n_batch {config.llamacppToolModel_n_batch} {config.llamacppToolModel_additional_server_options}"""
    os.system(cmd)

def chat():
    if isServerAlive("127.0.0.1", config.llamacppChatModel_server_port):
        print2(f"A service is already running at 127.0.0.1:{config.llamacppChatModel_server_port}!")
        return None
    cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppChatModel_server_port} --model "{config.llamacppChatModel_model_path}" --verbose True --chat_format chatml --n_ctx {config.llamacppChatModel_n_ctx} --n_gpu_layers {config.llamacppChatModel_n_gpu_layers} --n_batch {config.llamacppChatModel_n_batch} {config.llamacppChatModel_additional_server_options}"""
    os.system(cmd)

def vision():
    if isServerAlive("127.0.0.1", config.llamacppVisionModel_server_port):
        print2(f"A service is already running at 127.0.0.1:{config.llamacppVisionModel_server_port}!")
        return None
    cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppVisionModel_server_port} --model "{config.llamacppVisionModel_model_path}" --clip_model_path {config.llamacppVisionModel_clip_model_path} --verbose True --chat_format llava-1-5 --n_ctx {config.llamacppVisionModel_n_ctx} --n_gpu_layers {config.llamacppVisionModel_n_gpu_layers} --n_batch {config.llamacppVisionModel_n_batch} {config.llamacppVisionModel_additional_server_options}"""
    os.system(cmd)

def custommain():
    if not config.customToolServer_ip.lower() in ("localhost", "127.0.0.1"):
        # a remote server
        return None
    elif config.customToolServer_command:
        if isServerAlive(config.customToolServer_ip, config.customToolServer_port):
            print2(f"A service is already running at {config.customToolServer_ip}:{config.customToolServer_port}!")
            return None
        os.system(config.customToolServer_command)
    else:
        main()

def customchat():
    if not config.customChatServer_ip.lower() in ("localhost", "127.0.0.1"):
        return None
    elif config.customChatServer_command:
        if isServerAlive(config.customChatServer_ip, config.customChatServer_port):
            print2(f"A service is already running at {config.customChatServer_ip}:{config.customChatServer_port}!")
            return None
        os.system(config.customChatServer_command)
    else:
        chat()

def customvision():
    if not config.customVisionServer_ip.lower() in ("localhost", "127.0.0.1"):
        return None
    elif config.customVisionServer_command:
        if isServerAlive(config.customVisionServer_ip, config.customVisionServer_port):
            print2(f"A service is already running at {config.customVisionServer_ip}:{config.customVisionServer_port}!")
            return None
        os.system(config.customVisionServer_command)
    else:
        vision()