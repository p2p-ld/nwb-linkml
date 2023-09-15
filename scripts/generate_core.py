import pdb
import shutil
import os
import traceback

from argparse import ArgumentParser
from pathlib import Path
from linkml_runtime.dumpers import yaml_dumper
from rich.live import Live
from rich.panel import Panel
from rich.console import Group
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, Column
from rich import print
from nwb_linkml.generators.pydantic import NWBPydanticGenerator

from nwb_linkml.providers.schema import LinkMLProvider, PydanticProvider
from nwb_linkml.providers.git import NWB_CORE_REPO, GitRepo
from nwb_linkml.io import schema as io

def generate_core_yaml(output_path:Path, dry_run:bool=False):
    """Just build the latest version of the core schema"""

    core = io.load_nwb_core()
    built_schemas = core.build().schemas
    for schema in built_schemas:
        output_file = output_path / (schema.name + '.yaml')
        if not dry_run:
            yaml_dumper.dump(schema, output_file)

def generate_core_pydantic(yaml_path:Path, output_path:Path, dry_run:bool=False):
    """Just generate the latest version of the core schema"""
    for schema in yaml_path.glob('*.yaml'):
        python_name = schema.stem.replace('.', '_').replace('-', '_')
        pydantic_file = (output_path / python_name).with_suffix('.py')

        generator = NWBPydanticGenerator(
            str(schema),
            pydantic_version='2',
            emit_metadata=True,
            gen_classvars=True,
            gen_slots=True
        )
        gen_pydantic = generator.serialize()
        if not dry_run:
            with open(pydantic_file, 'w') as pfile:
                pfile.write(gen_pydantic)

def generate_versions(yaml_path:Path, pydantic_path:Path, dry_run:bool=False):
    """
    Generate linkml models for all versions
    """
    repo = GitRepo(NWB_CORE_REPO)
    #repo.clone(force=True)
    repo.clone()

    # use a directory underneath this one as the temporary directory rather than
    # the default hidden one
    tmp_dir = Path(__file__).parent / '__tmp__'
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()

    linkml_provider = LinkMLProvider(path=tmp_dir, verbose=False)
    pydantic_provider = PydanticProvider(path=tmp_dir, verbose=False)

    failed_versions = {}

    overall_progress = Progress()
    overall_task = overall_progress.add_task('All Versions', total=len(NWB_CORE_REPO.versions))

    build_progress = Progress(
        TextColumn("[bold blue]{task.fields[name]} - [bold green]{task.fields[action]}",
                   table_column=Column(ratio=1)),
        BarColumn(table_column=Column(ratio=1), bar_width=None)
    )
    panel = Panel(Group(build_progress, overall_progress))


    with Live(panel) as live:
        # make pbar tasks
        linkml_task = None
        pydantic_task = None

        for version in NWB_CORE_REPO.versions:
            # build linkml
            try:
                # check out the version (this should also refresh the hdmf-common schema)
                linkml_task = build_progress.add_task('', name=version, action='Checkout Version', total=3)
                repo.tag = version
                build_progress.update(linkml_task, advance=1, action="Load Namespaces")

                # first load the core namespace
                core_ns = io.load_namespace_adapter(repo.namespace_file)
                # then the hdmf-common namespace
                hdmf_common_ns = io.load_namespace_adapter(repo.temp_directory / 'hdmf-common-schema' / 'common' / 'namespace.yaml')
                core_ns.imported.append(hdmf_common_ns)
                build_progress.update(linkml_task, advance=1, action="Build LinkML")


                linkml_res = linkml_provider.build(core_ns)
                build_progress.update(linkml_task, advance=1, action="Built LinkML")

                # build pydantic
                ns_files = [res['namespace'] for res in linkml_res.values()]
                all_schema = []
                for ns_file in ns_files:
                    all_schema.extend(list(ns_file.parent.glob('*.yaml')))

                pydantic_task = build_progress.add_task('', name=version, action='', total=len(all_schema))
                for schema in all_schema:
                    pbar_string = ' - '.join([schema.parts[-3], schema.parts[-2], schema.parts[-1]])
                    build_progress.update(pydantic_task, action=pbar_string)
                    pydantic_provider.build(schema, versions=core_ns.versions, split=True)
                    build_progress.update(pydantic_task, advance=1)
                build_progress.update(pydantic_task, action='Built Pydantic')



            except Exception as e:
                build_progress.stop_task(linkml_task)
                if linkml_task is not None:
                    build_progress.update(linkml_task, action='[bold red]LinkML Build Failed')
                    build_progress.stop_task(linkml_task)
                if pydantic_task is not None:
                    build_progress.update(pydantic_task, action='[bold red]LinkML Build Failed')
                    build_progress.stop_task(pydantic_task)
                failed_versions[version] = traceback.format_exception(e)

            finally:
                overall_progress.update(overall_task, advance=1)
                linkml_task = None
                pydantic_task = None

    if not dry_run:
        shutil.rmtree(yaml_path / 'linkml')
        shutil.rmtree(pydantic_path / 'pydantic')
        shutil.move(tmp_dir / 'linkml', yaml_path)
        shutil.move(tmp_dir / 'pydantic', pydantic_path)

        # import the most recent version of the schemaz we built
        latest_version = sorted((pydantic_path / 'pydantic' / 'core').iterdir(), key=os.path.getmtime)[-1]

        # make inits to use the schema! we don't usually do this in the
        # provider class because we directly import the files there.
        with open(pydantic_path / 'pydantic' / '__init__.py', 'w') as initfile:
            initfile.write(' ')

        with open(pydantic_path / '__init__.py', 'w') as initfile:
            initfile.write(f'from .pydantic.core.{latest_version.name}.namespace import *')

    if len(failed_versions) > 0:
        print('Failed Building Versions:')
        print(failed_versions)




def parser() -> ArgumentParser:
    parser = ArgumentParser('Generate all available versions of NWB core schema')
    parser.add_argument(
        '--yaml',
        help="directory to export linkML schema to",
        type=Path,
        default=Path(__file__).parent.parent / 'nwb_linkml' / 'src' / 'nwb_linkml' / 'schema'
    )
    parser.add_argument(
        '--pydantic',
        help="directory to export pydantic models",
        type=Path,
        default=Path(__file__).parent.parent / 'nwb_linkml' / 'src' / 'nwb_linkml' / 'models'
    )
    parser.add_argument(
        '--latest',
        help="Only generate the latest version of the core schemas.",
        action="store_true"
    )
    parser.add_argument(
        '--dry-run',
        help="Generate schema and pydantic models without moving them into the target directories, for testing purposes",
        action='store_true'
    )
    return parser


def main():
    args = parser().parse_args()
    if not args.dry_run:
        args.yaml.mkdir(exist_ok=True)
        args.pydantic.mkdir(exist_ok=True)
    if args.latest:
        generate_core_yaml(args.yaml, args.dry_run)
        generate_core_pydantic(args.yaml, args.pydantic, args.dry_run)
    else:
        generate_versions(args.yaml, args.pydantic, args.dry_run)

if __name__ == "__main__":
    main()







