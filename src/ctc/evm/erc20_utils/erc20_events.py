import typing

from ctc import spec
from .. import event_utils
from . import erc20_metadata


# import pandas


def get_erc20_transfers(
    token_address: spec.ERC20Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = 'latest',
    **event_kwargs
) -> spec.DataFrame:
    return event_utils.get_events(
        contract_address=token_address,
        event_name='Transfer',
        start_block=start_block,
        end_block=end_block,
        **event_kwargs
    )


async def async_get_erc20_balances_from_transfers(
    transfers: spec.DataFrame,
    block: typing.Optional[spec.BlockNumberReference] = None,
    dtype: spec.DType = float,
    normalize: bool = True,
) -> spec.DataFrame:

    # filter block
    if block is not None:
        blocks = transfers.index.get_level_values('block_number').values
        mask = blocks <= block
        transfers = transfers[mask]

    if 'arg__amount' in transfers.columns:
        amount_key = 'arg__amount'
    elif 'arg__value' in transfers.columns:
        amount_key = 'arg__value'
    else:
        raise Exception('could not detect a transfer amout key in transfers')

    # convert to float
    transfers[amount_key] = transfers[amount_key].map(dtype)

    # subtract transfers out from transfers in
    from_transfers = transfers.groupby('arg__from')[amount_key].sum()
    to_transfers = transfers.groupby('arg__to')[amount_key].sum()
    balances = to_transfers.sub(from_transfers, fill_value=0)

    # normalize
    if normalize:
        block = transfers.index[-1][0]
        address = transfers['contract_address'].iloc[0]
        decimals = await erc20_metadata.async_get_erc20_decimals(
            token=address, block=block
        )
        balances = balances / dtype('1e' + str(decimals))

    # sort
    balances = balances.sort_values(ascending=False)

    balances.name = 'transfer_amount'

    return balances

