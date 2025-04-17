---
file_format: mystnb
#kernelspec:
#  name: nwb-linkml_docs
mystnb:
    output_stderr: 'remove-warn'
---

# Examples


```{info}
This is a demo for the linkml-arrays working group,
it is not how the docs will actually be :)
```

Setup
```{code-cell}
---
hide-cell: true
---
import json
import yaml
from pathlib import Path
import h5py
from myst_nb import glue
from rich import print
from rich.pretty import pprint
from IPython.display import display, Markdown
import pandas as pd
import numpy as np

from nwb_linkml import testing
from pynwb import NWBHDF5IO
from nwb_linkml.io.hdf5 import HDF5IO as Linkml_H5

tmp = Path() / "__tmp__"
tmp.mkdir(exist_ok=True)
```

Make the stuff

```{code-cell}
ecephys = testing.nwb_file_base()
ecephys = testing._nwb_ecephys(ecephys)
ecephys_path = tmp / "ecephys.nwb"
with NWBHDF5IO(ecephys_path, "w") as io:
    io.write(ecephys) 
```

Load it back in as nwb-linkml models

```{code-cell}
ecephys_linkml = Linkml_H5(ecephys_path).read()
# remove specs for the sake of display
ecephys_linkml.specifications = None
```
 
## Extracellular Ephys

### Schema

#### ElectricalSeries

`````{tab-set}
````{tab-item} NWB schema
```yaml
groups:
- neurodata_type_def: ElectricalSeries
  neurodata_type_inc: TimeSeries
  attributes:
  - name: filtering
    dtype: text
    required: false
  datasets:
  - name: data
    dtype: numeric
    dims:
    - - num_times
    - - num_times
      - num_channels
    - - num_times
      - num_channels
      - num_samples
    shape:
    - - null
    - - null
      - null
    - - null
      - null
      - null
    attributes:
    - name: unit
      dtype: text
      value: volts
  - name: electrodes
    neurodata_type_inc: DynamicTableRegion
  - name: channel_conversion
    dtype: float32
    dims:
    - num_channels
    shape:
    - null
    quantity: '?'
    attributes:
    - name: axis
      dtype: int32
      value: 1
        
        
```
````
````{tab-item} LinkML
```yaml
name: core.nwb.ecephys
annotations:
  is_namespace:
    tag: is_namespace
    value: false
  namespace:
    tag: namespace
    value: core
id: core.nwb.ecephys
version: 2.8.0
imports:
- core.nwb.base
- ../../hdmf_common/v1_8_0/namespace
- core.nwb.device
- core.nwb.language
default_prefix: core.nwb.ecephys/

classes:
  ElectricalSeries:
    name: ElectricalSeries
    is_a: TimeSeries
    attributes:
      name:
        name: name
        identifier: true
        range: string
        required: true
      filtering:
        name: filtering
        range: text
        required: false
      channel_conversion:
        name: channel_conversion
        array:
          dimensions:
          - alias: num_channels
        range: float32
        required: false
        multivalued: false
      data:
        name: data
        range: ElectricalSeries__data
        required: true
        inlined: true
      electrodes:
        name: electrodes
        range: DynamicTableRegion
        required: true
        inlined: true
    tree_root: true
    
  ElectricalSeries__data:
    name: ElectricalSeries__data
    description: Recorded voltage data.
    attributes:
      name:
        name: name
        ifabsent: string(data)
        identifier: true
        range: string
        required: true
        equals_string: data
      continuity:
        name: continuity
        range: text
        required: false
      conversion:
        name: conversion
        ifabsent: float(1.0)
        range: float32
        required: false
      offset:
        name: offset
        range: float32
        required: false
      resolution:
        name: resolution
        ifabsent: float(-1.0)
        range: float32
        required: false
      unit:
        name: unit
        ifabsent: string(volts)
        range: text
        required: true
        equals_string: volts
      value:
        name: value
        range: numeric
        any_of:
        - array:
            dimensions:
            - alias: num_times
        - array:
            dimensions:
            - alias: num_times
            - alias: num_channels
        - array:
            dimensions:
            - alias: num_times
            - alias: num_channels
            - alias: num_samples

