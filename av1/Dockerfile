FROM ubuntu:latest

# TODO work in progress

RUN apt-get update \
    && apt-get install -y \
        cmake \
        git

RUN git clone --depth=1 https://gitlab.com/AOMediaCodec/SVT-AV1.git \
    && cd SVT-AV1 \
    && cd Build \
    && cmake .. -G"Unix Makefiles" -DCMAKE_BUILD_TYPE=Release \
    && make -j $(nproc) \
    && make install

ENV LD_LIBRARY_PATH "${LD_LIBRARY_PATH}:/usr/local/lib"
ENV PKG_CONFIG_PATH "${PKG_CONFIG_PATH}:/usr/local/lib/pkgconfig"

RUN git clone --depth=1 https://github.com/FFmpeg/FFmpeg ffmpeg \
    && cd ffmpeg \
    && ./configure --enable-libsvtav1 \
    && make -j $(nproc)
