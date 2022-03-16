from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec

old_pool_factory = '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae'
pool_factory = '0xb9fc157394af804a3578134a6585c0dc9cc990d4'

creation_blocks = {
    '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae': 11942404,
    '0xb9fc157394af804a3578134a6585c0dc9cc990d4': 12903979,
}


async def async_get_base_pools(
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
    verbose: bool = False,
):
    import pandas as pd

    if start_block is None:
        start_block = 12903979

    # gather data
    coroutines = []
    for factory in [old_pool_factory, pool_factory]:
        if start_block is None:
            factory_start_block = creation_blocks[factory]
        else:
            factory_start_block = start_block
        coroutine = evm.async_get_events(
            contract_address=factory,
            event_name='BasePoolAdded',
            start_block=factory_start_block,
            end_block=end_block,
            provider=provider,
            verbose=verbose,
        )
        coroutines.append(coroutine)
    dfs = await asyncio.gather(*coroutines)
    events = pd.concat(dfs)

    # format data
    events = events.sort_index()
    events = events[['contract_address', 'transaction_hash', 'arg__base_pool']]
    events = events.rename(
        columns={
            'contract_address': 'factory',
            'arg__base_pool': 'pool',
        }
    )

    return events


async def async_get_plain_pools(
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
    verbose: bool = False,
):
    if start_block is None:
        start_block = 12903979

    events = await evm.async_get_events(
        contract_address=pool_factory,
        event_name='PlainPoolDeployed',
        start_block=start_block,
        end_block=end_block,
        provider=provider,
        verbose=verbose,
    )
    events = events[
        [
            'transaction_hash',
            'contract_address',
            'arg__coins',
            'arg__A',
            'arg__fee',
            'arg__deployer',
        ]
    ]
    events = events.rename(
        columns={
            'contract_address': 'factory',
            'arg__coins': 'coins',
            'arg__A': 'A',
            'arg__fee': 'fee',
            'arg__deployer': 'deployer',
        }
    )
    return events


async def async_get_meta_pools(
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
    verbose: bool = False,
):
    import pandas as pd

    # gather data
    coroutines = []
    for factory in [old_pool_factory, pool_factory]:
        if start_block is None:
            factory_start_block: spec.BlockNumberReference = creation_blocks[
                factory
            ]
        else:
            factory_start_block = start_block
        coroutine = evm.async_get_events(
            contract_address=factory,
            event_name='MetaPoolDeployed',
            start_block=factory_start_block,
            end_block=end_block,
            provider=provider,
            verbose=verbose,
        )
        coroutines.append(coroutine)
    dfs = await asyncio.gather(*coroutines)
    events = pd.concat(dfs)

    # format data
    events = events.sort_index()
    events = events[
        [
            'transaction_hash',
            'contract_address',
            'arg__coin',
            'arg__base_pool',
            'arg__A',
            'arg__fee',
            'arg__deployer',
        ]
    ]
    events = events.rename(
        columns={
            'contract_address': 'factory',
            'arg__coin': 'coin',
            'arg__base_pool': 'base_pool',
            'arg__A': 'A',
            'arg__fee': 'fee',
            'arg__deployer': 'deployer',
        }
    )

    return events

