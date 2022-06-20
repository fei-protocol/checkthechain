from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_symbol_command,
        'help': 'convert ERC20 address to symbol, or convert symbol to address',
        'args': [
            {'name': 'query', 'help': 'ERC20 address or symbol'},
        ],
    }


async def async_symbol_command(query: str) -> None:
    if evm.is_address_str(query):
        symbol = await evm.async_get_erc20_symbol(query)
        print(symbol)
    else:
        address = await evm.async_get_erc20_address(query)
        print(address)