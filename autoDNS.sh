#!/bin/bash

tmp_cache="/var/tmp/audoDNS.cache"
cache="./.cache"
conf="./conf.d/*.conf"

# Create a new, empty temporary file to store records in
ls $conf | ./util/map-records.sh | sort > $tmp_cache
echo $tmp_cache
touch $cache

comm -23 $tmp_cache $cache

mv $tmp_cache $cache
