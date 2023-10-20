# TODO

Important things that are not implemented yet!

- {meth}`nwb_linkml.adapters.classes.ClassAdapter.handle_dtype` does not yet handle compound dtypes,
  leaving them as `AnyType` instead. This is fine for a first draft since they are used rarely within
  NWB, but we will need to handle them by making slots for each of the dtypes since they typically
  represent table-like data.

## Docs TODOs

```{todolist}
```