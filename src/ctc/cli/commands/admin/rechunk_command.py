from __future__ import annotations

import asyncio

import toolcli

from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': rechunk_command,
        'help': 'rechunk events by specific chunk size',
        'args': [
            {
                'name': 'contract',
                'nargs': '?',
                'help': 'address of contract emitting the event',
            },
            {
                'name': 'event',
                'nargs': '?',
                'default': None,
                'help': 'event hash',
            },
            {
                'name': '--network',
                'metavar': 'NAME_OR_ID',
                'help': 'network to rechunk events of',
            },
            {
                'name': '--all',
                'action': 'store_true',
                'dest': 'all_events',
                'help': 'whether to rechunk all events (can take a long time)',
            },
            {
                'name': '--start-block',
                'type': int,
                'help': 'start of block range to rechunk',
            },
            {
                'name': '--end-block',
                'type': int,
                'help': 'end of block range to rechunk',
            },
            {
                'name': '--chunk-bytes',
                'type': int,
                'required': True,
                'help': 'target number of bytes per chunk',
            },
            {
                'name': '--dry',
                'action': 'store_true',
                'help': 'perform a dry run where no changes are made',
            },
            {
                'name': '--verbose',
                'action': 'store_true',
                'help': 'increase verbosity',
            },
        ],
    }


def rechunk_command(
    contract: spec.Address,
    event: str,
    all_events: bool,
    start_block: int,
    end_block: int,
    chunk_bytes: int,
    dry: bool,
    verbose: bool,
    network: spec.NetworkReference,
) -> None:
    coroutine = run(
        contract_address=contract,
        event=event,
        all_events=all_events,
        start_block=start_block,
        end_block=end_block,
        chunk_bytes=chunk_bytes,
        dry=dry,
        verbose=verbose,
        network=network,
    )
    asyncio.run(coroutine)


async def run(
    contract_address: spec.Address,
    event: str,
    all_events: bool,
    start_block: int,
    end_block: int,
    chunk_bytes: int,
    dry: bool,
    verbose: bool,
    network: spec.NetworkReference,
) -> None:

    if all_events:

        await evm.async_rechunk_all_events(
            network=network,
            start_block=start_block,
            end_block=end_block,
            chunk_target_bytes=chunk_bytes,
            dry=dry,
            verbose=verbose,
        )

    elif contract_address is not None and event is not None:

        if evm.is_event_hash(event):
            event_name = event
            event_hash = None
        else:
            event_name = None
            event_hash = event

        await evm.async_rechunk_events(
            contract_address=contract_address,
            network=network,
            event_name=event_name,
            event_hash=event_hash,
            start_block=start_block,
            end_block=end_block,
            chunk_target_bytes=chunk_bytes,
            dry=dry,
            verbose=verbose,
        )

    else:
        raise Exception(
            'usage either `ctc rechunk --all` or `ctc rechunk contract_address event_hash`'
        )

    await rpc.async_close_http_session()

