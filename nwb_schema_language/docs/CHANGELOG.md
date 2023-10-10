# 0.1.1

Revised models to make `name` an optional slot regardless of presence/absence
of `neurodata_type_def`, the naming of individual classes within the schema will be
handled by `nwb_linkml` - see:
https://github.com/NeurodataWithoutBorders/nwb-schema/issues/552

# 0.1.2

Regenerating models to refresh... not many changes

# 0.1.3

Except that I broke the ability for the `Namespace` model to parse singleton authors.

Reinstated with a patch that runs on `gen-pydantic`