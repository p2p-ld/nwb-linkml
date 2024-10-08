import shutil
import os
import sys
import traceback
from pdb import post_mortem
import subprocess

from argparse import ArgumentParser
from pathlib import Path
from linkml_runtime.dumpers import yaml_dumper
from rich.live import Live
from rich.panel import Panel
from rich.console import Group
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, Column
from rich import print
from nwb_linkml.generators.pydantic import NWBPydanticGenerator

from nwb_linkml.providers import LinkMLProvider, PydanticProvider
from nwb_linkml.providers.git import NWB_CORE_REPO, HDMF_COMMON_REPO, GitRepo
from nwb_linkml.io import schema as io


def make_tmp_dir(clear: bool = False) -> Path:
    # use a directory underneath this one as the temporary directory rather than
    # the default hidden one
    tmp_dir = Path(__file__).parent / "__tmp__"
    if tmp_dir.exists() and clear:
        for p in tmp_dir.iterdir():
            if p.is_dir() and not p.name == "git":
                shutil.rmtree(p)
    tmp_dir.mkdir(exist_ok=True)
    return tmp_dir


def generate_versions(
    yaml_path: Path,
    pydantic_path: Path,
    dry_run: bool = False,
    repo: GitRepo = NWB_CORE_REPO,
    pdb=False,
    latest: bool = False,
):
    """
    Generate linkml models for all versions
    """
    # repo.clone(force=True)
    repo.clone()

    tmp_dir = make_tmp_dir()

    linkml_provider = LinkMLProvider(path=tmp_dir, verbose=False)
    pydantic_provider = PydanticProvider(path=tmp_dir, verbose=False)

    failed_versions = {}

    if latest:
        versions = [repo.namespace.versions[-1]]
    else:
        versions = repo.namespace.versions

    overall_progress = Progress()
    overall_task = overall_progress.add_task("All Versions", total=len(versions))

    build_progress = Progress(
        TextColumn(
            "[bold blue]{task.fields[name]} - [bold green]{task.fields[action]}",
            table_column=Column(ratio=1),
        ),
        BarColumn(table_column=Column(ratio=1), bar_width=None),
    )
    panel = Panel(Group(build_progress, overall_progress))

    try:
        with Live(panel) as live:
            # make pbar tasks
            linkml_task = None
            pydantic_task = None

            for version in versions:
                # build linkml
                try:
                    # check out the version (this should also refresh the hdmf-common schema)
                    linkml_task = build_progress.add_task(
                        "", name=version, action="Checkout Version", total=3
                    )
                    repo.tag = version
                    build_progress.update(linkml_task, advance=1, action="Load Namespaces")

                    if repo.namespace == NWB_CORE_REPO:
                        # first load HDMF common
                        hdmf_common_ns = io.load_namespace_adapter(
                            repo.temp_directory / "hdmf-common-schema" / "common" / "namespace.yaml"
                        )
                        # then load nwb core
                        core_ns = io.load_namespace_adapter(
                            repo.namespace_file, imported=[hdmf_common_ns]
                        )

                    else:
                        # otherwise just load HDMF
                        core_ns = io.load_namespace_adapter(repo.namespace_file)

                    build_progress.update(linkml_task, advance=1, action="Build LinkML")

                    linkml_res = linkml_provider.build(core_ns, force=True)
                    build_progress.update(linkml_task, advance=1, action="Built LinkML")

                    # build pydantic
                    ns_files = [res.namespace for res in linkml_res.values()]

                    pydantic_task = build_progress.add_task(
                        "", name=version, action="", total=len(ns_files)
                    )
                    for schema in ns_files:
                        pbar_string = schema.parts[-3]
                        build_progress.update(pydantic_task, action=pbar_string)
                        pydantic_provider.build(
                            schema, versions=core_ns.versions, split=True, parallel=True, force=True
                        )
                        build_progress.update(pydantic_task, advance=1)
                    build_progress.update(pydantic_task, action="Built Pydantic")

                except Exception as e:
                    if pdb:
                        live.stop()
                        post_mortem()
                        sys.exit(1)

                    build_progress.stop_task(linkml_task)
                    if linkml_task is not None:
                        build_progress.update(linkml_task, action="[bold red]LinkML Build Failed")
                        build_progress.stop_task(linkml_task)
                    if pydantic_task is not None:
                        build_progress.update(pydantic_task, action="[bold red]LinkML Build Failed")
                        build_progress.stop_task(pydantic_task)
                    failed_versions[version] = traceback.format_exception(e)

                finally:
                    overall_progress.update(overall_task, advance=1)
                    linkml_task = None
                    pydantic_task = None

        if not dry_run:
            shutil.copytree(tmp_dir / "linkml", yaml_path, dirs_exist_ok=True)
            shutil.copytree(tmp_dir / "pydantic", pydantic_path, dirs_exist_ok=True)
            shutil.rmtree(tmp_dir / "linkml")
            shutil.rmtree(tmp_dir / "pydantic")

            # make inits to use the schema! we don't usually do this in the
            # provider class because we directly import the files there.
            with open(pydantic_path / "__init__.py", "w") as initfile:
                initfile.write(" ")

            subprocess.run(["black", "."])

    finally:
        if len(failed_versions) > 0:
            print("Failed Building Versions:")
            print(failed_versions)


def parser() -> ArgumentParser:
    parser = ArgumentParser("Generate all available versions of NWB core schema")
    parser.add_argument(
        "--yaml",
        help="directory to export linkML schema to",
        type=Path,
        default=Path(__file__).parent.parent
        / "nwb_models"
        / "src"
        / "nwb_models"
        / "schema"
        / "linkml",
    )
    parser.add_argument(
        "--pydantic",
        help="directory to export pydantic models",
        type=Path,
        default=Path(__file__).parent.parent
        / "nwb_models"
        / "src"
        / "nwb_models"
        / "models"
        / "pydantic",
    )
    parser.add_argument("--hdmf", help="Only generate the HDMF namespaces", action="store_true")
    parser.add_argument(
        "--latest",
        help="Only generate the latest version of the core schemas.",
        action="store_true",
    )
    parser.add_argument(
        "--dry-run",
        help=(
            "Generate schema and pydantic models without moving them into the target directories,"
            " for testing purposes"
        ),
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="Add annotations to generated schema that indicate how they were generated",
        action="store_true",
    )
    parser.add_argument("--pdb", help="Launch debugger on an error", action="store_true")
    return parser


def main():
    args = parser().parse_args()

    if args.debug:
        os.environ["NWB_LINKML_DEBUG"] = "true"
    else:
        if "NWB_LINKML_DEBUG" in os.environ:
            del os.environ["NWB_LINKML_DEBUG"]

    tmp_dir = make_tmp_dir(clear=True)
    git_dir = tmp_dir / "git"
    git_dir.mkdir(exist_ok=True)

    if args.hdmf:
        repo = GitRepo(HDMF_COMMON_REPO, path=git_dir)
    else:
        repo = GitRepo(NWB_CORE_REPO, path=git_dir)

    if not args.dry_run:
        args.yaml.mkdir(exist_ok=True)
        args.pydantic.mkdir(exist_ok=True)

    generate_versions(
        args.yaml, args.pydantic, args.dry_run, repo, pdb=args.pdb, latest=args.latest
    )


if __name__ == "__main__":
    main()