```
````
````{tab-item} Pydantic
```python
class ElectricalSeries(TimeSeries):
    """
    A time series of acquired voltage data from extracellular recordings. The data field is an int or float array storing data in volts. The first dimension should always represent time. The second dimension, if present, should represent channels.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ecephys", "tree_root": True})

    name: str = Field(...)
    filtering: Optional[str] = Field(None,)
    channel_conversion: Optional[NDArray[Shape["* num_channels"], float]] = Field(None,)
    data: ElectricalSeriesData = Field(...,)
    electrodes: Named[DynamicTableRegion] = Field(...,)
    description: Optional[str] = Field("no description",)
    comments: Optional[str] = Field("no comments",)
    starting_time: Optional[TimeSeriesStartingTime] = Field(None,)
    timestamps: Optional[NDArray[Shape["* num_times"], float]] = Field(None,)
    control: Optional[NDArray[Shape["* num_times"], int]] = Field(None,)
    control_description: Optional[NDArray[Shape["* num_control_values"], str]] = Field(None,)
    sync: Optional[TimeSeriesSync] = Field(None,)
    
class ElectricalSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage data.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ecephys"})

    name: Literal["data"] = Field("data",)
    continuity: Optional[str] = Field(None,)
    conversion: Optional[float] = Field(1.0,)
    offset: Optional[float] = Field(None,)
    resolution: Optional[float] = Field(-1.0,)
    unit: Literal["volts"] = Field("volts",)
    value: Optional[
        Union[
            NDArray[Shape["* num_times"], float | int],
            NDArray[Shape["* num_times, * num_channels"], float | int],
            NDArray[Shape["* num_times, * num_channels, * num_samples"], float | int],
        ]
    ] = Field(None)
    

```
````
`````

#### NWBFile.Electrodes

`````{tab-set}
````{tab-item} NWB schema
```yaml

- neurodata_type_def: NWBFile
  groups:
  - name: general
    groups:
    - name: extracellular_ephys
      doc: Metadata related to extracellular electrophysiology.
      quantity: '?'
      groups:
      - neurodata_type_inc: ElectrodeGroup
        doc: Physical group of electrodes.
        quantity: '*'
      - name: electrodes
        neurodata_type_inc: DynamicTable
        doc: A table of all electrodes (i.e. channels) used for recording.
        quantity: '?'
        datasets:
        - name: x
          neurodata_type_inc: VectorData
          dtype: float32
          doc: x coordinate of the channel location in the brain (+x is posterior).
          quantity: '?'
        - name: y
          neurodata_type_inc: VectorData
          dtype: float32
          doc: y coordinate of the channel location in the brain (+y is inferior).
          quantity: '?'
        - name: z
          neurodata_type_inc: VectorData
          dtype: float32
          doc: z coordinate of the channel location in the brain (+z is right).
          quantity: '?'
        - name: imp
          neurodata_type_inc: VectorData
          dtype: float32
          doc: Impedance of the channel, in ohms.
          quantity: '?'
        - name: location
          neurodata_type_inc: VectorData
          dtype: text
          doc: Location of the electrode (channel). Specify the area, layer, comments
            on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use
            standard atlas names for anatomical regions when possible.
        - name: filtering
          neurodata_type_inc: VectorData
          dtype: text
          doc: Description of hardware filtering, including the filter name and frequency cutoffs.
          quantity: '?'
        - name: group
          neurodata_type_inc: VectorData
          dtype:
            target_type: ElectrodeGroup
            reftype: object
          doc: Reference to the ElectrodeGroup this electrode is a part of.
        - name: group_name
          neurodata_type_inc: VectorData
          dtype: text
          doc: Name of the ElectrodeGroup this electrode is a part of.
        - name: rel_x
          neurodata_type_inc: VectorData
          dtype: float32
          doc: x coordinate in electrode group
          quantity: '?'
        - name: rel_y
          neurodata_type_inc: VectorData
          dtype: float32
          doc: y coordinate in electrode group
          quantity: '?'
        - name: rel_z
          neurodata_type_inc: VectorData
          dtype: float32
          doc: z coordinate in electrode group
          quantity: '?'
        - name: reference
          neurodata_type_inc: VectorData
          dtype: text
          doc: Description of the reference electrode and/or reference scheme used for this electrode, e.g.,
            "stainless steel skull screw" or "online common average referencing".
          quantity: '?'
        
```
````
````{tab-item} LinkML
```yaml
name: core.nwb.file
id: core.nwb.file
version: 2.8.0

classes:
  NWBFile:
    attributes:
      general:
        range: NWBFile__general
        required: true
        inlined: true
        inlined_as_list: true
        
  NWBFile__general:
     attributes:
      name:
        name: name
        ifabsent: string(general)
        identifier: true
        range: string
        required: true
        equals_string: general
      extracellular_ephys:
        name: extracellular_ephys
        description: Metadata related to extracellular electrophysiology.
        range: general__extracellular_ephys
        inlined: true
        inlined_as_list: true
        
  general__extracellular_ephys:
    name: general__extracellular_ephys
    description: Metadata related to extracellular electrophysiology.
    attributes:
      name:
        name: name
        ifabsent: string(extracellular_ephys)
        identifier: true
        range: string
        required: true
        equals_string: extracellular_ephys
      electrodes:
        name: electrodes
        description: A table of all electrodes (i.e. channels) used for recording.
        range: extracellular_ephys__electrodes
        inlined: true
        inlined_as_list: true
      value:
        name: value
        description: Physical group of electrodes.
        range: ElectrodeGroup
        multivalued: true
        inlined: true
        inlined_as_list: false
        
  extracellular_ephys__electrodes:
    name: extracellular_ephys__electrodes
    description: A table of all electrodes (i.e. channels) used for recording.
    is_a: DynamicTable
    attributes:
      name:
        name: name
        ifabsent: string(electrodes)
        identifier: true
        range: string
        required: true
        equals_string: electrodes
      x:
        name: x
        description: x coordinate of the channel location in the brain (+x is posterior).
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: float32
        required: false
        multivalued: false
      y:
        name: y
        description: y coordinate of the channel location in the brain (+y is inferior).
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: float32
        required: false
        multivalued: false
      z:
        name: z
        description: z coordinate of the channel location in the brain (+z is right).
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: float32
        required: false
        multivalued: false
      imp:
        name: imp
        description: Impedance of the channel, in ohms.
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: float32
        required: false
        multivalued: false
      location:
        name: location
        description: Location of the electrode (channel). Specify the area, layer,
          comments on estimation of area/layer, stereotaxic coordinates if in vivo,
          etc. Use standard atlas names for anatomical regions when possible.
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: text
        required: true
        multivalued: false
      filtering:
        name: filtering
        description: Description of hardware filtering, including the filter name
          and frequency cutoffs.
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: text
        required: false
        multivalued: false
      group:
        name: group
        description: Reference to the ElectrodeGroup this electrode is a part of.
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: ElectrodeGroup
        required: true
        multivalued: false
        inlined: true
      group_name:
        name: group_name
        description: Name of the ElectrodeGroup this electrode is a part of.
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: text
        required: true
        multivalued: false
      rel_x:
        name: rel_x
        description: x coordinate in electrode group
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: float32
        required: false
        multivalued: false
      rel_y:
        name: rel_y
        description: y coordinate in electrode group
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: float32
        required: false
        multivalued: false
      rel_z:
        name: rel_z
        description: z coordinate in electrode group
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: float32
        required: false
        multivalued: false
      reference:
        name: reference
        description: Description of the reference electrode and/or reference scheme
          used for this electrode, e.g., "stainless steel skull screw" or "online
          common average referencing".
        array:
          minimum_number_dimensions: 1
          maximum_number_dimensions: false
        range: text
        required: false
        multivalued: false
```
````
````{tab-item} Pydantic
```python
class NWBFile(NWBContainer):
    """
    An NWB file storing cellular-based neurophysiology data from a single experimental session.
    """
    
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.file", "tree_root": True}
    )
    
    general: NWBFileGeneral = Field(...)
    
class NWBFileGeneral(ConfiguredBaseModel):
    """
    Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.
    """
    
    extracellular_ephys: Optional[GeneralExtracellularEphys] = Field(
        None, description="""Metadata related to extracellular electrophysiology."""
    )
    
class GeneralExtracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to extracellular electrophysiology.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["extracellular_ephys"] = Field("extracellular_ephys")
    electrodes: Optional[ExtracellularEphysElectrodes] = Field(None)
    value: Optional[Dict[str, ElectrodeGroup]] = Field(None)

class ExtracellularEphysElectrodes(DynamicTable):
    """
    A table of all electrodes (i.e. channels) used for recording.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["electrodes"] = Field("electrodes")
    x: Optional[VectorData[NDArray[Any, float]]] = Field(None)
    y: Optional[VectorData[NDArray[Any, float]]] = Field(None)
    z: Optional[VectorData[NDArray[Any, float]]] = Field(None)
    imp: Optional[VectorData[NDArray[Any, float]]] = Field(None)
    location: VectorData[NDArray[Any, str]] = Field(...)
    filtering: Optional[VectorData[NDArray[Any, str]]] = Field(None)
    group: VectorData[NDArray[Any, ElectrodeGroup]] = Field(...)
    group_name: VectorData[NDArray[Any, str]] = Field(...)
    rel_x: Optional[VectorData[NDArray[Any, float]]] = Field(None)
    rel_y: Optional[VectorData[NDArray[Any, float]]] = Field(None)
    rel_z: Optional[VectorData[NDArray[Any, float]]] = Field(None)
    reference: Optional[VectorData[NDArray[Any, str]]] = Field(None)
    colnames: List[str] = Field(...)
    id: ElementIdentifiers = Field(...)

