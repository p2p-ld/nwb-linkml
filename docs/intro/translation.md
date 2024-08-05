# Translation Strategy

## NWB to LinkML

### Structure

### Names

### Arrays

## LinkML to Pydantic

### Types

### Metadata

### Arrays

## Special Cases

### DynamicTable

```{note}
See the [DynamicTable](https://hdmf-common-schema.readthedocs.io/en/stable/format_description.html#dynamictable)
reference docs
```

One of the major special cases in NWB is the use of `DynamicTable` to contain tabular data that
contains columns that are not in the base spec. 

#### Basic Usage

An example is the `TimeIntervals` neurodata type within `nwb.epoch` :

```yaml
groups:
- neurodata_type_def: TimeIntervals
  neurodata_type_inc: DynamicTable
  doc: A container for aggregating epoch data and the TimeSeries that each epoch applies
    to.
  datasets:
  - name: start_time
    neurodata_type_inc: VectorData
    dtype: float32
    doc: Start time of epoch, in seconds.
  - name: stop_time
    neurodata_type_inc: VectorData
    dtype: float32
    doc: Stop time of epoch, in seconds.
  - name: tags
    neurodata_type_inc: VectorData
    dtype: text
    doc: User-defined tags that identify or categorize events.
    quantity: '?'
  - name: tags_index
    neurodata_type_inc: VectorIndex
    doc: Index for tags.
    quantity: '?'
  - name: timeseries
    neurodata_type_inc: TimeSeriesReferenceVectorData
    doc: An index into a TimeSeries object.
    quantity: '?'
  - name: timeseries_index
    neurodata_type_inc: VectorIndex
    doc: Index for timeseries.
    quantity: '?'
```

Each of the columns of the table are specified as `VectorData` objects, 
which create an implicit `{n<=4}`-dimensional array,
and optionally have an adjoining `VectorIndex` attribute that has the `VectorData` item as a `target` :

```yaml
- data_type_def: VectorData
  data_type_inc: Data
  doc: ...
  dims:
  - ...
  shape:
  - ...
  attributes:
  - name: description
    dtype: text
    doc: Description of what these vectors represent.

- data_type_def: VectorIndex
  data_type_inc: VectorData
  dtype: uint8
  doc: ...
  dims:
  - num_rows
  shape:
  - null
  attributes:
  - name: target
    dtype:
      target_type: VectorData
      reftype: object
    doc: Reference to the target dataset that this index applies to.
```

The `DynamicTable` also allows for arbitrary additional `VectorData` columns,
where the `name` field is used as an identifier: columns specified in the model have a fixed `name` 
given by the schema, but each additional column is identified by its given `name`:

```yaml
- data_type_def: DynamicTable
  data_type_inc: Container
  doc: ...
  attributes:
  - name: colnames
    dtype: text
    dims:
    - num_columns
    shape:
    - null
    doc: The names of the columns in this table. This should be used to specify
      an order to the columns.
  - name: description
    dtype: text
    doc: Description of what is in this dynamic table.
  datasets:
  - name: id
    data_type_inc: ElementIdentifiers
    dtype: int
    dims:
    - num_rows
    shape:
    - null
    doc: Array of unique identifiers for the rows of this dynamic table.
  - data_type_inc: VectorData
    doc: Vector columns, including index columns, of this dynamic table.
    quantity: '*'
```

Where `colnames` is stored as an array in the metadata attributes of the group,
but all others are stored as hdf5 datasets.

In the simplest case, this results in a `TimeIntervals` group that looks like this
(abbreviated for clarity):

```
$ h5ls -rv an_nwb_dataset.nwb/trials
/trials                  Group
    Attribute: colnames {7}
        Type:      variable-length null-terminated UTF-8 string
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     TimeIntervals
/trials/id               Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     ElementIdentifiers
/trials/start_time       Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     VectorData
/trials/stop_time        Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     VectorData
/trials/surface_excursion_start_time Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     VectorData
/trials/surface_excursion_stop_time Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     VectorData
/trials/surface_location Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     VectorData
/trials/surface_return_start_time Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     VectorData
/trials/surface_return_stop_time Dataset {121/121}
    Attribute: neurodata_type scalar
        Type:      variable-length null-terminated UTF-8 string
        Value:     VectorData
```

#### Ragged Tables

`VectorIndex` and `VectorData` pairs can also be used to create ragged arrays, eg. in the case of the
`Units` model from `nwb.misc`

