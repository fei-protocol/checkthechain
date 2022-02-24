import toolstr

from ctc import evm
from ctc import directory
from ctc import rpc
from ctc.protocols import fei_utils


def get_command_spec():
    return {
        'f': async_pcv_command,
    }


async def async_pcv_command():
    pcv_stats = await fei_utils.async_get_pcv_stats()
    FEI = directory.get_erc20_address('FEI')
    total_fei = await evm.async_get_erc20_total_supply(FEI)

    total_pcv = pcv_stats['pcv'] / 1e18
    user_fei = pcv_stats['user_fei'] / 1e18
    protocol_fei = total_fei - user_fei
    protocol_equity = total_pcv - user_fei
    cr = total_pcv / user_fei

    output = 'list'
    # output = 'table'

    if output == 'list':
        format_kwargs = {'order_of_magnitude': True, 'prefix': '$'}
        toolstr.print_text_box('Fei PCV Summary')
        print('- total PCV:', toolstr.format(total_pcv, **format_kwargs))
        print('- total FEI:', toolstr.format(total_fei, **format_kwargs))
        print('- user FEI:', toolstr.format(user_fei, **format_kwargs))
        print('- protocol FEI:', toolstr.format(protocol_fei, **format_kwargs))
        print('- PCV equity:', toolstr.format(protocol_equity, **format_kwargs))
        print('- CR:', toolstr.format(cr, percentage=True))
    elif output == 'table':
        import tooltable

        rows = [
            ['total PCV', toolstr.format(total_pcv, **format_kwargs)],
            ['total FEI', toolstr.format(total_fei, **format_kwargs)],
            ['user FEI', toolstr.format(user_fei, **format_kwargs)],
            ['protocol FEI', toolstr.format(protocol_fei, **format_kwargs)],
            ['PCV equity', toolstr.format(protocol_equity, **format_kwargs)],
            ['CR', toolstr.format(cr, percentage=True)],
        ]
        toolstr.print_text_box('Fei PCV Summary')
        tooltable.print_table(rows, headers=['', 'amount'])

    await rpc.async_close_http_session()
