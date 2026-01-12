#!/bin/bash

while read filename; do
    source $filename
    address=$(./util/get-network-ip.sh $network)
    echo $record $address
done