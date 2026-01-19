#!/usr/bin/env python3
"""Test case to verify scanner catches the hash() TypeError"""


# This should trigger the scanner
def bad_example():
    kwargs = {"rebar_positions": [(1, 2), (3, 4)], "xu": 100}
    cache_key = f"viz_{hash(frozenset(kwargs.items()))}"  # ❌ Should be detected!
    return cache_key


# This should also be detected
def another_bad_example():
    data = {"items": [1, 2, 3]}
    key = hash(frozenset(data.items()))  # ❌ Should be detected!
    return key


# Good example (converted to tuples)
def good_example():
    def make_hashable(obj):
        if isinstance(obj, (list, tuple)):
            return tuple(make_hashable(item) for item in obj)
        elif isinstance(obj, dict):
            return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
        else:
            return obj

    kwargs = {"rebar_positions": [(1, 2), (3, 4)], "xu": 100}
    hashable_kwargs = make_hashable(kwargs)
    cache_key = f"viz_{hash(hashable_kwargs)}"  # ✅ Safe!
    return cache_key