```
````
`````

#### hdmf - DynamicTable

`````{tab-set}
````{tab-item} NWB schema
```yaml

- data_type_def: DynamicTableRegion
  data_type_inc: VectorData
  dtype: int
  dims:
  - num_rows
  shape:
  - null
  attributes:
  - name: table
    dtype:
      target_type: DynamicTable
      reftype: object
  - name: description
    dtype: text
    
- data_type_def: VectorData
  data_type_inc: Data
  dims:
  - - dim0
  - - dim0
    - dim1
  - - dim0
    - dim1
    - dim2
  - - dim0
    - dim1
    - dim2
    - dim3
  shape:
  - - null
  - - null
    - null
  - - null
    - null
    - null
  - - null
    - null
    - null
    - null
  attributes:
  - name: description
    dtype: text

```
````
````{tab-item} LinkML
```yaml
name: hdmf-common.table
annotations:
  is_namespace:
    tag: is_namespace
    value: false
  namespace:
    tag: namespace
    value: hdmf-common
id: hdmf-common.table
version: 1.8.0
imports:
- hdmf-common.base
- hdmf-common.nwb.language

classes:
  DynamicTable:
    name: DynamicTable
    is_a: Container
    extra_slots:
      range_expression: 
        range: VectorData
    attributes:
      name:
        name: name
        identifier: true
        range: string
        required: true
      colnames:
        name: colnames
        range: text
        required: true
        multivalued: true
      description:
        name: description
        range: text
        required: true
      id:
        name: id
        array:
          dimensions:
          - alias: num_rows
        range: int
        required: true
        multivalued: false
    tree_root: true
    
  VectorData:
    name: VectorData
    is_a: Data
    attributes:
      name:
        name: name
        identifier: true
        range: string
        required: true
      description:
        name: description
        range: text
        required: true
      value:
        name: value
        range: AnyType
        any_of:
        - array:
            dimensions:
            - alias: dim0
        - array:
            dimensions:
            - alias: dim0
            - alias: dim1
        - array:
            dimensions:
            - alias: dim0
            - alias: dim1
            - alias: dim2
        - array:
            dimensions:
            - alias: dim0
            - alias: dim1
            - alias: dim2
            - alias: dim3
    tree_root: true
