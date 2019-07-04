FROM alpine:3.9

LABEL maintainer="Guillaume Sottas"

# external arguments.
ARG branch=master

# setup environment variables.
ENV PROJECT_DIR=/usr/project
ENV BUILD_DIR=$PROJECT_DIR/docker_build

# install required binaries.
RUN apk update && apk add \
    build-base \
    cmake \
    doxygen \
    git \
    graphviz \
    libffi-dev \
    python3-dev

# checkout the project.
RUN git clone --branch ${branch} https://github.com/Sauci/CanTp $PROJECT_DIR

# install python requirements.
WORKDIR $PROJECT_DIR
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# generate the build system in debug mode.
WORKDIR $BUILD_DIR
RUN cmake .. -DCMAKE_BUILD_TYPE=Debug

# setup a shared volume.
WORKDIR $PROJECT_DIR
VOLUME ["$PROJECT_DIR"]
RUN cd $PROJECT_DIR
