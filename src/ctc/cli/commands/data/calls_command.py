from __future__ import annotations

import typing

import toolcli

from ctc import binary
from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.cli import cli_utils

command_help = """output the result of multiple calls"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_calls_command,
        'help': command_help,
        'args': [
            {'name': 'args', 'nargs': '*', 'help': '<see above>'},
            {
                'name': '--addresses',
                'nargs': '+',
                'help': 'addresses to point calls toward',
            },
            {'name': '--blocks', 'nargs': '+', 'help': 'block range for calls'},
            {'name': '--block', 'help': 'block number for calls'},
            {
                'name': '--quiet',
                'action': 'store_true',
                'help': 'omit summary, only output function result',
            },
            {
                'name': '--output',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
            {
                'name': '--from',
                'help': 'address that calls should come from',
                'dest': 'from_address',
            },
        ],
        'examples': {
            '<address> <function_name> [<function_parameters>] --blocks <blocks>': {
                'description': 'version 1: same call across multiple blocks',
                'runnable': False,
            },
            '<function_name> [<function_parameters>] --addresses <addresses> [--block block]': {
                'description': 'version 2: same call across multiple addresses',
                'runnable': False,
            },
        },
    }


async def async_calls_command(
    *,
    args: typing.Sequence[str],
    addresses: typing.Optional[typing.Sequence[str]],
    blocks: typing.Optional[typing.Sequence[str]],
    block: typing.Optional[str],
    quiet: bool,
    output: str,
    overwrite: bool,
    from_address: typing.Optional[spec.Address],
) -> None:

    import pandas as pd

    if addresses is not None:
        addresses = await evm.async_resolve_addresses(addresses, block=block)
    from_address = await evm.async_resolve_address(from_address, block=block)

    if blocks is not None and addresses is not None:
        raise Exception('cannot specify both --blocks or --to-addresses')
    if blocks is None and addresses is None:
        raise Exception('must specify either --blocks or --to-addresses')

    if blocks is not None:
        if block is not None:
            raise Exception('cannot specify both --block and --blocks')

        to_address, function_name, *function_parameters = args

        block_numbers = await cli_utils.async_resolve_block_range(blocks)

        # fetch data
        results = await rpc.async_batch_eth_call(
            to_address=to_address,
            function_name=function_name,
            function_parameters=function_parameters,
            block_numbers=block_numbers,
            from_address=from_address,
        )

        # get output names
        function_abi = await evm.async_get_function_abi(
            contract_address=to_address,
            function_name=function_name,
        )
        output_names = binary.get_function_output_names(
            function_abi, human_readable=True
        )

        # format into dataframe
        df = pd.DataFrame(results, index=block_numbers)
        df.index.name = 'block'
        df.columns = output_names

    elif addresses is not None:
        if block is None:
            block = 'latest'

        function_name, *function_parameters = args

        # assert that all address functions have the same number of outputs
        function_abi = await evm.async_get_function_abi(
            contract_address=addresses[0],
            function_name=function_name,
        )
        n_outputs = len(function_abi['outputs'])
        for to_address in addresses[1:]:
            other_function_abi = await evm.async_get_function_abi(
                contract_address=to_address,
                function_name=function_name,
            )
            if len(other_function_abi['outputs']) != n_outputs:
                print('to-addresses do no have same number of function outputs')

        # fetch data
        results = await rpc.async_batch_eth_call(
            to_addresses=addresses,
            function_name=function_name,
            function_parameters=function_parameters,
            block_number=block,
            from_address=from_address,
        )

        # name based on first contract's abi
        output_names = binary.get_function_output_names(
            function_abi, human_readable=True
        )

        df = pd.DataFrame(results, index=addresses)
        df.index.name = 'to_address'
        df.columns = output_names

    else:
        raise Exception('must specify either --blocks or --to-addresses')

    cli_utils.output_data(data=df, output=output, overwrite=overwrite)
