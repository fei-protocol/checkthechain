"""

## Config Keys
- config_spec_version: version of config schema
- data_dir: root directory for storing ctc data
- default_network: default network to use when none specified
- providers: default provider for each network
- networks: custom user-defined networks


## TODO
- add additional config settings
    - rpc: set batching and other parameters for each rpc method
    - sql: configuration for sql database backend
"""
from __future__ import annotations

import typing
from typing_extensions import TypedDict

from . import network_types
from . import rpc_types

if typing.TYPE_CHECKING:
    import toolsql


class ConfigNetworkDefaults(TypedDict):
    default_network: network_types.NetworkName
    scan_api: typing.Optional[network_types.ScanAPIKey]
    default_providers: typing.Dict[
        network_types.NetworkName, rpc_types.ProviderName
    ]


class PartialConfigSpec(TypedDict, total=False):
    config_spec_version: str
    data_dir: str
    providers: typing.Dict[rpc_types.ProviderName, rpc_types.Provider]
    networks: typing.Dict[
        network_types.NetworkName, network_types.NetworkMetadata
    ]
    network_defaults: ConfigNetworkDefaults
    db_configs: typing.Mapping[str, toolsql.DBConfig]

    log_rpc_calls: bool
    log_sql_queries: bool


class ConfigSpec(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Dict[rpc_types.ProviderName, rpc_types.Provider]
    networks: typing.Dict[
        network_types.NetworkName, network_types.NetworkMetadata
    ]
    network_defaults: ConfigNetworkDefaults
    #
    # data sources
    # data_sources: None # not sure of format for this yet
    db_configs: typing.Mapping[str, toolsql.DBConfig]

    log_rpc_calls: bool
    log_sql_queries: bool

