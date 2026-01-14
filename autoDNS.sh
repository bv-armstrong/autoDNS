#!/bin/bash

source .env
# EXAMPLE .env File
#
# CLOUDFLARE_API_TOKEN=*****
# CLOUDFLARE_ZONE=example.com
# AUTO_DNS_CACHE_FILE=./cache.json
# NETWORK_IP_MAP_FILE

JSON_IP_MAP_STRUCTURE="
{
    network_name: .ifname, 
    address: .addr_info[0].local
}
"

# Update network mappings
ip -j -4 address show | jq "[ .[] | $JSON_IP_MAP_STRUCTURE ]" > $NETWORK_IP_MAP_FILE

# Run remapping
python3 ./autoDNS.py run
