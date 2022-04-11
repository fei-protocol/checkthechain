import typing

from typing_extensions import TypedDict


NetworkId = int
NetworkName = str
NetworkReference = typing.Union[NetworkId, NetworkName, None]
ScanAPIKey = str

class NetworkMetadata(TypedDict):
    name: NetworkName
    chain_id: int
    block_explorer: str  # url

