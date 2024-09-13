# For General Information

https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server

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

[Install]
WantedBy=default.target
```

Reload:

> sudo systemctl daemon-reload

> sudo systemctl restart ollama
