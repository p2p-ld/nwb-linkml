"""
Since NWB doesn't necessarily have a term for a single nwb schema file, we're going
to call them "schema" objects
"""

from typing import Optional, List, TYPE_CHECKING
from pathlib import Path
from pydantic import Field

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.classes import ClassAdapter
if TYPE_CHECKING:
    from nwb_linkml.adapters.namespaces import NamespacesAdapter

from nwb_schema_language import Group, Dataset
from typing import NamedTuple

from linkml_runtime.linkml_model import SchemaDefinition


class SplitSchema(NamedTuple):
    main: BuildResult
    split: BuildResult

class SchemaAdapter(Adapter):
    """
    An individual schema file in nwb_schema_language
    """
    path: Path
    groups: List[Group] = Field(default_factory=list)
    datasets: List[Dataset] = Field(default_factory=list)
    imports: List['SchemaAdapter'] = Field(default_factory=list)
    namespace: Optional[str] = Field(
        None,
        description="""String of containing namespace. Populated by NamespacesAdapter""")
    split: bool = Field(
        True,
        description="Split anonymous subclasses into a separate schema file"
   )

    @property
    def name(self) -> str:
        return '.'.join([self.namespace, self.path.with_suffix('').name])

    def __repr__(self):
        out_str = '\n' + self.name + '\n'
        out_str += '-'*len(self.name) + '\n'
        if len(self.imports) > 0:
            out_str += "Imports:\n"
            out_str += "  " + ', '.join([i.name for i in self.imports]) + '\n'

        out_str += 'Groups:\n'
        out_str += '  ' + ', '.join([g.neurodata_type_def for g in self.groups])
        out_str += '\n'
        out_str += 'Datasets:\n'
        out_str += '  ' + ', '.join([d.neurodata_type_def for d in self.datasets])
        out_str += "\n"

        return out_str

    def build(self) -> BuildResult:
        """
        Make the LinkML representation for this schema file

        Things that will be populated later
        - `id` (but need to have a placeholder to instantiate)
        - `version`


        """
        classes = [ClassAdapter(cls=dset) for dset in self.datasets]
        classes.extend(ClassAdapter(cls=group) for group in self.groups)
        built_results = None
        for cls in classes:
            if built_results is None:
                built_results = cls.build()
            else:
                built_results += cls.build()

        if self.split:
            sch_split = self.split_subclasses(built_results)
            return sch_split

        else:
            sch = SchemaDefinition(
                name = self.name,
                id = self.name,
                imports = [i.name for i in self.imports],
                classes=built_results.classes,
                slots=built_results.slots,
                types=built_results.types
            )
            # every schema needs the language elements
            sch.imports.append('nwb.language')
            return BuildResult(schemas=[sch])

    def split_subclasses(self, classes: BuildResult) -> BuildResult:
        """
        Split the generated classes into top-level "main" classes and
        nested/anonymous "split" classes.

        Args:
            classes (BuildResult): A Build result object containing the classes
                for the schema

        Returns:
            :class:`.SplitSchema`
        """
        # just split by the presence or absence of __
        main_classes = [c for c in classes.classes if '__' not in c.name]
        split_classes = [c for c in classes.classes if '__' in c.name]
        split_sch_name = '.'.join([self.name, 'include'])


        imports = [i.name for i in self.imports]
        imports.append('nwb.language')
        # need to mutually import the two schemas because the subclasses
        # could refer to the main classes
        main_imports = imports
        main_imports.append(split_sch_name)
        imports.append(self.name)
        main_sch = SchemaDefinition(
            name=self.name,
            id=self.name,
            imports=main_imports,
            classes=main_classes,
            slots=classes.slots,
            types=classes.types
        )
        split_sch = SchemaDefinition(
            name=split_sch_name,
            id=split_sch_name,
            imports=imports,
            classes=split_classes,
            slots=classes.slots,
            types=classes.types
        )
        res = BuildResult(
            schemas=[main_sch, split_sch]
        )
        return res



    @property
    def created_classes(self) -> List[Group|Dataset]:
        classes = [t for t in self.walk_types([self.groups, self.datasets], (Group, Dataset)) if t.neurodata_type_def is not None]
        return classes

    @property
    def needed_imports(self) -> List[str]:
        """
        Classes that need to be imported from other namespaces

        TODO:
        - Need to also check classes used in links/references

        """
        type_incs = self.walk_fields(self, ('neurodata_type_inc', 'target_type'))

        definitions = [c.neurodata_type_def for c in self.created_classes]
        need = [inc for inc in type_incs if inc not in definitions]
        return need




