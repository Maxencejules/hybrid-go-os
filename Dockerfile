FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    nasm \
    gcc \
    gccgo \
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust nightly with rust-src (required for build-std)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --default-toolchain nightly --component rust-src
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /src
