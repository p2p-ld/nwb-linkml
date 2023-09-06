"""
This is a sandbox file that should be split out to its own pydantic-hdf5 package, but just experimenting here to get our bearings
"""
from typing import Optional, List, Dict
from pathlib import Path
from types import ModuleType

import h5py

from nwb_linkml.translate import generate_from_nwbfile

class HDF5IO():

    def __init__(self, path:Path):
        self.path = Path(path)
        self._modules: Dict[str, ModuleType] = {}

    @property
    def modules(self) -> Dict[str, ModuleType]:
        if len(self._modules) == 0:
            self._modules = generate_from_nwbfile(self.path)
        return self._modules

    def process_group(self, group:h5py.Group|h5py.File) -> dict | list:
        attrs = dict(group.attrs)

        # how to process the group?
        # --------------------------------------------------
        # list-like
        # --------------------------------------------------
        # a list of data classes
        if 'neurodata_type' not in attrs and \
            all([isinstance(v, h5py.Group) for v in group.values()]) and \
            all(['neurodata_type' in v.attrs for v in group.values()]):

            return [self.process_group(v) for v in group.values()]

        # --------------------------------------------------
        # dict-like
        # --------------------------------------------------

        res = {}


        for key, val in group.items():
            if isinstance(val, h5py.Group):
                res[key] = self.process_group(val)
            elif isinstance(val, h5py.Dataset):
                res[key] = self.process_dataset(val)
        return res

    def process_dataset(self, data: h5py.Dataset) -> dict | list:
        if len(data.shape) == 1:
            return list(data[:])


if __name__ == "__main__":
    NWBFILE = Path('/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb')
    h5f = HDF5IO(NWBFILE)


