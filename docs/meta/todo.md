# TODO

## v0.2 - update to linkml-arrays and formal release

NWB schema translation
- handle `links` field in groups
- handle compound `dtype` like in ophys.PlaneSegmentation.pixel_mask
- handle compound `dtype` like in TimeSeriesReferenceVectorData
- Create a validator that checks if all the lists in a compound dtype dataset are same length

Important things that are not implemented yet!

- {meth}`nwb_linkml.adapters.classes.ClassAdapter.handle_dtype` does not yet handle compound dtypes,
  leaving them as `AnyType` instead. This is fine for a first draft since they are used rarely within
  NWB, but we will need to handle them by making slots for each of the dtypes since they typically
  represent table-like data.

## Docs TODOs

```{todolist}
```