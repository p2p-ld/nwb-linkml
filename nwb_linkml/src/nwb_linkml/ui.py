"""
UI Elements :)
"""

from typing import TYPE_CHECKING

from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Column, Progress, SpinnerColumn, TextColumn

if TYPE_CHECKING:
    from nwb_linkml.adapters.namespaces import NamespacesAdapter


class AdapterProgress:
    def __init__(self, ns: "NamespacesAdapter"):
        self.ns = ns
        self.task_ids = {}

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn(
                "[bold blue]{task.fields[name]} - [bold red]{task.fields[action]}",
                table_column=Column(ratio=1),
            ),
            BarColumn(table_column=Column(ratio=1), bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            expand=True,
        )

        # add tasks for each namespace
        for an_ns in self.ns.namespaces.namespaces:
            ns_schemas = self.ns.namespace_schemas(an_ns.name)
            self.task_ids[an_ns.name] = self.progress.add_task(
                "", name=an_ns.name, action="", total=len(ns_schemas)
            )
        for imported_ns in self.ns.imported:
            for an_ns in imported_ns.namespaces.namespaces:
                ns_schemas = imported_ns.namespace_schemas(an_ns.name)
                self.task_ids[an_ns.name] = self.progress.add_task(
                    "", name=an_ns.name, action="", total=len(ns_schemas)
                )

        self.panel = Panel(
            self.progress, title="Building Namespaces", border_style="green", padding=(2, 2)
        )

    def update(self, namespace: str, **kwargs) -> None:
        self.progress.update(self.task_ids[namespace], **kwargs)

    def start(self) -> None:
        self.progress.start()

    def stop(self) -> None:
        self.progress.stop()

    def __enter__(self) -> Live:
        self._live = Live(self.panel)
        return self._live.__enter__()

    def __exit__(self, *args):
        return self._live.__exit__(*args)
