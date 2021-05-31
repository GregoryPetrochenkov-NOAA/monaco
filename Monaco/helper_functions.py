from collections import Iterable
from operator import itemgetter
from tqdm import tqdm
import numpy as np
import pandas as pd
from typing import Union

def is_num(val) -> bool:
    if isinstance(val, bool):
        return False
    else:
        try:
            float(val)
        except ValueError:
            return False
        else:
            return True


def length(x) -> Union[None, int]:
    if isinstance(x, Iterable):
        return len(x)
    elif isinstance(x, (np.float, float, bool, int)):
        return 1
    else:
        return None


def get_iterable(x) -> Union[tuple, Iterable]:
    if x is None:
        return tuple()
    elif isinstance(x, pd.DataFrame):
        return (x,)
    elif isinstance(x, Iterable):
        return x
    else:
        return (x,)


def slice_by_index(sequence, indices) -> list:
    if not sequence or not indices:
        return []
    items = itemgetter(*indices)(sequence)
    if len(indices) == 1:
        return [items]
    return list(items)


def vprint(verbose, *args, **kwargs):
    if verbose:
        print(*args, **kwargs)


def vwrite(verbose, *args, **kwargs):
    if verbose:
        tqdm.write(*args, **kwargs)

'''
### Test ###
if __name__ == '__main__':
    pass
#'''