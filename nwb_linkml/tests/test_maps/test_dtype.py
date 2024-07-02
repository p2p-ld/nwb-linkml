import numpy as np
import nptyping
from nwb_linkml.maps.dtype import struct_from_dtype


def test_struct_from_dtype():
    # Super weak test with fixed values, will expand with parameterize if needed
    np_dtype = np.dtype([("name1", "int32"), ("name2", "object"), ("name3", "str")])
    struct = struct_from_dtype(np_dtype)
    assert struct == nptyping.Structure["name1: Int32, name2: Object, name3: Unicode"]
