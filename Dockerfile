FROM alpine:3.9 AS env_cantp

LABEL maintainer="Guillaume Sottas"

ENV PROJECT_DIR=/usr/project/

# get build utilities (compiler, linker,...).
RUN apk update && apk add \
    build-base \
    cmake \
    libffi \
    libffi-dev \
    mercurial \
    nano \
    python3 \
    python3-dev

# install required python packages.
RUN pip3 install --upgrade pip && \
    pip3 install cffi gcovr pcpp pytest

WORKDIR $PROJECT_DIR/prebuilt
COPY . .
RUN mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Debug -Denable_test=ON && \
    make sdist_install && \
    ctest -V

WORKDIR $PROJECT_DIR
VOLUME ["$PROJECT_DIR"]
RUN cd $PROJECT_DIR
