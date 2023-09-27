from typing import Annotated

class HDF5_Path(str):
    """Trivial subclass of string to indicate that it is a reference to a location within an HDF5 file"""
    pass