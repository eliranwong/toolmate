# Docker Setup on Android Termux

This page describe how to set up `docker` on Android via Termux.  It is a requirement for settting up Perplexica and SearXNG with which ToolMate AI plugins `search perplexica` and `search searxng` work.

# Overview

The steps below installs a virtual machine of `alpine` in Termux.

Docker and docker related service are set up inside the virtual machine.

Android web browsers or ToolMate AI tools access the service via forwarded ports.

# Preparation 1

Install Termux first!

Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Termux%20Setup.md

# Preparation 2

Check available free memory on your Android device, by running `free -h`.

![memory_check](https://github.com/user-attachments/assets/f6364b94-8338-48a3-b216-f2b1f163a29b)

You may consider this piece of information when you assign memory to the virtual machine we are going to build.

# Preparation 3

1. Go to https://www.alpinelinux.org/downloads/
2. Locate `x86_64` ander the `virtual` session.
3. Long press on it and select `Copy link address`

In the following example the address is:

> https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-virt-3.20.3-x86_64.iso

We will use this address in the following step.

# Alpine Setup

```
cd
pkg update && pkg upgrade
pkg install wget qemu-system-x86-64-headless qemu-utils
mkdir alpine
cd alpine
wget https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-virt-3.20.3-x86_64.iso
```

Remarks: In the last line above, we use the previous copied address.

```
qemu-img create -f qcow2 alpine.qcow2 10G
qemu-system-x86_64 -m 512 -netdev user,id=n1,hostfwd=tcp::2222-:22,hostfwd=tcp::4000-:4000,hostfwd=tcp::3000-:3000,hostfwd=tcp::3001-:3001 -device virtio-net,netdev=n1 -nographic alpine.qcow2 -cdrom alpine-virt-*.iso
```

Remarks: 

1. You may adjust the memory assignment `-m 512`, depending on the available memory on your device that we previously checked, e.g. you may change it to `-m 1024` or `-m 2048`.

2. Port `2222` from host is forwarded to the port `22` in the virtual machine for ssh access from the host.

3. Ports `4000` is exposed for access to SearXNG server, that is to be installed later.

4. Ports `3000` and `3001` are exposed for access to Perplexica frontend and backend servers, that are to be installed later.

```
mkdir -p /etc/udhcpc
echo 'RESOLV_CONF="no"' >> /etc/udhcpc/udhcpc.conf
echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" >> /etc/resolv.conf
setup-alpine
```

![alpine_001](https://github.com/user-attachments/assets/a5ca574d-965e-49e2-a8b3-542da909a888)

Remarks:

For most steps in the setup, you may simply press `enter` to use default value, except the following items:

1. Enter a time zone when prompted.

![alpine_003_time_zone](https://github.com/user-attachments/assets/404a95cd-acca-4920-bad2-0eee3f180ace)

2. Enter `none` to question `Which NLP client to run?`

![ntp_client](https://github.com/user-attachments/assets/a86ef5db-ca4d-42b1-9689-c8a441d5c421)

3. Enter `yes` to question `Allow root ssh login?`

4. Enter `sda` to question `Which disk(s) would you like to use?`

5. Enter `sys` to question `How would you like to use it?`

![alpine_setup_last_steps](https://github.com/user-attachments/assets/6bb78271-863e-456b-aec9-d9f703752a41)

6. At the end, enter `y` to question `Erase the above disk(s) and continue?`

```
poweroff
exit
```

# Docker Setup

Restart:

```
echo "alias docker=\"printf '\033]0;Docker\007' && cd ~/alpine && qemu-system-x86_64 -netdev user,id=n1,hostfwd=tcp::2222-:22,hostfwd=tcp::4000-:4000,hostfwd=tcp::3000-:3000,hostfwd=tcp::3001-:3001 -device virtio-net,netdev=n1 -nographic alpine.qcow2 -m 512\"" >> ~/.bashrc
source ~/.bashrc
docker
```

Remarks: Please note that the command line here does not contain `-cdrom alpine-virt-*.iso`.

Edit repositories:

```
vi /etc/apk/repositories
```

![add_repository](https://github.com/user-attachments/assets/1f215cd5-efbf-4088-9577-b0027226a149)

1. Press the `i` key, to enter the edit mode
2. Navigate to the beginning of the line 3
3. Uncomment the line by removing the `#` symbol
4. Press the `ESC` key, to leave the edit mode
5. Enter `:wq` to save the change and exit the editor

Install Docker and common tools:

```
apk update
apk add docker docker-cli docker-compose py3-pip git wget curl
```

Start Docker:

```
service docker start
echo "service docker start" >> /etc/profile
```

Test Docker:

```
docker run hello-world
```

# Install Perplexica and SearXNG

Inside the virtual machine:

```
cd
git clone https://github.com/ItzCrazyKns/Perplexica
cd Perplexica
cp sample.config.toml config.toml
vi config.toml
```

![edit_perplexica_config](https://github.com/user-attachments/assets/340e71f1-4ea3-4048-839b-208c7c18abf8)

![perplexica_config](https://github.com/user-attachments/assets/342a1996-0d8d-4959-85a2-a439861be1b8)

Steps to edit:

1. Press the `i` key, to enter the edit mode
2. Navigate inside the quotes "" of API keys or Ollama url
3. Long press to paste previously copied API keys or url
4. Press the `ESC` key, to leave the edit mode
5. Enter `:wq` to save the change and exit the editor

```
docker compose up -d
```

Wait until you see all the ticks, like below:

![install_Perplexica](https://github.com/user-attachments/assets/7c831c15-1291-4417-8ceb-2eb5a3b4ef06)

Test SearXNG with web browser:

> http://localhost:4000

![Screenshot_20241016-004429](https://github.com/user-attachments/assets/ad08f570-9004-4561-9d56-59ca555e3518)

Test Perplexica with web browser:

> http://localhost:3000

![Screenshot_20241016-004411](https://github.com/user-attachments/assets/302401c5-1eac-4285-991f-ae97eae239bd)

Remarks: It takes time the first time for the links to be loaded.  In our testings, Firefox browser loads faster than Chrome browser.

# Integration of SearXNG and Perplexica with ToolMate AI

Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Perplexica%20and%20SearXNG%20Integration.md

# How to shutdown the virtual machine?

Run in virtual machine:

```
poweroff
exit
```

# How to restart the virtual machine?

Run in Termux:

```
qemu-system-x86_64 -m 512 -netdev user,id=n1,hostfwd=tcp::2222-:22,hostfwd=tcp::4000-:4000,hostfwd=tcp::3000-:3000,hostfwd=tcp::3001-:3001 -device virtio-net,netdev=n1 -nographic alpine.qcow2
```

# How to run ToolMate AI while the virtual machine is running?

Long press the left edge of the Termux app and drag gently to the right, then you will see the panel where you can add a `NEW SESSION`.

Launch a `NEW SESSION` in which you may run ToolMate AI.

![new_session](https://github.com/user-attachments/assets/3cc9f388-e878-45a6-9ba7-a846fa092c5d)

# How to Update Perplexica?
```
cd ~/Perplexica
git pull
docker pull
docker compose up -d
```

# References

https://github.com/P1N2O/qemu-termux-alpine

https://github.com/cyberkernelofficial/docker-in-termux

https://medium.com/@kumargaurav.pandey/vms-on-mobile-without-root-yes-please-f14f473deec7

https://medium.com/@kumargaurav.pandey/docker-on-mobile-that-too-without-root-how-7b0848833c42
