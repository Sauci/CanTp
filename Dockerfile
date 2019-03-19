FROM alpine:3.9 AS cmake_builder

LABEL maintainer="Guillaume Sottas"

ENV HOME=/usr \
    TOOL=$HOME/tool \
    PROJECT_DIR=$HOME/project \
    CMAKE_BUILD_DIR=$HOME/build/cmake \
    CMAKE_INSTALL_DIR=$HOME/install/cmake

RUN apk update && apk add build-base git linux-headers make

WORKDIR $CMAKE_BUILD_DIR
RUN git clone -b v3.14.0 --depth 1 https://github.com/Kitware/CMake.git $CMAKE_BUILD_DIR && \
    ./bootstrap --prefix=$CMAKE_INSTALL_DIR && make install -j 8


FROM alpine:3.9 AS env_cantp

# get cmake from cmake_uilder and add bin directory to PATH.
COPY --from=cmake_builder $CMAKE_INSTALL_DIR $TOOL/cmake
ENV PATH="${TOOL}/cmake/bin:${PATH}"

# get build utilities (compiler, linker,...).
RUN apk update && apk add build-base cmake python python3 python-dev python3-dev swig

# copy CanTp project.
WORKDIR $PROJECT_DIR/cantp
COPY . .
RUN mkdir build && cd build && cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON && make all

CMD ["/bin/sh"]
VOLUME ["$PROJECT_DIR/cantp"]
