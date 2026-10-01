from __future__ import annotations

import itertools
import math
from collections import defaultdict
from typing import Mapping


Distribution = Mapping[tuple[str, ...], Mapping[str, float]]


def iia_log_odds_spans(distributions: Distribution, eps: float = 1e-8) -> dict[tuple[str, str], float]:
    """Return the menu-to-menu span of log odds for every observed alternative pair.

    Under Luce/MNL, log(P(i|C)/P(j|C)) is invariant to the other alternatives in C.
    """
    values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for menu, p in distributions.items():
        for i, j in itertools.combinations(menu, 2):
            a, b = sorted((i, j))
            pa, pb = max(float(p[a]), eps), max(float(p[b]), eps)
            values[(a, b)].append(math.log(pa / pb))
    return {pair: max(xs) - min(xs) for pair, xs in values.items() if len(xs) >= 2}


def summarize_iia(distributions: Distribution) -> dict[str, float]:
    spans = list(iia_log_odds_spans(distributions).values())
    if not spans:
        return {"iia_log_odds_span_mean": 0.0, "iia_log_odds_span_max": 0.0}
    return {
        "iia_log_odds_span_mean": sum(spans) / len(spans),
        "iia_log_odds_span_max": max(spans),
    }
