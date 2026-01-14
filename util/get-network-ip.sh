#!/bin/bash
# ip -j -4 address show $1 | jq -r ".[].addr_info[0].local"

ip -j -4 address show | jq "[ .[] | {name: .ifname, address: .addr_info[0].local} ]"