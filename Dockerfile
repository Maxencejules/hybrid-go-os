FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    nasm \
    gcc \
    libc6-dev \
    binutils \
    xorriso \
    qemu-system-x86 \
    python3 \
    python3-pytest \
    git \
    make \
    dos2unix \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
