import pprint

from libs.utils import ProgressBar
from libs.utils import STANDARD_COLORS, TREND_COLORS, INDEXES
from libs.utils import EXEMPT_METRICS, INDICATOR_NAMES

NORMAL = STANDARD_COLORS["normal"]
WARNING = STANDARD_COLORS["warning"]
NOTIFY = STANDARD_COLORS["ticker"]
BULL = TREND_COLORS["good"]
BEAR = TREND_COLORS["bad"]


SIGNAL_KEY = 'signals'
SIZE_KEY = 'length_of_data'


def assemble_last_signals(meta_sub: dict, lookback: int = 10, **kwargs) -> dict:
    """assemble_last signals

    Look through all indicators of lookback time and list them

    Arguments:
        meta_sub {dict} -- metadata subset "metadata[fund][view]"

    Keyword Arguments:
        lookback {int} -- number of trading periods into past to find signals (default: {5})

    Optional Args:
        standalone {bool} -- if run as a function, fetch all metadata info (default: {False})
        print_out {bool} -- print in terminal (default: {False})
        name {str} -- (default: {''})
        pbar {ProgressBar} -- (default: {None})

    Returns:
        dict -- last signals data object
    """
    standalone = kwargs.get('standalone', False)
    print_out = kwargs.get('print_out', False)
    name = kwargs.get('name', '')
    pbar = kwargs.get('progress_bar')

    metadata = []
    meta_keys = []
    name = INDEXES.get(name, name)

    if standalone:
        for key in meta_sub:
            if key not in EXEMPT_METRICS:
                metadata.append(meta_sub[key])
                meta_keys.append(key)
    else:
        metadata = [meta_sub]
        meta_keys.append('')

    increment = 1.0 / float(len(metadata))

    content = {"signals": []}
    for a, sub in enumerate(metadata):
        content['signals'] = []

        for key in sub:
            if key in INDICATOR_NAMES:

                if SIGNAL_KEY in sub[key] and SIZE_KEY in sub[key]:
                    start_period = sub[key][SIZE_KEY] - lookback - 1

                    for signal in sub[key][SIGNAL_KEY]:
                        if signal['index'] >= start_period:
                            data = {
                                "type": signal['type'],
                                "indicator": key,
                                "value": signal['value'],
                                "date": signal['date'],
                                "days_ago": (sub[key][SIZE_KEY] - 1 - signal['index'])
                            }
                            content["signals"].append(data)

        content["signals"].sort(key=lambda x: x['days_ago'])

        if pbar is not None:
            pbar.uptick(increment=increment)

        if print_out:
            content_printer(content, meta_keys[a], name=name)

    return content


def content_printer(content: dict, meta_key: str, **kwargs):
    """Content Printer

    Print to terminal with correct formatting.

    Arguments:
        content {dict} -- content dictionary
        meta_key {str} -- key for content

    Optional Args:
        name {str} -- (default: {''})
    """
    name = kwargs.get('name', '')

    COL_1_SPACE = 8
    COL_2_SPACE = 8
    COL_3_SPACE = 8
    COL_4_SPACE = 24
    COL_5_SPACE = 48

    print("\r\n")
    print(
        f"Content for {NOTIFY}{name}{NORMAL} for {NOTIFY}{meta_key}\r\n{NORMAL}")

    spaces_1 = " " * (COL_1_SPACE - len("(Ago)"))
    spaces_2 = " " * (COL_2_SPACE - len("Type"))
    spaces_3 = " " * (COL_3_SPACE - len("::"))
    spaces_4 = " " * (COL_4_SPACE - len("Indicator"))
    spaces_5 = " " * (COL_5_SPACE - len("(value/signal)"))

    print(
        f"{NOTIFY}(Ago){spaces_1}Type{spaces_2}::{spaces_3}Indicator{spaces_4}" +
        f"(value/signal){spaces_5}:: date{NORMAL}")
    print("")

    for sig in content["signals"]:
        if sig['type'] == 'bearish':
            color = BEAR
        else:
            color = BULL

        indicator = sig['indicator'].split('_')
        for i, ind in enumerate(indicator):
            indicator[i] = ind.capitalize()
        indicator = ' '.join(indicator)
        ind_spaces = " " * (COL_4_SPACE - len(indicator))

        ago = f"({sig['days_ago']})"
        ago_spaces = " " * (COL_1_SPACE - len(ago))

        _type = f"{sig['type'].upper()}"
        _type_spaces = " " * (COL_2_SPACE - len(_type))

        colon = "::"
        colon_spaces = " " * (COL_3_SPACE - len(colon))

        value = f"({sig['value']})"
        value_spaces = " " * (COL_5_SPACE - len(value))

        string = f"{color}{ago}{ago_spaces}{_type}{_type_spaces}{colon}{colon_spaces}" + \
            f"{indicator}{ind_spaces}{value}{value_spaces}:: {sig['date']}{NORMAL}"
        print(string)
