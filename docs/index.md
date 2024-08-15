# nwb-linkml

```{role} feature
```

A translation of the [Neurodata Without Borders](https://www.nwb.org/) standard
to [LinkML](https://linkml.io/).

```{admonition} Quick Links
* [Quickstart](guide/quickstart) - Some stuff this package does
* [Purpose](intro/purpose) - Why this package exists
* [Overview](guide/overview) - Overview of how it works
* [API Docs](api/nwb_linkml/index) - Ok *really* how it works
* [TODO](meta/todo) - The work that remains to be done
```

`nwb-linkml` is an independent implementation of the standard capable of:

* Translating schemas written in the {index}`NWB Schema Language` to LinkML.
* Manage multiple versions of NWB schemas with dependencies
* Generating pydantic models from nwb-flavored LinkML 
* Read NWB files (including those that use custom, embedded schemas)
* {feature}`Coming Soon` Write/edit NWB files
* {feature}`Coming Soon` Export NWB to a Relational Database
* {feature}`Coming Soon` Export NWB to a Triple Store

## Example Translation

(Abbreviated for clarity)

`````{tab-set}
````{tab-item} NWB schema
```yaml
groups:
- neurodata_type_def: TimeSeries
  neurodata_type_inc: NWBDataInterface
  doc: General purpose time series.
  attributes:
  - name: description
    dtype: text
    default_value: no description
    doc: Description of the time series.
    required: false
  - name: comments
    dtype: text
    default_value: no comments
    doc: Human-readable comments about the TimeSeries. This second descriptive field
      can be used to store additional information, or descriptive information if the
      primary description field is populated with a computer-readable string.
    required: false
  datasets:
  - name: data
    dims:
    - - num_times
    - - num_times
      - num_DIM2
    - - num_times
      - num_DIM2
      - num_DIM3
    - - num_times
      - num_DIM2
      - num_DIM3
      - num_DIM4
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
    doc: Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension
      should always represent time. This can also be used to store binary data
      (e.g., image frames). This can also be a link to data stored in an external file.
    attributes:
    - name: conversion
      dtype: float32
      default_value: 1.0
      doc: Scalar to multiply each element in data (...)
      required: false
  - name: timestamps
    dtype: float64
    dims:
    - num_times
    shape:
    - null
    doc: Timestamps for samples stored in data, in seconds, relative to the
      common experiment master-clock stored in NWBFile.timestamps_reference_time.
    quantity: '?'
    attributes:
    - name: interval
      dtype: int32
      value: 1
      doc: Value is '1'
    - name: unit
      dtype: text
      value: seconds
      doc: Unit of measurement for timestamps, which is fixed to 'seconds'.
```
````
````{tab-item} LinkML
```yaml
classes:
  TimeSeries:
    name: TimeSeries
    description: General purpose time series.
    is_a: NWBDataInterface
    attributes:
      name:
        name: name
        identifier: true
        range: string
        required: true
      description:
        name: description
        description: Description of the time series.
        range: text
      comments:
        name: comments
        description: Human-readable comments about the TimeSeries. This second descriptive
          field can be used to store additional information, or descriptive information
          if the primary description field is populated with a computer-readable string.
        range: text
      data:
        name: data
        description: Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first
          dimension should always represent time. This can also be used to store binary
          data (e.g., image frames). This can also be a link to data stored in an
          external file.
        multivalued: false
        range: TimeSeries__data
        required: true
      timestamps:
        name: timestamps
        description: Timestamps for samples stored in data, in seconds, relative to
          the common experiment master-clock stored in NWBFile.timestamps_reference_time.
        multivalued: false
        range: TimeSeries__timestamps__Array
        required: false
    tree_root: true
    
  TimeSeries__data:
    name: TimeSeries__data
    description: Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension
      should always represent time. This can also be used to store binary data (e.g.,
      image frames). This can also be a link to data stored in an external file.
    attributes:
      name:
        name: name
        ifabsent: string(data)
        identifier: true
        range: string
        required: true
        equals_string: data
      conversion:
        name: conversion
        description: Scalar to multiply each element in data to convert it to the
          specified 'unit'. If the data are stored in acquisition system units or
          other units that require a conversion to be interpretable, multiply the
          data by 'conversion' to convert the data to the specified 'unit'. e.g. if
          the data acquisition system stores values in this object as signed 16-bit
          integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V
          to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion'
          multiplier to get from raw data acquisition values to recorded volts is
          2.5/32768/8000 = 9.5367e-9.
        range: float32
      array:
        name: array
        range: TimeSeries__data__Array
        
  TimeSeries__data__Array:
    name: TimeSeries__data__Array
    is_a: Arraylike
    attributes:
      num_times:
        name: num_times
        range: AnyType
        required: true
      num_DIM2:
        name: num_DIM2
        range: AnyType
        required: false
      num_DIM3:
        name: num_DIM3
        range: AnyType
        required: false
      num_DIM4:
        name: num_DIM4
        range: AnyType
        required: false
        
  TimeSeries__timestamps__Array:
    name: TimeSeries__timestamps__Array
    is_a: Arraylike
    attributes:
      num_times:
        name: num_times
        range: float64
        required: true
```
````
````{tab-item} Pydantic
```python
class TimeSeries(NWBDataInterface):
    """
    General purpose time series.
    """
    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    data: TimeSeriesData = Field(..., description="""Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.""")
    timestamps: Optional[NDArray[Shape["* num_times"], Float64]] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    
class TimeSeriesData(ConfiguredBaseModel):
    """
    Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.
    """
    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    conversion: Optional[float] = Field(None, description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as signed 16-bit integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion' multiplier to get from raw data acquisition values to recorded volts is 2.5/32768/8000 = 9.5367e-9.""")
    array: Optional[Union[
        NDArray[Shape["* num_times"], Any],
        NDArray[Shape["* num_times, * num_DIM2"], Any],
        NDArray[Shape["* num_times, * num_DIM2, * num_DIM3"], Any],
        NDArray[Shape["* num_times, * num_DIM2, * num_DIM3, * num_DIM4"], Any]
    ]] = Field(None)
    

```
````
`````

```{toctree}
:caption: Intro
:maxdepth: 3
:hidden:

intro/purpose
intro/nwb
intro/translation
```

```{toctree}
:caption: Guide
:maxdepth: 1
:hidden:

guide/quickstart
guide/overview
```

````{only} minimal
```{toctree}
:caption: API
:maxdepth: 3
:hidden:

api/nwb_linkml/index
api/nwb_schema_language/index
api/nwb_linkml/schema/index
```
````

````{only} full
```{toctree}
:caption: API
:maxdepth: 3
:hidden:

api/nwb_linkml/index
api/nwb_schema_language/index
api/models/nwb_linkml.models
api/nwb_linkml/schema/index
```
````

```{toctree}
:caption: Meta
:hidden:

meta/todo
meta/changelog
meta/references
genindex
```



