FROM alpine:3.10

LABEL maintainer="Guillaume Sottas"

# setup environment variables.
ENV PROJECT_DIR=/usr/project

# install required binaries.
RUN apk update && apk add \
    bash \
    build-base \
    cmake \
    curl \
    doxygen \
    findutils \
    gdb \
    git \
    graphviz \
    libffi-dev \
    python3-dev

# install python requirements.
COPY ./requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# setup a shared volume.
WORKDIR $PROJECT_DIR
VOLUME ["$PROJECT_DIR"]
RUN cd $PROJECT_DIR
