#!/usr/bin/env bash
echo "Begin autoDNS"
date

AUTO_DNS_DIRECTORY=$(dirname $(realpath $BASH_SOURCE))
cd $AUTO_DNS_DIRECTORY

source .env
# EXAMPLE .env File
#
# CLOUDFLARE_API_TOKEN=*****
# CLOUDFLARE_ZONE=example.com
# AUTO_DNS_CACHE_FILE=./cache.json
# NETWORK_IP_MAP_FILE=
# AUTO_DNS_LOG_FILE=

JSON_IP_MAP_STRUCTURE="
{
    network_name: .ifname, 
    address: .addr_info[0].local
}
"

# Update network mappings
ip -j -4 address show \
| jq "[ .[] | $JSON_IP_MAP_STRUCTURE ]" \
| tee ./network-mappings.log \
| ./.venv/bin/python3 ./autoDNS.py $@ 2>&1 \
| tee $AUTO_DNS_LOG_FILE

echo "End autoDNS"
