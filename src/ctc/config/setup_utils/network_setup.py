from __future__ import annotations

import typing
from typing_extensions import TypedDict
import urllib.parse

import toolcli

from ctc import rpc
from ctc import spec
from ctc import directory
from ctc.toolbox import nested_utils
from .. import config_read


class _NetworkData(TypedDict):
    networks: dict[spec.NetworkName, spec.NetworkMetadata]
    providers: dict[spec.ProviderName, spec.Provider]
    network_defaults: spec.ConfigNetworkDefaults


def setup_networks(styles: typing.Mapping[str, str]) -> tuple[_NetworkData, bool]:
    print()
    print()
    toolcli.print('## Network Setup', style=styles['header'])

    print()
    print('The following networks are already added:')
    default_networks = directory.load_networks_from_disk(use_default=True)
    for network_name, network_metadata in default_networks.items():
        print('-', network_name)

    # add new networks
    networks: dict[spec.NetworkName, spec.NetworkMetadata] = {}
    while toolcli.input_yes_or_no(
        '\nWould you like to add additional networks? ',
        style=styles['question'],
        default='no',
    ):

        go_back = False
        valid_answer = False
        while not valid_answer:
            name = toolcli.input_prompt(
                'Network name? (to go back, input a blank line) ',
                style=styles['question'],
            )
            if name == '':
                go_back = True
                break
            elif name in default_networks or name in networks:
                answer = toolcli.input_yes_or_no(
                    'Network with this name already exists. Overwrite? ',
                    style=styles['question'],
                )
                if answer:
                    valid_answer = True
            else:
                valid_answer = True
        if go_back:
            break

        network_id = toolcli.input_int(
            'Network chain_id? ', style=styles['question']
        )
        block_explorer = toolcli.input_prompt(
            'Network block explorer? ', style=styles['question']
        )

        if name in networks:
            print()
            print('Overwriting network with name', name)

        networks[name] = {
            'name': name,
            'chain_id': network_id,
            'block_explorer': block_explorer,
        }

    # set default network
    choices_set = set(networks.keys()) | set(default_networks.keys())
    choices = sorted(choices_set)
    print()
    default_network_index = toolcli.input_number_choice(
        prompt='Which network to use as default?',
        choices=choices,
        default='mainnet',
        style=styles['question'],
    )
    default_network = choices[default_network_index]

    # get providers
    all_networks = dict(default_networks, **networks)
    providers = specify_providers(
        all_networks=all_networks,
        config_networks=networks,
        default_network=default_network,
        styles=styles,
    )
    network_defaults = specify_network_defaults(
        default_network=default_network,
        providers=providers,
        styles=styles,
    )

    data: _NetworkData = {
        'networks': networks,
        'providers': providers,
        'network_defaults': network_defaults,
    }

    # check if any settings have been changed
    if config_read.config_path_exists() and config_read.config_is_valid():
        old_config = config_read.get_config()
        old_data = {key: old_config.get(key) for key in data.keys()}
        create_new_config = not nested_utils.is_equal(data, old_data)
    else:
        create_new_config = True

    return data, create_new_config


def get_default_provider_name(provider_url: str, network: str) -> str:
    hostname = urllib.parse.urlparse(provider_url).hostname
    if hostname is not None:
        hostname_pieces = hostname.split('.')
        if len(hostname_pieces) == 1:
            hostname_piece = hostname_pieces[0]
        else:
            hostname_piece = hostname_pieces[-2]
    else:
        hostname_piece = provider_url

    return hostname_piece + '_' + network


