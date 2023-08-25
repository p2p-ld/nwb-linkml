from argparse import ArgumentParser
from pathlib import Path
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators import PydanticGenerator

from nwb_linkml import io

def generate_core_yaml(output_path:Path):
    core = io.load_nwb_core()
    built_schemas = core.build().schemas
    for schema in built_schemas:
        output_file = output_path / (schema.name + '.yaml')
        yaml_dumper.dump(schema, output_file)

def generate_core_pydantic(yaml_path:Path, output_path:Path):
    for schema in yaml_path.glob('*.yaml'):
        pydantic_file = (output_path / schema.name).with_suffix('.py')

        generator = PydanticGenerator(
            str(schema),
            pydantic_version='1',
            emit_metadata=True,
            gen_classvars=True,
            gen_slots=True
        )
        gen_pydantic = generator.serialize()
        with open(pydantic_file, 'w') as pfile:
            pfile.write(gen_pydantic)

def parser() -> ArgumentParser:
    parser = ArgumentParser('Generate NWB core schema')
    parser.add_argument(
        '--yaml',
        help="directory to export linkML schema to",
        type=Path,
        default=Path(__file__).parent.parent / 'nwb_linkml' / 'schema'
    )
    parser.add_argument(
        '--pydantic',
        help="directory to export pydantic models",
        type=Path,
        default=Path(__file__).parent.parent / 'nwb_linkml' / 'models'
    )
    return parser


def main():
    args = parser().parse_args()
    args.yaml.mkdir(exist_ok=True)
    args.pydantic.mkdir(exist_ok=True)
    generate_core_yaml(args.yaml)
    generate_core_pydantic(args.yaml, args.pydantic)

if __name__ == "__main__":
    main()







