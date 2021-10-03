# Using GPU functionality requires a GPU-enabled Docker platform and container image
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker
# To run this image with GPU support enabled, use
# nvidia-docker run -it <image_name>

FROM nvidia/cuda:11.4.2-base-ubuntu20.04

RUN apt-get update \
    && apt-get install -y \
        wget \
        # This resolves the error
        # [1111/070916:FATAL:src/halogen/cuda/cuda_library.cpp(1713)] Failed to load nvmlInit_v2: /geekbench/Geekbench-5.2.0-Linux/geekbench_x86_64: undefined symbol: nvmlInit_v2
        libnvidia-compute-470 \
        # These resolve the error
        # [1111/073032:WARNING:src/halogen/cl/opencl_library.cpp(691)] Cannot find or load OpenCL library.
        libnvidia-gl-470 \
        ocl-icd-libopencl1 \
        # This should enable Vulkan support (but does not work yet)
        mesa-vulkan-drivers

RUN mkdir /geekbench \
    && cd /geekbench \
    && wget https://cdn.geekbench.com/Geekbench-5.4.0-Linux.tar.gz -O geekbench5.tar.gz \
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

# For debugging
# CMD ["/geekbench/Geekbench-5.2.0-Linux/geekbench5", "--compute-list"]
