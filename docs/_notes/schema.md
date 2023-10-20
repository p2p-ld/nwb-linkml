# Schema Notes

https://schema-language.readthedocs.io/en/latest/

rough notes kept while thinking about how to translate the schema

The easiest thing to do seems to just be to make a linkML schema of the nwb-schema spec itself and then use that to generate python dataclasses that process the loaded namespaces using mixin methods lol

## Overview

We want to translate the schema to LinkML so that we can export to other schema formats,
generate code for dealing with the data, and ultimately make it interoperable
with other formats.


## Structure

- root is `nwb.namespace.yaml` and imports the rest of the namespaces
- `hdmf-common` is implicitly loaded (`TODO` link to issue)
- 

## Components

The [nwb specification language](https://schema-language.readthedocs.io/en/latest/description.html)
has several components

- **Namespaces:** top level object
- **Schema:** specified within a `namespaces` object. Each schema is a list of data types
- **Data types:** Each top-level list in a schema file is a data type. data types are one of three subtypes:
	- Groups: generic collection
	- Datasets: like groups, but also describe arrays
	- Links: references to other top-level 
- Attributes: Groups and Datasets, in addition to their default properties, also can have a list named `attributes` that seem to just be used like `**kwargs`, but also seem to maybe be used to specify arrays? 
	- > The specification of datasets looks quite similar to attributes and groups. Similar to attributes, datasets describe the storage of arbitrary n-dimensional array data. However, in contrast to attributes, datasets are not associated with a specific parent group or dataset object but are (similar to groups) primary data objects (and as such typically manage larger data than attributes)

The components, in turn:

- Groups and Datasets are recursive: ie. groups and datasets can have groups and datasets 
	- and also links (but the recursive part is just the group or dataset being linked to)

## Properties

**`dtype`** defines the storage type of the given "data type," which we'll also start calling "class" because confusing. 

dtypes can be 
- unset, where then the "data type"/"class" becomes a group of datasets.
- a string
- a list of dtypes: single-layer recursion
- a dictionary defining a "reference", 
	- `target_type`: that type the target of the reference is
	- `reftype`: the kind of reference being made, `ref/reference/object` (all equivalent) or `region` for a subset of the referred object.

**`dims`** defines the axis names, and `shape`** defines the possible shapes of an array. The structure of each has to match

eg: 

```yaml
- neurodata_type_def: Image
  neurodata_type_inc: NWBData
  dtype: numeric
  dims:
  - - x
    - y
  - - x
    - y
    - r, g, b
  - - x
    - y
    - r, g, b, a
  shape:
  - - null
    - null
  - - null
    - null
    - 3
  - - null
    - null
    - 4
```

Can a compound dtype be used with multiple dims?? if dtype also controls the shape of the data type (eg. the tabular data example with a bigass dtype,) then what are dims?

Seems like when `dtype` is specified with `dims` then it is treated as an array, but otherwise scalar. 


### Inheritance

- `neurodata_type_def` - defines a new data type
- `neurodata_type_inc` - includes/inherits from another data type within the namespace

Both are optional. Inheritance and instantiation appear to be conflated here

- `(def unset/inc unset)` - untyped data type? - seems to be because "datasets" are recursive, so the actual numerical arrays are "datasets" but so are the top-level classes. but can datasets truly be recursive? i think the HDF5 implementation probably means that untyped datasets are terminal - ie. untype datasets cannot contain datasets. maybe?
- `(def set  /inc unset)` - new data type
- `(def set  /inc set  )` - inheritance
- `(def unset/inc set  )` - instantiate???


If no new type is defined, the "data type" has a "data type" of the `inc`luded type? 

I believe this means that including without defining is instantiating the type, hence the need for a unique name. Otherwise, the "name" is presumably the name of the type?

Does overriding a dataset or group from the parent class ... override it? or add to it? or does it need to be validated against the parent dataset schema?

instantiation as a group can be used to indicate an abstract number of a dataset, not sure how that's distinct from `dtype` and `dims` yet.



## Mappings

What can be restructured to fit LinkML

we need to map:
- Namespaces: seem to operate like separate schema? Then within a namespace the
  rest are top-level objects
- Inheritance: NWB has an odd inheritance system, where the same syntax is used for
  inheritance, mixins, type declaration, and inclusion.
  - `neurodata_type_inc` -> `is_a`
- Groups: 
- Slots: Lots of properties are reused in the nwb spec, and LinkML lets us separate these out as slots
- `quantity` needs a manual map to linkML's cardinality property
- dims, shape, and dtypes: these should have been just attributes rather than put in the spec
  language, so we'll just make an Array class and use that.
  - dims and shape should probably be a dictionary so you don't need a zillion nulls, eg rather than 
  ```yaml
  dims:
  - - x
    - y
  - - x
    - y
    - r, g, b
  shape:
  - - null
    - null
  - - null
    - null
    - 3
  ```
  do
  ```yaml
  dims:
  - - name: x
    - name: y
  - - name: x
    - name: y
    - name: r, g, b
      shape: 3
  ```
  or even
  ```yaml
  dims:
  - - x
    - y
  - - x
    - y
    - name: r, g, b
      shape: 3

  ```

  And also is there any case that would break where there is some odd dependency between dims where it wouldn't work to just use an `optional` param

  ```yaml
  dims:
  - name: x
    shape: null
  - name: y
    shape: null
  - name: r, g, b
    shape: 3
    optional: true
  ```

## Parsing

- Given a `nwb.schema.yml` meta-schema that defines the types of objects in nwb schema...
- The top level of an NWB schema is a `namespaces` object
- each file specified in the `namespaces.schema` array is a distinct schema
	- that inherits the 
- `groups`
	- Top level lists are parsed as "groups"

## Special Types

holy hell it appears as if `hdmf-common` is all special cases. eg. DynamicTable.... is like a parallel implementation of links and references???