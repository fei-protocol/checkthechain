from __future__ import annotations

import os

import toolcli

from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_address_command,
        'help': """summarize address

for contracts, will display ABI
""",
        'args': [
            {'name': 'address', 'help': 'address to get summary of'},
            {
                'name': ['-v', '--verbose'],
                'action': 'store_true',
                'help': 'emit extra output',
            },
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'emit abi in raw json',
            },
            {
                'name': '--network',
                'metavar': 'NAME_OR_ID',
                'help': 'network name or id to scan address of',
            },
        ],
    }


async def async_address_command(
    address: spec.Address, verbose: bool | int, network: str, raw: bool
) -> None:
    try:
        max_width = os.get_terminal_size().columns
    except OSError:
        max_width = 80

    if verbose:
        verbose = 2
    await evm.async_print_address_summary(
        address=address,
        verbose=verbose,
        max_width=max_width,
        raw=raw,
        provider={'network': network},
    )
    await rpc.async_close_http_session()

