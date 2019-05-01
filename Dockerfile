FROM alpine:3.9

LABEL maintainer="Guillaume Sottas"

ENV PROJECT_DIR=/usr/project/

RUN apk update && apk add \
    build-base \
    cmake \
    git \
    libffi \
    libffi-dev \
    python3 \
    python3-dev

RUN git clone https://github.com/Sauci/CanTp $PROJECT_DIR

WORKDIR $PROJECT_DIR
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
RUN mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Debug

WORKDIR $PROJECT_DIR
VOLUME ["$PROJECT_DIR"]
RUN cd $PROJECT_DIR

EXPOSE 4567
