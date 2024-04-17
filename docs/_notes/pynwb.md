# PyNWB notes

## How does pynwb use the schema?

* nwb-schema is included as a git submodule within pynwb
* [__get_resources](https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/src/pynwb/__init__.py#L23) encodes the location of the directory
* [__TYPE_MAP](https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/src/pynwb/__init__.py#L51) eventually contains the schema information
* on import, [load_namespaces](https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/src/pynwb/__init__.py#L115-L116) populates `__TYPE_MAP`
* [register_class](https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/src/pynwb/__init__.py#L135-L136) decorator is used on all pynwb classes to register with `__TYPE_MAP`
  * Unclear how the schema is used if the containers contain the same information
* the [register_container_type](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/build/manager.py#L727-L736) method in hdmf's TypeMap class seems to overwrite the loaded schema???
  * `__NS_CATALOG` seems to actually hold references to the schema but it doesn't seem to be used anywhere except within `__TYPE_MAP` ? 
* [NWBHDF5IO](https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/src/pynwb/__init__.py#L237-L238) uses `TypeMap` to greate a `BuildManager`
  * Parent class [HDF5IO](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/backends/hdf5/h5tools.py#L37) then reimplements a lot of basic functionality from elsewhere
  * Parent-parent metaclass [HDMFIO](https://github.com/hdmf-dev/hdmf/blob/dev/src/hdmf/backends/io.py) appears to be the final writing class?
  * `BuildManager.build` then [calls `TypeMap.build`](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/build/manager.py#L171) ???
* `TypeMap.build` ...
  * gets the [`ObjectMapper`](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/build/manager.py#L763) which does [god knows what](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/build/manager.py#L697)
  * Calls the [`ObjectMapper.build`](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/build/objectmapper.py#L700) method
  * Which seems to ultimately create a [`DatasetBuilder`](https://github.com/hdmf-dev/hdmf/blob/dev/src/hdmf/build/builders.py#L315) object
* The `DatasetBuilder` is returned to the `BuildManager` which seems to just store it?
* [HDMFIO.write](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/backends/io.py#L78) then calls `write_builder` to use the builder, which is unimplemented in the metaclass
  * [HDF5IO.write_builder](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/backends/hdf5/h5tools.py#L806) implements it for HDF5, which then calls `write_group`, `write_dataset`, `write_link`, depending on the builder types, each of which are extremely heavy methods! 
  * eg. [`write_dataset`](https://github.com/hdmf-dev/hdmf/blob/dd39b3878523c4b03f5286fc740752befd192d8b/src/hdmf/backends/hdf5/h5tools.py#L1080) is basically unreadable to me, but seems to implement every type of dataset writing in a single method.
* At this point it is entirely unclear how the schema is involved, but the file is written.