```yaml
- neurodata_type_def: Units
  neurodata_type_inc: DynamicTable
  default_name: Units
  doc: Data about spiking units. Event times of observed units (e.g. cell, synapse,
    etc.) should be concatenated and stored in spike_times.
  datasets:
  - name: spike_times_index
    neurodata_type_inc: VectorIndex
    doc: Index into the spike_times dataset.
    quantity: '?'
  - name: spike_times
    neurodata_type_inc: VectorData
    dtype: float64
    doc: Spike times for each unit in seconds.
    quantity: '?'
    attributes:
    - name: resolution
      dtype: float64
      doc: The smallest possible difference between two spike times. Usually 1 divided by the acquisition sampling rate
        from which spike times were extracted, but could be larger if the acquisition time series was downsampled or
        smaller if the acquisition time series was smoothed/interpolated and it is possible for the spike time to be
        between samples.
      required: false
```

In this case, the `spike_times` are stored as a 1-dimensional vector with spike times for each of the units
concatenated. The `spike_times_index` then stores the first index for each of the units such that when one
indexes the `NWBFile.units[0]` one gets an array of all the spike times for the `0th` unit.

#### Inter-table views

The `DynamicTableRegion` model is a subclass of `VectorData` that refers to rows within another `DynamicTable`.

For example, the `ElectricalSeries` model from `nwb.ecephys` (abbreviated for clarity):

```yaml
- neurodata_type_def: ElectricalSeries
  neurodata_type_inc: TimeSeries
  doc: ...
  datasets:
  - name: data
    dtype: numeric
    dims:
    - ...
    shape:
    - ...
    doc: Recorded voltage data.
    attributes:
    - name: unit
      dtype: text
      value: volts
      doc: ...
  - name: electrodes
    neurodata_type_inc: DynamicTableRegion
    doc: DynamicTableRegion pointer to the electrodes that this time series was generated from.
```

This produces an HDF5 dataset like `/acquisition/{name}/electrodes` that has 
- a `table` attribute that is a reference to another dynamic table (eg. `/general/extracellular_ephys/electrodes`)
- a vector of values that are references to the row indices of that table

such that the `{n_times} x {n_electrodes}` `/data` array can be indexed such that 
each of the channels from `electrodes` correspond to a column of the array. 



#### Implicit Behavior

- A `VectorIndex` does not need to explicitly refer to a `VectorData` column using the `target` attribute,
  but can be implicitly linked by being named `{VectorData.name}_index`
- When indexing a dynamictable, the result that is returned with `DynamicTable.columname[0]` 
  is actually the `VectorIndex`ed view into the `VectorData` column, rather than the `VectorData` column itself
- References through `DynamicTableRegion` are similarly resolved by the API, replacing values from the referenced
  tables and datasets.

#### Implementation

When translating from nwb-schema-language to linkml we....

```{todo}
Link to relevant adapter classes
```

- Interpret `VectorData` as regular array-like slots if they have no additional attributes, or as subclasses when they do
- Replace all the special reference notation with `range: Class` annotations that directly refer to the classes being linked to

When generating pydantic models we...

- Include a special :class:`~nwb_linkml.includes.hdmf.DynamicTableMixin` in the generated `hdmf_common.table` module and
  replace the configured base model
- Since `linkml` doesn't have the notion of "arbitrary additional slots of this type" differentiated by a `name`,
  the Mixin class reconfigures the model to allow for `extra` fields.
- The mixin then has model-level validation routines to verify that the columns are of equal length
- The mixin also provides the accessor magic methods for indexing as usual. 




### References

There are several different ways to create references between objects in nwb/hdmf:

- [`links`](https://schema-language.readthedocs.io/en/latest/description.html#sec-link-spec) are group-level
  properties that can reference other groups or datasets like this:
  ```yaml
  links:
  - name: Link name
    doc: Required string with the description of the link
    target_type: Type of target
    quantity: Optional quantity identifier for the group (default=1).
  ```
- [Reference `dtype`](https://schema-language.readthedocs.io/en/latest/description.html#reference-dtype)s are
  dataset, and attribute-level properties that can reference both other objects and regions within other objects:
  ```yaml
  dtype:
    target_type: ElectrodeGroup
    reftype: object
  ```
- Implicitly, hdmf creates references between objects according to some naming conventions, eg.
  an attribute/dataset that is a `VectorIndex` named `mydata_index` will be linked to a `VectorData`
  object `mydata`.
- There is currrently a note in the schema language docs that there will be an additional
  [Relationships](https://schema-language.readthedocs.io/en/latest/description.html#relationships) system
  that explicitly models relationships, but it is unclear how that would be different than references. 

We represent all of these by just directly referring to the object type, preserving the source type
in an annotation, when necessary.


## LinkML to Everything

How to generalize to linked data triplets.