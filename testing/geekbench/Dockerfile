# Using GPU functionality requires a GPU-enabled Docker platform and container image
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker
# To run this image with GPU support enabled, use
# nvidia-docker run -it <image_name>

FROM nvidia/cuda:11.4.2-base-ubuntu20.04

WORKDIR /geekbench

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

COPY ./download_geekbench.sh /geekbench/
RUN /geekbench/download_geekbench.sh

# For debugging
# CMD ["/geekbench/Geekbench-5.2.0-Linux/geekbench5", "--compute-list"]
