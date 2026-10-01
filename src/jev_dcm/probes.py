from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProbeState:
    state_id: str
    regime: str
    state: dict[str, Any]
    alternatives: dict[str, str]


def _weighted_utility(idx: int, rng: random.Random) -> ProbeState:
    w_cost = rng.choice([1, 2, 3])
    w_quality = rng.choice([1, 2, 3])
    w_speed = rng.choice([1, 2, 3])
    alts: dict[str, str] = {}
    for j, name in enumerate("ABCDE"):
        cost = rng.randint(2, 9)
        quality = rng.randint(2, 9)
        speed = rng.randint(2, 9)
        alts[name] = f"cost={cost}; quality={quality}; speed={speed}"
    return ProbeState(
        f"weighted_{idx:04d}",
        "weighted_utility",
        {
            "task": "Choose the available option with the highest utility.",
            "utility_rule": f"utility = {w_quality}*quality + {w_speed}*speed - {w_cost}*cost",
            "tie_break": "If utilities are exactly equal, prefer the alphabetically earlier option name.",
        },
        alts,
    )


def _lexicographic(idx: int, rng: random.Random) -> ProbeState:
    alts: dict[str, str] = {}
    for name in "ABCDE":
        risk = rng.randint(1, 5)
        benefit = rng.randint(1, 9)
        cost = rng.randint(1, 9)
        alts[name] = f"risk={risk}; benefit={benefit}; cost={cost}"
    return ProbeState(
        f"lexicographic_{idx:04d}",
        "lexicographic",
        {
            "task": "Choose among the available options using the rule below.",
            "rule": "First minimize risk. Among tied lowest-risk options maximize benefit. If still tied, minimize cost.",
        },
        alts,
    )


def _dominance(idx: int, rng: random.Random) -> ProbeState:
    base = rng.randint(2, 4)
    alts = {
        "A": f"quality={base+5}; reliability={base+5}; cost={base}",
        "B": f"quality={base+3}; reliability={base+4}; cost={base+1}",
        "C": f"quality={base+2}; reliability={base+2}; cost={base+3}",
        "D": f"quality={base+1}; reliability={base+3}; cost={base+4}",
        "E": f"quality={base}; reliability={base+1}; cost={base+5}",
    }
    return ProbeState(
        f"dominance_{idx:04d}",
        "dominance",
        {
            "task": "Choose the best available option.",
            "rule": "Higher quality and reliability are better; lower cost is better. Prefer an option that Pareto-dominates another.",
        },
        alts,
    )


def _semantic_clones(idx: int, rng: random.Random) -> ProbeState:
    city = rng.choice(["Tokyo", "Osaka", "Yokohama", "Nagoya"])
    alts = {
        "A": f"A quiet cafe in {city}, 4 minutes away, excellent coffee, moderate price.",
        "B": f"A calm coffee shop in {city}, 5 minutes away, excellent coffee, moderate price.",
        "C": f"A lively cafe in {city}, 3 minutes away, good coffee, low price.",
        "D": f"A quiet tea house in {city}, 8 minutes away, excellent tea, moderate price.",
        "E": f"A premium bakery cafe in {city}, 6 minutes away, very good coffee, high price.",
    }
    return ProbeState(
        f"clones_{idx:04d}",
        "semantic_clones",
        {
            "task": "Choose the best available place for a focused one-hour conversation.",
            "preferences": "Quietness matters most, then drink quality, then walking time, then price.",
        },
        alts,
    )


def _underspecified(idx: int, rng: random.Random) -> ProbeState:
    theme = rng.choice(["project plan", "travel option", "candidate design", "vendor", "research direction"])
    alts = {
        "A": "Conservative, predictable, and easy to explain.",
        "B": "Fast and ambitious, with meaningful execution risk.",
        "C": "Flexible and balanced, but not best on any single dimension.",
        "D": "Novel and potentially high-upside, with sparse evidence.",
        "E": "Low-cost and reversible, but likely lower upside.",
    }
    return ProbeState(
        f"underspecified_{idx:04d}",
        "underspecified",
        {
            "task": f"Choose the best available {theme}.",
            "context": "No additional preference information is available. Make the most defensible choice from the descriptions.",
        },
        alts,
    )


_FACTORIES = [_weighted_utility, _lexicographic, _dominance, _semantic_clones, _underspecified]


def generate_probes(n_states: int, seed: int = 20261001) -> list[ProbeState]:
    rng = random.Random(seed)
    probes = []
    for i in range(n_states):
        factory = _FACTORIES[i % len(_FACTORIES)]
        probes.append(factory(i, rng))
    return probes


def write_probes(path: str | Path, probes: list[ProbeState]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for probe in probes:
            f.write(json.dumps(asdict(probe), ensure_ascii=False) + "\n")


def read_probes(path: str | Path) -> list[ProbeState]:
    out = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(ProbeState(**json.loads(line)))
    return out
