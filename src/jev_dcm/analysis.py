from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from .axioms.iia import summarize_iia
from .axioms.regularity import summarize_regularity
from .axioms.rum import rum_distance


def _menu_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(row["menu"])


def distributions_for_state(rows: list[dict[str, Any]], symmetrize: bool) -> dict[tuple[str, ...], dict[str, float]]:
    if not symmetrize:
        return {
            _menu_key(row): {k: float(v) for k, v in row["probabilities"].items()}
            for row in rows
            if int(row["permutation_index"]) == 0
        }

    grouped: dict[tuple[str, ...], list[dict[str, float]]] = defaultdict(list)
    for row in rows:
        grouped[_menu_key(row)].append({k: float(v) for k, v in row["probabilities"].items()})
    out: dict[tuple[str, ...], dict[str, float]] = {}
    for menu, ps in grouped.items():
        averaged = {option: mean(p[option] for p in ps) for option in menu}
        z = sum(averaged.values())
        out[menu] = {k: v / z for k, v in averaged.items()} if z else {k: 1 / len(menu) for k in menu}
    return out


def order_sensitivity(rows: list[dict[str, Any]]) -> dict[str, float]:
    grouped: dict[tuple[str, ...], list[dict[str, float]]] = defaultdict(list)
    for row in rows:
        grouped[_menu_key(row)].append({k: float(v) for k, v in row["probabilities"].items()})

    spreads = []
    unstable = 0
    comparable = 0
    for menu, ps in grouped.items():
        if len(ps) < 2:
            continue
        comparable += 1
        for option in menu:
            xs = [p[option] for p in ps]
            spreads.append(max(xs) - min(xs))
        argmaxes = {max(menu, key=p.__getitem__) for p in ps}
        unstable += len(argmaxes) > 1
    return {
        "order_probability_spread_mean": mean(spreads) if spreads else 0.0,
        "order_probability_spread_max": max(spreads, default=0.0),
        "order_argmax_instability_rate": unstable / comparable if comparable else 0.0,
    }


def analyze_state(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("state has no rows")
    result: dict[str, Any] = {
        "state_id": rows[0]["state_id"],
        "regime": rows[0]["regime"],
        **order_sensitivity(rows),
    }
    for label, sym in (("canonical", False), ("symmetrized", True)):
        dists = distributions_for_state(rows, symmetrize=sym)
        rum = rum_distance(dists)
        metrics = {
            **summarize_iia(dists),
            **summarize_regularity(dists),
            "rum_success": rum.success,
            "rum_mean_l1": rum.mean_l1,
            "rum_total_l1": rum.total_l1,
        }
        result[label] = metrics
    return result


def _aggregate(states: list[dict[str, Any]]) -> dict[str, Any]:
    if not states:
        return {}
    scalar_paths = [
        ("order_probability_spread_mean",),
        ("order_probability_spread_max",),
        ("order_argmax_instability_rate",),
        ("canonical", "iia_log_odds_span_mean"),
        ("canonical", "iia_log_odds_span_max"),
        ("canonical", "regularity_violation_rate"),
        ("canonical", "regularity_max_delta"),
        ("canonical", "rum_mean_l1"),
        ("symmetrized", "iia_log_odds_span_mean"),
        ("symmetrized", "iia_log_odds_span_max"),
        ("symmetrized", "regularity_violation_rate"),
        ("symmetrized", "regularity_max_delta"),
        ("symmetrized", "rum_mean_l1"),
    ]
    out: dict[str, Any] = {"n_states": len(states)}
    for path in scalar_paths:
        vals = []
        for s in states:
            cur: Any = s
            for part in path:
                cur = cur[part]
            vals.append(float(cur))
        out["_".join(path) + "_mean"] = mean(vals)
    return out


def analyze_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_state: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_state[row["state_id"]].append(row)
    states = [analyze_state(by_state[sid]) for sid in sorted(by_state)]

    by_regime: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for state in states:
        by_regime[state["regime"]].append(state)
    return {
        "summary": _aggregate(states),
        "by_regime": {regime: _aggregate(xs) for regime, xs in sorted(by_regime.items())},
        "states": states,
    }


def report_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# Experiment 00 — Menu Geometry",
        "",
        f"States analyzed: **{s.get('n_states', 0)}**",
        "",
        "## Overall",
        "",
        "| metric | mean |",
        "|---|---:|",
    ]
    preferred = [
        "order_probability_spread_mean_mean",
        "order_argmax_instability_rate_mean",
        "canonical_iia_log_odds_span_mean_mean",
        "canonical_regularity_violation_rate_mean",
        "canonical_rum_mean_l1_mean",
        "symmetrized_iia_log_odds_span_mean_mean",
        "symmetrized_regularity_violation_rate_mean",
        "symmetrized_rum_mean_l1_mean",
    ]
    for key in preferred:
        if key in s:
            lines.append(f"| `{key}` | {s[key]:.8g} |")

    lines += ["", "## By regime", ""]
    for regime, stats in report["by_regime"].items():
        lines.append(f"### {regime}")
        lines.append("")
        lines.append(f"States: {stats['n_states']}")
        lines.append("")
        for key in preferred:
            if key in stats:
                lines.append(f"- `{key}`: {stats[key]:.8g}")
        lines.append("")
    return "\n".join(lines)


def write_report(out_dir: str | Path, report: dict[str, Any]) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "report.md").write_text(report_markdown(report), encoding="utf-8")
