# For General Information

https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server

# Minimum Ollama Version

From Toolmate AI version 0.5.75, we support Ollama v0.5.0+ latest structured output featue. Users need to upgrade Ollama to version 0.5.0 or higher to work with Toolmate AI.  Read https://ollama.com/ for downloading the latest Ollama version.

# Ubuntu

Official guide uses "systemctl edit ollama.service", however it does not work for some users.

Instead, I use:

> sudo nano /etc/systemd/system/ollama.service

Edit the content, e.g.

```
Read [Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=4"
Environment="OLLAMA_HOST=0.0.0.0"

[Install]
WantedBy=default.target
```

Reload:

> sudo systemctl daemon-reload

> sudo systemctl restart ollama

# Android

Install Ollama on Android via Termux

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Termux%20Setup.md#instal-ollama-on-termux

Install Ollama on Android via Ubuntu container in Termux

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Termux%20Setup.md#install-toolmate-ai