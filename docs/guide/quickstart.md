---
file_format: mystnb
kernelspec:
  name: nwb-linkml_docs
mystnb:
    output_stderr: 'remove-warn'
---
# Quickstart

## Reading Data

To get the fun part out of the way, you can read ur data:

```{code-cell}
:tags: [hide-output]

from pathlib import Path
from rich.pretty import pprint, pretty_repr
from rich.console import Console
from nwb_linkml.io import HDF5IO

# set up for pprinting in notebooks
console = Console(width=100)
print = console.print

# find sample data file and read
nwb_file = Path('../../nwb_linkml/tests/data/aibs.nwb')
data = HDF5IO(nwb_file).read()
print(data) 
```

## Load and manipulate NWB schemas

A {mod}`~nwb_linkml.providers.git` provider module can manage a repository to
provide a given NWB namespace at a given version, and cast the
schema into Pydantic models from {mod}`nwb_schema_language`. 

For the nwb-core schema, loading first just the namespaces file (without
adjoining schema):

```{code-cell}
:tags: [hide-output]

from nwb_linkml.providers.git import NWB_CORE_REPO
from nwb_linkml.io.schema import load_namespaces

namespace_file: 'Path' = NWB_CORE_REPO.provide_from_git('2.6.0')
core_namespaces = load_namespaces(namespace_file)
print(core_namespaces)
```

Or for a schema file... 

```{code-cell}
:tags: [hide-output]

from nwb_linkml.io.schema import load_schema_file

base_schema_file =  namespace_file.parent / 'nwb.base.yaml'
nwb_core_base = load_schema_file(base_schema_file)
print(nwb_core_base)
```

And additional {mod}`~nwb_linkml.adapters` are used to handle some of the
implicit behavior in nwb schema files, like importing other namespaces
at a specific version, and inter-schema class imports. Eg. the 
{class}`~nwb_linkml.adapters.NamespacesAdapter` finds the implicitly
imported `hdmf-common` namespace (again provided by the git schema provider).

```{code-cell}
:tags: [hide-output]

from nwb_linkml.adapters import NamespacesAdapter

core_ns = NamespacesAdapter.from_yaml(namespace_file)
print(core_ns.imported) 
```

The classes in {mod}`nwb_schema_language` are just pydantic models, so they 
can be used like any other to create new, validated schemas.

## Translating to LinkML

{mod}`~nwb_linkml.adapters` handle the conversion from NWB schema language to 
LinkML. 

```{code-cell}
:tags: [hide-output]

core_linkml = core_ns.build()
print(core_linkml)
```

The {class}`~nwb_linkml.adapters.BuildResult` class holds the LinkML representation
of each of the schemas and their classes, which are now in {class}`linkml_runtime.linkml_model.SchemaDefinition`
and `ClassDefinition` classes:

```{code-cell}
:tags: [hide-output]

print(core_linkml.schemas[0])
```





