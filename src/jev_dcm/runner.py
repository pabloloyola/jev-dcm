from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from .client import KevClient
from .menus import all_menus, menu_permutations
from .probes import ProbeState


INSTRUCTIONS = (
    "Choose the best option among the available alternatives using only the decision rule and context in the state."
)


def _qid(menu_index: int, permutation_index: int) -> str:
    return f"m{menu_index:02d}_p{permutation_index:02d}"


def run_probe(
    probe: ProbeState,
    client: KevClient,
    permutations: int = 3,
    seed: int = 20261001,
) -> list[dict[str, Any]]:
    """Evaluate every nontrivial menu for one state in one packed SystemOne request."""
    rng = random.Random(f"{seed}:{probe.state_id}")
    alt_names = tuple(probe.alternatives)
    questions: dict[str, dict[str, Any]] = {}
    meta: dict[str, tuple[tuple[str, ...], int, tuple[str, ...]]] = {}

    for m_idx, menu in enumerate(all_menus(alt_names)):
        for p_idx, order in enumerate(menu_permutations(menu, permutations, rng)):
            qid = _qid(m_idx, p_idx)
            criteria = {name: probe.alternatives[name] for name in order}
            questions[qid] = {"type": "choice", "instructions": INSTRUCTIONS, "criteria": criteria}
            meta[qid] = (menu, p_idx, order)

    body = client.system_one(probe.state, questions)
    answers = body["answers"]
    rows: list[dict[str, Any]] = []
    for qid, (menu, p_idx, order) in meta.items():
        answer = answers[qid]
        probs = answer.get("probabilities")
        if not isinstance(probs, dict):
            raise ValueError(f"question {qid} did not return choice probabilities: {answer}")
        rows.append(
            {
                "state_id": probe.state_id,
                "regime": probe.regime,
                "menu": list(menu),
                "permutation_index": p_idx,
                "order": list(order),
                "probabilities": {k: float(v) for k, v in probs.items()},
                "choice": answer.get("choice"),
                "confidence": answer.get("confidence"),
                "model": body.get("model", client.model),
                "latency_ms": body.get("latency_ms"),
            }
        )
    return rows


def run_probes(
    probes: list[ProbeState],
    client: KevClient,
    output: str | Path,
    permutations: int = 3,
    seed: int = 20261001,
) -> list[dict[str, Any]]:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, Any]] = []
    with path.open("w", encoding="utf-8") as f:
        for probe in probes:
            rows = run_probe(probe, client, permutations=permutations, seed=seed)
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            all_rows.extend(rows)
    return all_rows


def read_rows(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