def specify_providers(
    config_networks: typing.Mapping[spec.NetworkName, spec.NetworkMetadata],
    all_networks: typing.Mapping[spec.NetworkName, spec.NetworkMetadata],
    default_network: str,
    styles: typing.Mapping[str, str],
) -> dict[spec.ProviderName, spec.Provider]:

    # load old providers
    if config_read.config_path_exists():
        try:
            old_config = config_read.get_config(validate=False)
            default_providers: dict[str, spec.Provider] = {}
            old_providers = old_config.get('providers', default_providers)
        except Exception:
            old_providers = {}
    else:
        old_providers = {}

    # check whether to keep old providers
    if len(old_providers) > 0:
        print()
        print('Currently installed providers:')
        for provider_name, provider in old_providers.items():
            network_value = provider.get('network')
            if network_value is not None:
                network_name = network_value
            else:
                network_name = 'UNKNOWN'
            print('-', provider_name, '(network=' + network_name + ')')
        print()
        if toolcli.input_yes_or_no(
            'Keep these providers? ',
            default='yes',
            style=styles['question'],
        ):
            providers = old_providers
        else:
            providers = {}
    else:
        providers = {}

    # check whether default network has a provider
    default_network_has_providers = False
    for provider_metadata in providers.values():
        if provider_metadata['network'] == default_network:
            default_network_has_providers = True
            break
    if not default_network_has_providers:
        prompt = (
            'Do you want to specify a provider node for '
            + default_network
            + '? '
        )
        print()
        if toolcli.input_yes_or_no(
            prompt=prompt, default='yes', style=styles['question']
        ):
            provider_network = default_network
            provider_url = toolcli.input_prompt(
                prompt='Provider node URL? ', style=styles['question']
            )
            default_name = get_default_provider_name(
                provider_url=provider_url, network=default_network
            )
            provider_name = toolcli.input_prompt(
                'Provider node name? ',
                style=styles['question'],
                default=default_name,
            )

            provider_spec: spec.PartialProvider = {
                'name': provider_name,
                'url': provider_url,
                'network': provider_network,
                'protocol': 'http',
                'session_kwargs': None,
                'chunk_size': None,
            }
            # should validate that this confirms to spec.ProviderSpec
            providers[provider_name] = provider_spec

    # specify additional providers
    print()
    answer = toolcli.input_yes_or_no(
        prompt='Do you want to specify any additional providers? ',
        default='no',
        style=styles['question'],
    )
    while answer:

        # specify network
        go_back = False
        valid_answer = False
        while not valid_answer:
            print()
            print('Adding new provider node...')
            provider_network = toolcli.input_prompt(
                prompt='Network of provider? (see list of networks above) ',
                style=styles['question'],
            )
            if provider_network == '':
                go_back = True
                break
            elif provider_network not in all_networks:
                print('unknown network')
            else:
                valid_answer = True
        if go_back:
            break

        # specify url
        provider_url = toolcli.input_prompt(
            prompt='Provider URL? (enter blank line to go back) ',
            style=styles['question'],
        )
        if provider_url == '':
            break
        default_name = get_default_provider_name(
            provider_url=provider_url, network=provider_network
        )

        # specify name
        valid_answer = False
        while not valid_answer:
            provider_name = toolcli.input_prompt(
                'Provider name? (enter blank line to go back) ',
                style=styles['question'],
                default=default_name,
            )
            if provider_name == '':
                go_back = True
                break
            elif provider_name in providers:
                if toolcli.input_prompt(
                    'Provider with this name already exists. Overwrite? '
                ):
                    valid_answer = True
                else:
                    continue
            else:
                valid_answer = True
        if go_back:
            break

        provider_spec = {
            'name': provider_name,
            'url': provider_url,
            'network': provider_network,
        }
        providers[provider_name] = rpc.get_provider(provider_spec)

    return providers


def specify_network_defaults(
    default_network: str,
    providers: typing.Mapping[str, spec.Provider],
    styles: typing.Mapping[str, typing.Optional[str]],
) -> spec.ConfigNetworkDefaults:

    # compile providers for each network
    providers_per_network: dict[str, list[str]] = {}
    for provider_name, provider_metadata in providers.items():
        network = provider_metadata['network']
        if network is None:
            raise Exception('unknown network for provider: ' + str(provider_metadata))
        providers_per_network.setdefault(network, [])
        providers_per_network[network].append(provider_name)

    # get default provider for each network
    default_providers = {}
    for network in providers_per_network:
        n_providers = len(providers_per_network[network])
        if n_providers == 1:
            default_providers[network] = providers_per_network[network][0]
        elif n_providers > 1:
            answer = toolcli.input_number_choice(
                prompt='Which provider to use as default for ' + network + '?',
                choices=providers_per_network[network],
                style=styles['question'],
            )
            default_providers[network] = providers_per_network[network][answer]
    scan_api_key = None
    default_networks = directory.load_networks_from_disk(use_default=True)
    network_explorer = default_networks[default_network]['block_explorer']

    if (default_network.lower() != 'mainnet'):
        scan_api_key = toolcli.input_prompt(
            prompt= network_explorer+ 'API Key?', style=styles['question']
        )
    return {
        'default_network': default_network,
        'scan_api': scan_api_key,
        'default_providers': default_providers,
    }

