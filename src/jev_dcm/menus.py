from __future__ import annotations

import itertools
import math
import random
from collections.abc import Iterable, Sequence


def all_menus(alternatives: Sequence[str], min_size: int = 2) -> list[tuple[str, ...]]:
    """Return every subset/menu of ``alternatives`` with size >= ``min_size``.

    Menus inherit the canonical order of ``alternatives``. For five alternatives and
    ``min_size=2`` this returns 26 menus.
    """
    xs = tuple(alternatives)
    return [menu for k in range(min_size, len(xs) + 1) for menu in itertools.combinations(xs, k)]


def menu_permutations(menu: Sequence[str], n: int, rng: random.Random) -> list[tuple[str, ...]]:
    """Canonical order first, followed by up to ``n-1`` unique random permutations."""
    canonical = tuple(menu)
    if n <= 1 or len(canonical) <= 1:
        return [canonical]

    target = min(n, math.factorial(len(canonical)))
    seen = {canonical}
    out = [canonical]

    # Small menus have tiny permutation spaces; exhaustive enumeration avoids a
    # rejection-sampling tail when target approaches k!.
    if math.factorial(len(canonical)) <= 24:
        rest = [p for p in itertools.permutations(canonical) if p != canonical]
        rng.shuffle(rest)
        out.extend(rest[: target - 1])
        return out

    while len(out) < target:
        p = list(canonical)
        rng.shuffle(p)
        t = tuple(p)
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def is_subset_menu(a: Iterable[str], b: Iterable[str]) -> bool:
    aa, bb = frozenset(a), frozenset(b)
    return aa < bb
