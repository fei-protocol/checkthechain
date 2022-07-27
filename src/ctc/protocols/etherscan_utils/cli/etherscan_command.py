from __future__ import annotations

import subprocess

import toolcli

from ctc import evm
from ctc.protocols import etherscan_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_etherscan_command,
        'args': [
            {
                'name': 'query',
                'help': 'address / tx / block / ERC20 symbol / ens',
            },
            {
                'name': '--abi',
                'help': 'output only the json ABI of an address',
                'action': 'store_true',
            },
        ],
        'help': 'open etherscan query in browser or fetch',
        'examples': {
            '0xd3181ddbb2cea7b4954b8d4a05dbf85d8fc36aef': {'skip': True},
            '0x146063226f2bc60ab02fff825393555672ff505afb352ff11b820355422ba31e': {'skip': True},
            '14000000': {'skip': True},
            'DAI': {'skip': True},
            'vitalik.eth': {'skip': True},
        },
    }


async def async_etherscan_command(query: str, abi: bool) -> None:

    is_address = False
    if query.startswith('0x') and len(query) == 42:
        url = etherscan_utils.create_address_url(query)
        address = query
        is_address = True
    elif query.startswith('0x') and len(query) == 66:
        url = etherscan_utils.create_transaction_url(query)
    elif query.isnumeric():
        url = etherscan_utils.create_block_url(int(query))
    elif query.endswith('.eth'):
        from ctc.protocols import ens_utils

        address = await ens_utils.async_resolve_name(query)
        url = etherscan_utils.create_address_url(address)
        is_address = True
    else:
        try:
            address = await evm.async_get_erc20_address('FEI')
            url = etherscan_utils.create_address_url(address)
            is_address = True
        except Exception:
            raise Exception('unknown query: ' + str(query))

    if abi:
        if is_address:
            import json

            raw_abi = await etherscan_utils.async_get_contract_abi(
                address, verbose=False
            )
            print(json.dumps(raw_abi, sort_keys=True, indent=4))
        else:
            raise Exception('can only use --abi for addresses')
    else:
        subprocess.call(['xdg-open', url])
