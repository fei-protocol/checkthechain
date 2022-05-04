from __future__ import annotations

from ctc import rpc
from ctc import spec


feed_registry = {
    'mainnet': '0x47fb2585d2c56fe188d0e6ec628a38b74fceeedf',
    'kovan': '0xAa7F6f7f507457a1EE157fE97F6c7DB2BEec5cD0',
}

feed_registry_asset_addresses = {
    'BTC': '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    'ETH': '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    'USD': '0x0000000000000000000000000000000000000348',
    'GBP': '0x000000000000000000000000000000000000033a',
    'EUR': '0x00000000000000000000000000000000000003d2',
}

feed_registry_address_assets = {
    v: k for k, v in feed_registry_asset_addresses.items()
}

feed_registry_abis = {
    'getFeed': {
        'inputs': [
            {'internalType': 'address', 'name': 'base', 'type': 'address'},
            {'internalType': 'address', 'name': 'quote', 'type': 'address'},
        ],
        'name': 'getFeed',
        'outputs': [
            {
                'internalType': 'contract AggregatorV2V3Interface',
                'name': 'aggregator',
                'type': 'address',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getPhaseRange': {
        'inputs': [
            {'internalType': 'address', 'name': 'base', 'type': 'address'},
            {'internalType': 'address', 'name': 'quote', 'type': 'address'},
            {'internalType': 'uint16', 'name': 'phaseId', 'type': 'uint16'},
        ],
        'name': 'getPhaseRange',
        'outputs': [
            {
                'internalType': 'uint80',
                'name': 'startingRoundId',
                'type': 'uint80',
            },
            {
                'internalType': 'uint80',
                'name': 'endingRoundId',
                'type': 'uint80',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
}


async def async_get_registry_feed(
    base: str,
    quote: str,
    provider: spec.ProviderSpec = None,
):
    network = rpc.get_provider_network(provider)
    registry_address = feed_registry[network]

    return await rpc.async_eth_call(
        to_address=registry_address,
        function_abi=feed_registry_abis['getFeed'],
        function_parameters=[base, quote],
        provider=provider,
    )


async def async_get_phase_range(
    base: str,
    quote: str,
    phase: int,
    provider: spec.ProviderSpec = None,
) -> None:
    network = rpc.get_provider_network(provider)
    registry_address = feed_registry[network]

    result = await rpc.async_eth_call(
        to_address=registry_address,
        function_abi=feed_registry_abis['getPhaseRange'],
        function_parameters=[base, quote, phase],
        provider=provider,
    )

    return result

