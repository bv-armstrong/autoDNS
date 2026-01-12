#!/bin/bash

tmp_cache="/var/tmp/audoDNS.cache"
cache="./.cache"
conf="./conf.d/*.conf"

# Map the given .conf files to DNS records (name => ip address)
ls $conf | ./util/map-records.sh | sort > $tmp_cache
echo "The following mappings have been generated from configuration $conf:"
cat $tmp_cache
echo

touch $cache # Create file if it doesn't exist to prevent errors

# Detects changes by comparing output to cached values
# Then pass changes into python script
comm -23 $tmp_cache $cache | python3 util/autoDNS.py

# Update cache
mv $tmp_cache $cache
