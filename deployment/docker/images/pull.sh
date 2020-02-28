#!/bin/bash

docker pull nginx:latest

docker pull redis:latest

docker pull mysql:5.7

docker pull python:3.8

pushd pandora >/dev/null
docker build --rm -t pandora:latest .
popd >/dev/null
