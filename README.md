# translate-nwb
Translating NWB schema language to linkml

The [nwb specification language](https://schema-language.readthedocs.io/en/latest/description.html)
has several components

- Namespaces: subcollections of specifications
- Groups: 

We want to translate the schema to LinkML so that we can export to other schema formats,
generate code for dealing with the data, and ultimately make it interoperable
with other formats.

To do that, we need to map:
- Namespaces: seem to operate like separate schema? Then within a namespace the
  rest are top-level objects
- Inheritance: NWB has an odd inheritance system, where the same syntax is used for
  inheritance, mixins, type declaration, and inclusion.
  - `neurodata_type_inc` -> `is_a`
- Groups: 
- Slots: Lots of properties are reused in the nwb spec, and LinkML lets us separate these out as slots
- dims, shape, and dtypes: these should have been just attributes rather than put in the spec
  language, so we'll just make an Array class and use that.