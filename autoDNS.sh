#!/bin/bash

# CLOUDFLARE_API_TOKEN=*****
# CLOUDFLARE_ZONE=example.com
# AUTO_DNS_CACHE_FILE=./cache.json
source .env


JSON_IP_MAP_STRUCTURE="
{
    network_name: .ifname, 
    address: .addr_info[0].local
}
"

# Get network mappings
ip -j -4 address show | jq "[ .[] | $JSON_IP_MAP_STRUCTURE ]" > $NETWORK_IP_MAP_FILE
python3 ./util/autoDNS.py run

# OLD 
# TODO: Delete

# Map the given .conf files to DNS records (name => ip address)
# ls $conf | ./util/map-records.sh | sort > $tmp_cache
# echo "The following mappings have been generated from configuration $conf:"
# cat $tmp_cache
# echo

# touch $cache # Create file if it doesn't exist to prevent errors

# # Detects changes by comparing output to cached values
# # Then pass changes into python script
# comm -23 $tmp_cache $cache | python3 util/autoDNS.py

# # Update cache
# mv $tmp_cache $cache
