# Using GPU functionality requires a GPU-enabled Docker platform and container image
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker
FROM nvidia/cuda:11.1-base

# Todo: fix GPU support by installing some libraries?
RUN apt-get update && apt-get install -y wget

RUN mkdir /geekbench \
    && cd /geekbench \
    && wget https://cdn.geekbench.com/Geekbench-5.2.0-Linux.tar.gz -O geekbench5.tar.gz \
    && wget https://cdn.geekbench.com/Geekbench-4.3.3-Linux.tar.gz -O geekbench4.tar.gz \
    && wget https://cdn.primatelabs.com/Geekbench-3.4.2-Linux.tar.gz -O geekbench3.tar.gz \
    && wget https://cdn.primatelabs.com/Geekbench-2.4.3-Linux.tar.gz -O geekbench2.tar.gz \
    && tar -xzf geekbench5.tar.gz \
    && tar -xzf geekbench4.tar.gz \
    && tar -xzf geekbench3.tar.gz \
    && tar -xzf geekbench2.tar.gz \
    && rm geekbench*.tar.gz \
    && mv ./dist/* . \
    && rm ./dist -r
