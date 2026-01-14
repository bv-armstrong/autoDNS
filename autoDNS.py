import argparse
import os
import json
from dotenv import load_dotenv
from util import print_error



### CONSTANTS ###

# Environment Variable Keys
ENV_API_TOKEN_KEY = 'CLOUDFLARE_API_TOKEN'
ENV_CF_ZONE_KEY = 'CLOUDFLARE_ZONE'
ENV_CACHE_FILE_KEY = 'AUTO_DNS_CACHE_FILE'
ENV_IP_MAP_FILE_KEY = 'NETWORK_IP_MAP_FILE'



### CLASS DEFINITIONS ###

class NetworkMapEntry:
    '''
    Encapsulates Mapping between a network and a device's corresponding IP address on that network.
    '''

    name: str
    address: str

    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address
    
    # Static

    NAME_KEY = 'network_name'
    ADDRESS_KEY = 'address'

    def from_dict(d: dict):
        '''
        Loads a Map Entry from a Dictionary.
        Used when importing mapping from JSON.
        
        :param d: The dictionary mapping attribute_name to attribute
        :type d: dict
        '''
        return NetworkMapEntry(d[NetworkMapEntry.NAME_KEY], d[NetworkMapEntry.ADDRESS_KEY])


class CacheEntry:
    '''
    Encapsulates an entry in program's cache.
    This cache stores a user-defined name for a network and a device's current IP address
    on that network.
    '''

    name: str
    network_name: str
    address: str

    def __init__(self, name: str, network_name: str, address: str):
        self.name = name
        self.network_name = network_name
        self.address = address
    

    # Static

    NAME_KEY = 'name'
    NETWORK_KEY = 'network_name'
    ADDRESS_KEY = 'address'


class DnsManager:
    '''
    Generic class for interacting with an Application API to manage DNS records.
    The idea is to allow further customization for different DNS managers, which
    can be loaded only when needed.
    '''

    def remap_records(self, old_value: str, new_value: str) -> None:
        '''
        Default implementation for DNS Manager to remap records.
        Calls a function load_dns_manager, which loads the DNS Manager
        according to the Environment and reassigns the global dns_manager.
        Finally, it calls the remap_records function on the new dns_manager.
        
        :param self: Description
        :param old_value: The old IP address, used to look up records to change
        :type old_value: str
        :param new_value: The new IP address to set the DNS records to point to
        :type new_value: str
        '''
        load_dns_manager()
        dns_manager.remap_records(old_value, new_value)



### GLOBAL VARIABLES ###

cache: list[CacheEntry]
ip_map: dict[str, str]
dns_manager = DnsManager()



### SETUP FUNCTIONS ###

def load_cache() -> None:
    '''
    Loads the cache from the previous time the program ran.
    Requires the {ENV_CACHE_FILE} environment variable to have been set
    and a corresponding cache file to have been created.
    '''
    global cache

    try:
        with open(os.environ[ENV_CACHE_FILE_KEY]) as cache_file:
            cache = json.load(cache_file, object_hook=lambda d: CacheEntry(d[CacheEntry.NAME_KEY], d[CacheEntry.NETWORK_KEY], d[CacheEntry.ADDRESS_KEY] if CacheEntry.ADDRESS_KEY in d else ''))
    except OSError as e:
        print_error(e.strerror)
        cache = []


def write_cache() -> None:
    '''
    Writes the current cache to a file set by the {ENV_CACHE_FILE}
    environment variable.
    '''
    print("Writing cache")
    with open(os.environ[ENV_CACHE_FILE_KEY], 'w') as cache_file:
        json.dump([obj.__dict__ for obj in cache], cache_file)


def load_ip_mappings() -> None:
    '''
    Loads a set of IP Mappings from stdin.
    '''
    global ip_map

    print("Reading IP Address Map:")
    with open(os.environ[ENV_IP_MAP_FILE_KEY]) as file:
        mappings = json.load(file, object_hook=NetworkMapEntry.from_dict)

    ip_map = {}
    for entry in mappings:
        print(f'\t{entry.name} = {entry.address}')
        ip_map[entry.name] = entry.address

    print()


def load_dns_manager() -> None:
    '''
    Loads a DNS manager according to environment settings.
    Sets the global dns_manager variable to point to this new manager.
    '''
    global dns_manager

    # TODO: Support other managers?
    from util.cf import CloudfareDNSManager
    
    if not os.environ[ENV_API_TOKEN_KEY]:
        raise RuntimeError(f'{ENV_API_TOKEN_KEY} evironment variable not set')
        
    dns_manager = CloudfareDNSManager(os.environ[ENV_API_TOKEN_KEY], os.environ[ENV_CF_ZONE_KEY])

    # Point the remap_records interface method to refer to the CloudfareDNSManager's update_DNS_records
    dns_manager.remap_records = dns_manager.update_DNS_records



### FUNCTIONS ###

def add_mapping(network_name: str, name: str | None = None) -> None:
    '''
    Adds a new network mapping to the cache.
    
    :param network_name: The name of the network, associated with an IP Adress in the ip_mapping dictionary
    :type network_name: str
    :param name: A name associated with this entry, for utility purposes only. Defaults to network_name.
    :type name: str | None
    '''
    if name == None:
        name = network_name
    
    if network_name not in ip_map:
        raise Exception(f'{network_name} not found in ip mappings')
    
    for entry in cache:
        if entry.network_name == network_name:
            print(f'{network_name} already in cache')
            entry.name = name
            entry.address = ip_map[network_name]
            return
        
    cache.append(CacheEntry(name, network_name, ip_map[network_name]))


def autoDNS() -> None:
    '''
    Runs the main AutoDNS program.

    Given a set of IP addresses, detects if any of those IP addresses have changed since the previous
    iteration of the program. If they have, uses a DNS manager's API to update any records that point
    to the old IP address to point to the new IP address.

    Requires a cache and network mapping to have been loaded.
    '''
    for entry in cache:
        new_address = ip_map[entry.network_name]
        if new_address == entry.address:
            print(f'Skipping {entry.name} ({entry.network_name} = {entry.address} remains unchanged)')
            continue
        if entry.address:
            dns_manager.remap_records(entry.address, new_address)
        else:
            print(f'Caching address {new_address} for {entry.name} ({entry.network_name})')
        entry.address = new_address
    
    print()

    print("No changes\n")    



### MAIN ###

def parse_args():
    '''
    Reads Command Line Arguments

    TODO: Add help documentation
    '''
    parser = argparse.ArgumentParser(
        # prog='Auto DNS'
    )
    sub = parser.add_subparsers()
    
    add_parser = sub.add_parser('add')
    add_parser.add_argument(CacheEntry.NETWORK_KEY)
    add_parser.add_argument(CacheEntry.NAME_KEY, nargs='?', default=None)
    add_parser.set_defaults(func=lambda args: add_mapping(args[CacheEntry.NETWORK_KEY], name=args[CacheEntry.NAME_KEY]))

    run_parser = sub.add_parser('run')
    run_parser.set_defaults(func=lambda args: autoDNS())

    return parser.parse_args()


if __name__ == '__main__':
    # Read command line arguments
    args = parse_args()
    print(args)

    # Load environment variables
    load_dotenv()

    # Load cache (from previous run) and new IP Mappings
    load_cache()
    load_ip_mappings()

    # Run program specified by command
    args.func(vars(args))

    # Update cache
    write_cache()

        