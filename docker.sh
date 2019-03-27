#!/usr/bin/env bash
docker build --tag cantp .
docker run -it --name cantp -p 4444:4444 -v "$(pwd)":/usr/project cantp
