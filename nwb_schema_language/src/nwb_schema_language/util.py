"""
The fabled junk drawer
"""

import re
import textwrap
from pprint import pformat as _pformat


def pformat(fields: dict, cls_name: str, indent: str = "  ") -> str:
    """
    pretty format the fields of the items of a ``YAMLRoot`` object without the
    wonky indentation of pformat.

    formatting is similar to black -
    items at similar levels of nesting have similar levels of indentation,
    rather than getting placed at essentially random levels of indentation
    depending on what came before them.
    """
    res = []
    total_len = 0
    for key, val in fields.items():
        if val == [] or val == {} or val is None:
            continue
        # pformat handles everything else that isn't a YAMLRoot object,
        # but it sure does look ugly
        # use it to split lines and as the thing of last resort,
        # but otherwise indent = 0, we'll do that
        val_str = _pformat(val, indent=0, compact=True, sort_dicts=False)
        # now we indent everything except the first line by indenting
        # and then using regex to remove just the first indent
        val_str = re.sub(rf"\A{re.escape(indent)}", "", textwrap.indent(val_str, indent))
        # now recombine with the key in a format that can be re-eval'd
        # into an object if indent is just whitespace
        val_str = f"'{key}': " + val_str

        # count the total length of this string so we know if we need to linebreak or not later
        total_len += len(val_str)
        res.append(val_str)

    if total_len > 80:
        inside = ",\n".join(res)
        # we indent twice - once for the inner contents of every inner object, and one to
        # offset from the root element. that keeps us from needing to be recursive except for the
        # single pformat call
        inside = textwrap.indent(inside, indent)
        return cls_name + "({\n" + inside + "\n})"
    else:
        return cls_name + "({" + ", ".join(res) + "})"
