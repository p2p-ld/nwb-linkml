"""
Utility functions for dealing with yaml files.

No we are not going to implement a yaml parser here
"""
import re
from pathlib import Path
from typing import Literal, List, Union, overload


@overload
def yaml_peek(key: str, path: Union[str, Path], root:bool = True, first:Literal[True]=True) -> str: ...

@overload
def yaml_peek(key: str, path: Union[str, Path], root:bool = True, first:Literal[False]=False) -> List[str]: ...

@overload
def yaml_peek(key: str, path: Union[str, Path], root:bool = True, first:bool=True) -> Union[str, List[str]]: ...

def yaml_peek(key: str, path: Union[str, Path], root:bool = True, first:bool=True) -> Union[str, List[str]]:
    """
    Peek into a yaml file without parsing the whole file to retrieve the value of a single key.

    This function is _not_ designed for robustness to the yaml spec, it is for simple key: value
    pairs, not fancy shit like multiline strings, tagged values, etc. If you want it to be,
    then i'm afraid you'll have to make a PR about it.

    Returns a string no matter what the yaml type is so ya have to do your own casting if you want

    Args:
        key (str): The key to peek for
        path (:class:`pathlib.Path` , str): The yaml file to peek into
        root (bool): Only find keys at the root of the document (default ``True`` ), otherwise
            find keys at any level of nesting.
        first (bool): Only return the first appearance of the key (default). Otherwise return a
            list of values (not implemented lol)

    Returns:
        str
    """
    if root:
        pattern = re.compile(rf'^(?P<key>{key}):\s*(?P<value>\S.*)')
    else:
        pattern = re.compile(rf'^\s*(?P<key>{key}):\s*(?P<value>\S.*)')

    res = None
    if first:
        with open(path, 'r') as yfile:
            for l in yfile:
                res = pattern.match(l)
                if res:
                    break
        if res:
            return res.groupdict()['value']
    else:
        with open(path, 'r') as yfile:
            text = yfile.read()
        res = [match.groupdict()['value'] for match in pattern.finditer(text)]
        if res:
            return res

    raise KeyError(f'Key {key} not found in {path}')

