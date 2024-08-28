"""
Monkeypatches to external modules
"""

# ruff: noqa: ANN001 - not well defined types for this module


def patch_array_expression() -> None:
    """
    Allow SlotDefinitions to use `any_of` with `array`

    see: https://github.com/linkml/linkml-model/issues/199
    """
    from dataclasses import field, make_dataclass
    from typing import Optional

    from linkml_runtime.linkml_model import meta, types

    new_dataclass = make_dataclass(
        "AnonymousSlotExpression",
        fields=[("array", Optional[meta.ArrayExpression], field(default=None))],
        bases=(meta.AnonymousSlotExpression,),
    )
    meta.AnonymousSlotExpression = new_dataclass
    types.AnonymousSlotExpression = new_dataclass


def apply_patches() -> None:
    """Apply all monkeypatches"""
    patch_array_expression()
