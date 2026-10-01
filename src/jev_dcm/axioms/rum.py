from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
from scipy.optimize import linprog


Distribution = Mapping[tuple[str, ...], Mapping[str, float]]


@dataclass(frozen=True)
class RUMResult:
    success: bool
    mean_l1: float
    total_l1: float
    n_rows: int
    n_rankings: int
    weights: np.ndarray | None = None


def _rows(distributions: Distribution) -> list[tuple[tuple[str, ...], str]]:
    rows: list[tuple[tuple[str, ...], str]] = []
    for menu in sorted(distributions, key=lambda m: (len(m), m)):
        rows.extend((menu, option) for option in menu)
    return rows


def rum_matrix(alternatives: Sequence[str], rows: Sequence[tuple[tuple[str, ...], str]]) -> tuple[np.ndarray, list[tuple[str, ...]]]:
    rankings = list(itertools.permutations(alternatives))
    A = np.zeros((len(rows), len(rankings)), dtype=float)
    for r_idx, ranking in enumerate(rankings):
        rank = {option: pos for pos, option in enumerate(ranking)}
        for row_idx, (menu, option) in enumerate(rows):
            chosen = min(menu, key=rank.__getitem__)
            if chosen == option:
                A[row_idx, r_idx] = 1.0
    return A, rankings


def rum_distance(distributions: Distribution, alternatives: Sequence[str] | None = None) -> RUMResult:
    """Minimum mean absolute distance to the random-ranking/RUM polytope.

    A probability distribution over all strict rankings induces menu choice probabilities
    by selecting the highest-ranked available alternative. We solve

        min_{lambda in simplex} ||A lambda - p||_1.

    For five alternatives this uses only 120 ranking columns.
    """
    if not distributions:
        return RUMResult(True, 0.0, 0.0, 0, 0, np.array([]))

    if alternatives is None:
        alternatives = sorted({x for menu in distributions for x in menu})
    alternatives = tuple(alternatives)
    rows = _rows(distributions)
    A, rankings = rum_matrix(alternatives, rows)
    p = np.array([float(distributions[menu][option]) for menu, option in rows], dtype=float)

    R, M = len(rankings), len(rows)
    # Variables: ranking masses lambda_R, absolute residual slacks u_M.
    c = np.concatenate([np.zeros(R), np.ones(M)])
    A_ub = np.vstack(
        [
            np.hstack([A, -np.eye(M)]),
            np.hstack([-A, -np.eye(M)]),
        ]
    )
    b_ub = np.concatenate([p, -p])
    A_eq = np.zeros((1, R + M))
    A_eq[0, :R] = 1.0
    b_eq = np.array([1.0])
    bounds = [(0.0, None)] * (R + M)

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not result.success:
        return RUMResult(False, float("nan"), float("nan"), M, R, None)
    total = float(result.fun)
    return RUMResult(True, total / M if M else 0.0, total, M, R, result.x[:R])
