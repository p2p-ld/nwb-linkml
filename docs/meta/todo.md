# TODO

## v0.2 - update to linkml-arrays and formal release

NWB schema translation
- handle `links` field in groups
- handle compound `dtype` like in ophys.PlaneSegmentation.pixel_mask
- handle compound `dtype` like in TimeSeriesReferenceVectorData
- Create a validator that checks if all the lists in a compound dtype dataset are same length
- [ ] Make `target` optional in vectorIndex

Cleanup
- [ ] Update pydantic generator
- [ ] Restore regressions from stripping the generator
- [x] Make any_of with array ranges work
- [ ] PR upstream `equals_string` and `ifabsent` (if existing PR doesn't fix)
- [ ] Use the class rather than a string in _get_class_slot_range_origin:
      ```
      or inlined_as_list
      or (
      # sv.get_identifier_slot(range_cls.name, use_key=True) is None and
      ``` 
                
- [ ] Make a minimal pydanticgen-only package to slim linkml deps?
- [ ] Disambiguate "maps" terminology - split out simple maps from the eg. dataset mapping classes
- [ ] Remove unnecessary imports
  - dask
  - nptyping
- [ ] Adapt the split generation to the new split generator style 

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

Remove monkeypatches/overrides once PRs are closed
- [ ] https://github.com/linkml/linkml-runtime/pull/330

Tests
- [ ] Ensure schemas and pydantic modules in repos are up to date

## Docs TODOs

```{todolist}
```