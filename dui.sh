#!/bin/sh
docker build . -t dui
docker run \
  -v $PWD/config:/config:ro \
  -v $PWD/data:/data \
  -v $PWD/cache:/cache \
  dui
