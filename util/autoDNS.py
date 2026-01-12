import os
import logging
from dotenv import load_dotenv
from cloudflare import Cloudflare

ENV_API_KEY = 'CLOUDFLARE_API_TOKEN'
ENV_ZONE_ID_KEY = 'CLOUDFLARE_ZONE_ID'

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='AutoDNS'
        description='TODO'
    )

    parser.add_argument('record', help='The name of the DNS record.')
    parser.add_argument('address')

    zone_group = parser.add_mutually_exclusive_group(required=False)
    zone_group.add_argument(
        '-Z', '--zone',
        help='Cloudflare zone name (example.com).')
    zone_group.add_argument(
        '-z', '--zone-id', 
        help='Either the Cloudflare zone name (example.com) or the zone id.')
    
    parser.add_argument(
        '-e', '--env',
        default='.env',
        help='Environment file.'
    )

    parser.add_argument(
        '-c', '--cache-env',
        action='store_true',
        help='TODO'
    )

    return parser.parse_args()

def get_cf_zone(zone_name: str) -> str:
    res = client.zones.list(name=zone_name)
    if res.result_info.count == 0:
        raise Exception("Unable to find Zone")
    return res.result[0].id

def update_DNS_record(zone_id: str, name: str, record_type: str | None = None, new_value: str):
    list_res = client.dns.records.list(
        zone_id=zone_id,
        name=name,
        type=record_type
    )

    for record in list_res.result:
        if record.content == new_value:
            continue
        # TODO: pages
        edit_res = client.dns.records.edit(
            dns_record_id=record.id,
            zone_id=zone_id,
            content=new_value
        )
        if not edit_res.success:
            logging.error(f'An error occurred while editing DNS record {name} ({record.id})')
            logging.error(edit_res)


if __name__ == '__main__':
    opts = parse_arguments()

    load_dotenv(opts.env)

    if not os.environ[ENV_API_TOKEN_KEY]:
        # TODO
        os.quit(1)

    client = Cloudflare(api_token=os.environ[ENV_API_KEY])
    if opts.zone_id:
        os.environ[ENV_ZONE_ID_KEY] = opts.zone_id
    elif opts.zone:
        os.environ[ENV_ZONE_ID_KEY] = get_cf_zone(opts.zone)
    
    # if not os.environ[ENV_ZONE_ID_KEY]:



    # if opts.cache:
        

# print(get_cf_zone('bv-armstrong.dev'))
