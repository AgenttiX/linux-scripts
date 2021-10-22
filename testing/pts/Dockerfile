FROM phoronix/pts:latest
# TODO: Work in progress

# Download as much as possible as early as possible to avoid redownloading
RUN /phoronix-test-suite/phoronix-test-suite install \
    # Test suites
    pts/compilation \
    pts/compression \
    pts/cpu \
    pts/cryptography \
    pts/encoding \
    pts/linux-system \
    pts/machine-learning \
    pts/network \
    pts/opencl \
    pts/python \
    pts/scientific-computing \
    pts/server \
    pts/video-encoding \    # includes pts/av1
    pts/workstation \
    # Individual tests
    system/wireguard
