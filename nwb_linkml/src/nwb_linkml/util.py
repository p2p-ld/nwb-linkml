"""
The much maligned junk drawer
"""


def merge_dicts(
    source: dict, target: dict, list_key: str | None = None, exclude: list[str] | None = None
) -> dict:
    """
    Deeply merge nested dictionaries, replacing already-declared keys rather than
    e.g. merging lists as well

    Args:
        source (dict): source dictionary
        target (dict): target dictionary (values merged over source)
        list_key (str | None): Optional: if present, merge lists of dicts using this to
            identify matching dicts
        exclude: (list[str] | None): Optional: if present, exclude keys from parent.

    References:
        https://stackoverflow.com/a/20666342/13113166

    """
    if exclude is None:
        exclude = []
    ret = {k: v for k, v in source.items() if k not in exclude}
    for key, value in target.items():
        if key not in ret:
            ret[key] = value
        elif isinstance(value, dict):
            if key in ret:
                ret[key] = merge_dicts(ret[key], value, list_key, exclude)
            else:
                ret[key] = value
        elif isinstance(value, list) and list_key and all([isinstance(v, dict) for v in value]):
            src_keys = {v[list_key]: ret[key].index(v) for v in ret.get(key, {}) if list_key in v}
            target_keys = {v[list_key]: value.index(v) for v in value if list_key in v}

            # all dicts not in target
            # screwy double iteration to preserve dict order
            new_val = [
                ret[key][src_keys[k]]
                for k in src_keys
                if k in set(src_keys.keys()) - set(target_keys.keys())
            ]
            # all dicts not in source
            new_val.extend(
                [
                    value[target_keys[k]]
                    for k in target_keys
                    if k in set(target_keys.keys()) - set(src_keys.keys())
                ]
            )
            # merge dicts in both
            new_val.extend(
                [
                    merge_dicts(ret[key][src_keys[k]], value[target_keys[k]], list_key, exclude)
                    for k in target_keys
                    if k in set(src_keys.keys()).intersection(set(target_keys.keys()))
                ]
            )
            new_val = sorted(new_val, key=lambda i: i[list_key])
            # add any dicts that don't have the list_key
            # they can't be merged since they can't be matched
            new_val.extend([v for v in ret.get(key, {}) if list_key not in v])
            new_val.extend([v for v in value if list_key not in v])

            ret[key] = new_val

        else:
            ret[key] = value

    return ret
