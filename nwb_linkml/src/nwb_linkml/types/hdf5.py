from typing import Annotated

HDF5_Path = Annotated[str, """Trivial subclass of string to indicate that it is a reference to a location within an HDF5 file"""]