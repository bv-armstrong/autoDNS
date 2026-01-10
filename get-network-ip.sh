#! /bin/bash
ip -j -4 address show $1 | jq -r ".[].addr_info[].local"
