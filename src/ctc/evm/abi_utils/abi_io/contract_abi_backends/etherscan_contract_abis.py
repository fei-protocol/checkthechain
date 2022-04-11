import asyncio
import json
import time

from ctc import config
from ctc import spec
from .... import address_utils
from ctc import directory


_last_request = {'time': None}


async def async_get_contract_abi_from_etherscan(contract_address, network=None):
    """fetch contract abi using etherscan"""
    api_key = None
    if network is None:
        network = config.get_default_network()
    if network != 'mainnet':
        api_key = '&apikey=' + config.get_default_api_key()

    import aiohttp

    print('fetching abi from etherscan:', contract_address)

    # ratelimit
    cadence = 6
    current_time = time.time()
    if (
        _last_request['time'] is not None
        and current_time < _last_request['time'] + cadence
    ):
        sleep_time = _last_request['time'] + cadence - current_time
        sleep_time = max(0, sleep_time)
        print('sleeping', sleep_time, 'seconds for etherscan ratelimit')
        asyncio.sleep(sleep_time)
    _last_request['time'] = time.time()

    if not address_utils.is_address_str(contract_address):
        raise Exception('not a valid address: ' + str(contract_address))
    default_networks = directory.load_networks_from_disk(use_default=True)
    network_explorer = default_networks[network]['block_explorer']

    url_template = 'http://api.{explorer}/api?module=contract&action=getabi&address={address}{key}&format=raw'
    
    abi_endpoint = url_template.format(explorer=network_explorer, address=contract_address, key=api_key)
    async with aiohttp.ClientSession() as session:
        async with session.get(abi_endpoint) as response:
            content = await response.text()
    if content == 'Contract source code not verified':
        raise spec.AbiNotFoundException()
    abi = json.loads(content)
    if isinstance(abi, dict) and abi.get('status') == '0':
        raise Exception(
            'could not obtain contract abi from etherscan for '
            + str(contract_address)
        )
    return abi

