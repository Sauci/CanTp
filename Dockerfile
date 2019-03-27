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

# copy CanTp project and generate makefile.
#WORKDIR $PROJECT_DIR/cantp
#COPY . .
#RUN mkdir build && cd build && cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON && make all

WORKDIR $PROJECT_DIR
VOLUME ["$PROJECT_DIR"]
RUN cd $PROJECT_DIR

#EXPOSE 4444
