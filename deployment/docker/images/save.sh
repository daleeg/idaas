#!/bin/bash

rm -rf *.tar

docker save nginx:latest > nginx.tar
docker save redis:latest > redis-web.tar
docker save mysql:5.7 > mysql.tar
docker save pandora:latest > pandora.tar
