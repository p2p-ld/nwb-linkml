# TODO

## v0.2 - update to linkml-arrays and formal release

NWB schema translation
- handle `links` field in groups
- handle compound `dtype` like in ophys.PlaneSegmentation.pixel_mask
- handle compound `dtype` like in TimeSeriesReferenceVectorData
- Create a validator that checks if all the lists in a compound dtype dataset are same length

Cleanup
- [ ] Update pydantic generator
- [ ] Make a minimal pydanticgen-only package to slim linkml deps?
- [ ] Disambiguate "maps" terminology - split out simple maps from the eg. dataset mapping classes
- [ ] Remove unnecessary imports
  - dask
  - nptyping

Important things that are not implemented yet!

- [x] {meth}`nwb_linkml.adapters.classes.ClassAdapter.handle_dtype` does not yet handle compound dtypes,
  leaving them as `AnyType` instead. This is fine for a first draft since they are used rarely within
  NWB, but we will need to handle them by making slots for each of the dtypes since they typically
  represent table-like data.
- [ ] Need to handle DynamicTables!
  - Adding columns?
  - Validating eg. all are same length?
  - Or do we want to just say "no dynamictables, just subclass and add more slots since it's super easy to do that."
  - method to return a dataframe
  - append rows/this should just be a df basically.
  - existing handler is fucked, for example, in `maps/hdmf`
- [ ] Handle indirect indexing eg. https://pynwb.readthedocs.io/en/stable/tutorials/general/plot_timeintervals.html#accessing-referenced-timeseries

## Docs TODOs

```{todolist}
```