"""
Mapping functions for handling HDMF classes like DynamicTables
"""

from typing import Any, List, Optional

import h5py


def dereference_reference_vector(dset: h5py.Dataset, data: Optional[List[Any]]) -> List:
    """
    Given a compound dataset with indices, counts, and object references, dereference to values

    Data is of the form
    (idx_start, count, target)
    """
    # assume all these references are to the same target
    # and the index is in the 3rd position
    if data is None:
        data = dset[:]

    target = dset.parent.get(data[0][-1])
    res = [target[d[0] : d[0] + d[1]] for d in data]
    return res
