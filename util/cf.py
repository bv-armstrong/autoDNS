from cloudflare import Cloudflare
from util import print_error


class CloudfareDNSManager:

    client: Cloudflare
    zone_id: str

    def __init__(self, api_token: str, zone_name: str) -> None:
        '''
        Initializes the CloudFlare API client.
        
        :param api_token: API Token used to access CloudFlare
        :type api_token: str
        :param zone_name: The name of the Cloudflare Zone (e.g., example.com)
        :type zone_name: str
        '''
        self.client = Cloudflare(api_token=api_token)
        self.set_zone(zone_name)


    def set_zone(self, zone_name: str) -> None:
        '''
        Loads a DNS Zone into the Cloudflare Client.
        Requires the client to have been initialized.

        :param zone_name: The name of the Cloudflare Zone (e.g., example.com)
        :type zone_name: str
        '''

        res = self.client.zones.list(name=zone_name)
        if res.result_info.count == 0:
            raise Exception(f"Unable to find Cloudflare Zone for {zone_name}")
        if res.result_info.count > 1:
            # TODO
            raise Exception(f"")
        
        self.zone_id = res.result[0].id


    def update_DNS_records(self, old_value: str, new_value: str) -> None:
        '''
        Updates the DNS type A records that point to old_value,
        remapping them to point to new_value
        
        :param old_value: The old IP address used to match records against
        :type old_value: str
        :param new_value: The new IP address to updatae the records to
        :type new_value: str
        '''
        print(f'\nUpdating records {old_value} => {new_value}')
        list_res = self.client.dns.records.list(
            zone_id=self.zone_id,
            content={'exact': old_value},
            type='A'
        )

        if list_res.result_info.count == 0:
            print(f"WARNING: No records found for {old_value}")

        for record in list_res.result:
            print(f'{record.name} ({record.id})')
            # TODO: pages
            edit_res = self.client.dns.records.edit(
                dns_record_id=record.id,
                zone_id=self.zone_id,
                content=new_value,
                type=record.type,
                name=record.name
            )
            if not edit_res.success:
                print_error(f'An error occurred while editing DNS record {record.name} ({record.id}), {old_value} => {new_value}:\n{edit_res}')
            else:
                print(edit_res)
            print()
