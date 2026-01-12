import os
import sys
from dotenv import load_dotenv
from cloudflare import Cloudflare

ENV_API_TOKEN_KEY = 'CLOUDFLARE_API_TOKEN'
ENV_CF_ZONE_KEY = 'CLOUDFLARE_ZONE'

def get_cf_zone(zone_name: str) -> str:
    res = client.zones.list(name=zone_name)
    if res.result_info.count == 0:
        raise Exception("Unable to find Zone")
    return res.result[0].id

def update_DNS_record(zone_id: str, name: str, new_value: str, record_type: str | None = None):
    print(f'\nUpdating record {name} => {new_value}')
    list_res = client.dns.records.list(
        zone_id=zone_id,
        name=name,
        type=record_type
    )

    # TODO: create new record if needed if list_res.

    for record in list_res.result:
        if record.content == new_value:
            print(f'No change (id={record.id})')
            continue
        # TODO: pages
        edit_res = client.dns.records.edit(
            dns_record_id=record.id,
            zone_id=zone_id,
            content=new_value
        )
        if edit_res.success:
            print(f'Success (id={record.id})')
        else:
            print(f'An error occurred while editing DNS record {name} ({record.id}):\n{edit_res}', file=sys.stderr)


if __name__ == '__main__':
    load_dotenv()

    if not os.environ[ENV_API_TOKEN_KEY]:
        # TODO
        os.quit(1)

    client = Cloudflare(api_token=os.environ[ENV_API_TOKEN_KEY])
    cf_zone = get_cf_zone(os.environ[ENV_CF_ZONE_KEY])

    for line in sys.stdin:
        name, address = line.split()
        update_DNS_record(cf_zone, name, address)
        

# print(get_cf_zone('bv-armstrong.dev'))
