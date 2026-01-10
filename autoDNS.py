import os
import logging
from dotenv import load_dotenv
from cloudflare import Cloudflare

load_dotenv()

client = Cloudflare(
    api_token=os.getenv("CLOUDFLARE_API_TOKEN")
)

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

print(get_cf_zone('bv-armstrong.dev'))
