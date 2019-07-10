FROM alpine:3.10

LABEL maintainer="Guillaume Sottas"

# setup environment variables.
ENV PROJECT_DIR=/usr/project

# install required binaries.
RUN apk update && apk add \
    build-base \
    cmake \
    curl \
    doxygen \
    git \
    graphviz \
    libffi-dev \
    openssl-dev \
    zlib-dev

# build python from sources.
RUN curl -s -O https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tar.xz && \
    tar xf Python-3.6.9.tar.xz && \
    cd Python-3.6.9 && \
    ./configure && make -j 8 && make install

# install python requirements.
COPY ./requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# setup a shared volume.
WORKDIR $PROJECT_DIR
VOLUME ["$PROJECT_DIR"]
RUN cd $PROJECT_DIR