```
````
````{tab-item} Pydantic
(a lot more than this, the hdmf mixins are like most of the code of the models)
```python
T = TypeVar("T", default=NDArray)

class DynamicTable(DynamicTableMixin):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). These datasets represent different columns in the table. Apart from a column that contains unique identifiers for each row, there are no other required datasets. Users are free to add any number of custom VectorData objects (columns) here. DynamicTable also supports ragged array columns, where each element can be of a different size. To add a ragged array column, use a VectorIndex type to index the corresponding VectorData type. See documentation for VectorData and VectorIndex for more details. Unlike a compound data type, which is analogous to storing an array-of-structs, a DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable.
    """
    __pydantic_extra__: dict[str, "VectorData"]

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(...)
    colnames: List[str] = Field(...)
    description: str = Field(...)
    id: ElementIdentifiers = Field(...)
    
class VectorData(VectorDataMixin):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex[0]]. The second vector is at VectorData[VectorIndex[0]:VectorIndex[1]], and so on.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(...)
    description: str = Field(...)
    value: Optional[T] = Field(None)
```
````
`````


### pynwb HDF5

```{code-cell}

with h5py.File(ecephys_path) as h5f:
    print(testing.print_h5(h5f))
```

### nwb-linkml model

#### ecephys basics

```{code-cell}
eseries = ecephys_linkml.acquisition['ElectricalSeries']
pprint(eseries, max_depth=4)
```

All array items from hdf5 are proxies - 
the file handle isn't held open, we just slice it when needed.
Think of this like a full database transaction per operation rather than opening a session
and pooling transactions.

```{code-cell}
eseries.data.value
```

it's not that slow actually, and makes concurrent access easy to deal with since we have one place to lock

the numpydantic proxies provide some (idk, hopefully eventually all) common methods from the array protocol

```{code-cell}
eseries.data.value.shape
```

our attribute access can be a little redundant... so some convenience stuff

Item access propagates down through "value" and "data" fields:
NWB schema has attributes and array data at the same "level", 
so we have to invent a magic word for them.

So:
- `data` is the name of the dataset within electricalseries,
  NWB uses this by convention for the obvious data-bearing entity in the group
- `value` is the name of the array (or whatever kind of thing the value is) specified by the dataset

So we can select items from the array like this

```{code-cell}
eseries[0:3, 0:3]
```

#### electrodes - dynamic tables

Electrodes is a region of a table (a subset of all the electrodes)

```{code-cell}
electrodes = eseries.electrodes
pprint(electrodes, max_depth=2)
```

The whole table behaves like a table!

```{code-cell}
electrodes.table[:]
```

And we can index around it and whatnot with a combination of 

```{code-cell}
electrodes.table['group'][2].device
```

And our index into it has had a temporary regression but it too should behave like a table

```{code-cell}
pd.concat(electrodes[0:2])
```

It uses the items in its `value` array to index the electrodes table

```{code-cell}
electrodes.value[:]
```

Since the vector data are any-dimensional, and the dynamic tables are dynamic,
we can do whatever we want there.

A little awkward, haven't written convenience methods for this yet:

```{code-cell}
vd = type(electrodes.table.group)
electrodes.table.bonus = vd(
    name="bonus", 
    description="", 
    value=np.random.default_rng().random((len(electrodes.table), 10, 12))
) 
electrodes.table.colnames.append('bonus') 
electrodes.table[0]
```


#### icephys - aligned dynamic table

this starts to get pretty whacky (complimentary) once we start stacking these dynamictables together.

The nwb-linkml mixins that implement the hdmf behavior compose nicely tho, so it's not *too* complex.

So for example the intracellular recordings table is
- an aligned dynamic table of three subtables
  - electrodes
  - responses
  - stimuli
- each of which is a table that parameterizes an index into a vector
- which is an n-dimensional array that has been flattened out for storage

```{code-cell}
icephys = testing.nwb_file_base()
icephys = testing._nwb_icephys(icephys)
icephys_path = tmp / "icephys.nwb"
with NWBHDF5IO(icephys_path, "w") as io:
    io.write(icephys) 
    
icephys_linkml = Linkml_H5(icephys_path).read()
# remove specs for the sake of display
icephys_linkml.specifications = None
```

I can't print this thing because it's so much html it starts to lag the browser.
pretty printing is TODO.



```{code-cell}
ic_recordings = icephys_linkml.general.intracellular_ephys.intracellular_recordings
pprint(ic_recordings, max_depth=3)
```

but ya it'a s table of tables of arrays of arrays

Each row is a whole recording, aligned with its response, stimulus, and electrode metadata

(transpose because it's very wide)

```{code-cell}
ic_recordings[:2].transpose()
```

So say we want to get some response...

We can do it object style

```{code-cell}
ic_recordings.responses.response[0]
```

or  (multi-index) table style

```{code-cell}
ic_recordings['responses']['response'][0]
```

And if we drill all the way into the core of the mega table object...

... we can actually set values too!

```{code-cell}
ts_data= ic_recordings.responses.response.timeseries[0].data
ts_data.value[:] = 5
ts_data.value[:]
```

and we can validate with h5py right from the object bc numpydantic gives us a nice lil handle

```{code-cell}
response_h5 = ts_data.value.open()
response_h5
```

```{code-cell}
response_h5[:]
```

(we do have to close it tho, or should)
```{code-cell}
ts_data.value.close()
```


### linkml-nwb yaml

#### Currently...

It's a literal transcription of the model with some additional metadata added for roundtripping!

Since the model itself is just a schematic representation of scalar values and references to arrays,
it can be encoded that way as well.

Consider this the "expanded" concrete form.

At the moment we are not packing references in a tidy way, just expading them, but that's the next step...


```{code-cell}

ecephys_json = json.loads(ecephys_linkml.model_dump_json(round_trip=True, exclude_none=True))
# remove specs for display
ecephys_yaml = yaml.safe_dump(ecephys_json)
print(ecephys_yaml) 
```  

#### Goals

- objects get identity from context
- first-class references using URI anchor fragments as the document root and `@` for local anchors
- better control over dumping
- content addressing for chunks!
 
```yaml
meta:
  # meta dict could behave like a json-ld context and be declared once for a project
  # and imported like
  # extends:
  #   - //username/project_config.yaml
  
  id: my_dataset

  prefixes:
    nwbfile:
      - path: "test_nwb.nwb"
      - hash: "blake2b:blahblahblahblah"

  imports:
    core:
      as: nwb
      version: "2.7.0"
      from:
        - pypi:
            package: nwb-models
    hdmf-common:
      as: hdmf
      version: "1.8.0"
      from:
        - pypi:
            package: nwb-models
            
data:
  is_a: nwb:NWBFile
  file_create_date: [ 2024-01-01 ]
  identifier: "1111-1111-1111-1111"
  session_description: All that you touch, you change.
  session_start_time: 2024-01-01T01:01:01
  acquisition:
    cool_recording: "#cool_recording"
  general:
    devices:
      - Heka ITC-1600:
      - Microscope:
          description: My two-photon microscope
          manufacturer: The best microscope manufacturer
      - array:
          description: old reliable
          manufacturer: diy
    extracellular_ephys: "#extracellular_ephys"
    experiment_description: All that you change, changes you.
    experimenter: [ "Lauren Oya Olamina" ]
    institution: Earthseed Research Institute
    keywords:
      - behavior
      - belief
    related_publications: doi:10.1016/j.neuron.2016.12.011

extracellular_ephys:
  is_a: ExtracellularEphys
  electrodes:
    group:
      - "@shank0"
      - "@shank0"
      - "@shank0"
      - "@shank1"
      - # etc.
    shank0:
      device: "#data.general.devices.array"
    shank1:
      device: "#data.general.devices.array"
    # etc.
    
cool_recording:
  is_a: ElectricalSeries
  from:
    type: hdf5
    source: nwbfile:/acquisition/cool_recording

```


