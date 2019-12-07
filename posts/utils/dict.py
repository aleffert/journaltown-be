from typing import List


def without(d: dict, keys: List[str]) -> dict:
    return {
        key: d[key]
        for key in d
        if key not in keys
    }
