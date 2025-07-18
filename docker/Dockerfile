FROM ubuntu:latest

# To build:
# > docker build -t ubuntu-shell --build-arg UID=$(id -u) --build-arg USER=$(whoami) .
# or
# > docker build -t ubuntu-shell -f Dockerfile --no-cache --progress plain --build-arg UID=$UID --build-arg USER=$USER .

# To run:
# > docker run --hostname toolmate -it ubuntu-shell

# get UID/GID of host user for remapping to access bindmounts on host
ARG USER
ARG UID

# Set the TERM environment variable
ENV TERM=xterm-256color

# Update package lists
RUN apt update

# Install necessary packages
RUN apt install -y \
    bash \
    curl \
    vim \
    net-tools \
    sudo \
    python3 \
    python3-setuptools python3-pip python3-dev python3-venv portaudio19-dev ffmpeg wget git wget w3m lynx nano micro sqlite3 libsqlite3-dev \
    libxcb-cursor0 pulseaudio-utils alsa-base alsa-utils mpg123 espeak software-properties-common golang-go build-essential

# Set hostname
RUN echo "toolmate" > /etc/hostname

# Create the user and group, if current username is not `ubuntu`
RUN if [ ${USER} != "ubuntu" ]; then \
        useradd -m -d /home/${USER} -s /bin/bash ${USER}; \
    fi

# Add user to sudo group
RUN usermod -aG sudo ${USER}

RUN echo ${USER}" ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}

WORKDIR /home/${USER}

RUN \
    # support container sound output
    echo 'export PULSE_SERVER=127.0.0.1' >> /home/${USER}/.bashrc && \
    # install rust
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    export PATH=/home/${USER}/.cargo/bin:$PATH && \
    # uncomment the following two lines to install ollama
    #curl -fsSL https://ollama.com/install.sh | sh && \
    #echo 'export OLLAMA_HOST=0.0.0.0' >> /home/${USER}/.bashrc && \
    # configure local bin
    mkdir -p .local/bin && \
    echo "export PATH=$HOME/.local/bin:$PATH" >> /home/${USER}/.bashrc
    # uncomment the following line to install fabric
    #curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-arm64 > /home/${USER}/.local/bin/fabric && chmod +x /home/${USER}/.local/bin/fabric

RUN \
    mkdir -p /home/${USER}/apps && \
    cd /home/${USER}/apps && \
    python3 -m venv toolmate && \
    . toolmate/bin/activate && \
    pip install --upgrade toolmate==0.5.13 flaml[automl] ag2[autobuild]>=0.3.1

# Set the default command
#CMD ["/bin/bash"]
CMD ["sh", "-c", ". apps/toolmate/bin/activate && apps/toolmate/toolmate"]
