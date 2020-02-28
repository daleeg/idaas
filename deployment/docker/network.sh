#!/bin/bash


create_network() {
    net_name=pandora
    docker network inspect $net_name | docker network create $net_name
}

create_network
