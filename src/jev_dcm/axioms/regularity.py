from __future__ import annotations

from typing import Mapping


Distribution = Mapping[tuple[str, ...], Mapping[str, float]]


def regularity_violations(distributions: Distribution, tol: float = 1e-8) -> list[dict[str, object]]:
    """Find C subset D for which P(i|D) > P(i|C).

    Every menu-independent random-utility model obeys regularity.
    """
    menus = list(distributions)
    out: list[dict[str, object]] = []
    for small in menus:
        sset = set(small)
        for large in menus:
            lset = set(large)
            if not sset < lset:
                continue
            for option in small:
                delta = float(distributions[large][option]) - float(distributions[small][option])
                if delta > tol:
                    out.append(
                        {
                            "small_menu": list(small),
                            "large_menu": list(large),
                            "option": option,
                            "delta": delta,
                        }
                    )
    return out


def summarize_regularity(distributions: Distribution, tol: float = 1e-8) -> dict[str, float]:
    menus = list(distributions)
    comparisons = 0
    for small in menus:
        sset = set(small)
        for large in menus:
            if sset < set(large):
                comparisons += len(small)
    violations = regularity_violations(distributions, tol=tol)
    return {
        "regularity_comparisons": float(comparisons),
        "regularity_violations": float(len(violations)),
        "regularity_violation_rate": (len(violations) / comparisons) if comparisons else 0.0,
        "regularity_max_delta": max((float(v["delta"]) for v in violations), default=0.0),
    }
