from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyze_rows, write_report
from .client import KevClient
from .probes import generate_probes, read_probes, write_probes
from .runner import read_rows, run_probes


def _client(args: argparse.Namespace) -> KevClient:
    return KevClient(base_url=args.base_url, model=args.model, timeout=args.timeout)


def cmd_generate(args: argparse.Namespace) -> None:
    probes = generate_probes(args.n_states, seed=args.seed)
    write_probes(args.out, probes)
    print(f"wrote {len(probes)} states to {args.out}")


def cmd_run(args: argparse.Namespace) -> None:
    probes = read_probes(args.input)
    rows = run_probes(
        probes,
        _client(args),
        args.out,
        permutations=args.permutations,
        seed=args.seed,
    )
    print(f"wrote {len(rows)} menu/permutation rows to {args.out}")


def cmd_analyze(args: argparse.Namespace) -> None:
    rows = read_rows(args.input)
    report = analyze_rows(rows)
    write_report(args.out_dir, report)
    print(f"wrote report.json and report.md to {args.out_dir}")


def cmd_exp00(args: argparse.Namespace) -> None:
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    probes_path = out / "probes.jsonl"
    raw_path = out / "raw.jsonl"

    probes = generate_probes(args.n_states, seed=args.seed)
    write_probes(probes_path, probes)
    rows = run_probes(
        probes,
        _client(args),
        raw_path,
        permutations=args.permutations,
        seed=args.seed,
    )
    report = analyze_rows(rows)
    write_report(out, report)
    print(f"experiment complete: {len(probes)} states, {len(rows)} rows -> {out}")


def _add_server_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--base-url", default="http://127.0.0.1:8009")
    p.add_argument("--model", default="kev-latest")
    p.add_argument("--timeout", type=float, default=120.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jev-dcm")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="generate controlled probe states")
    p.add_argument("--n-states", type=int, default=20)
    p.add_argument("--seed", type=int, default=20261001)
    p.add_argument("--out", default="data/probes.jsonl")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("run", help="query a running Kev server")
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--permutations", type=int, default=3)
    p.add_argument("--seed", type=int, default=20261001)
    _add_server_args(p)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("analyze", help="analyze recorded choice probabilities")
    p.add_argument("--input", required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("exp00", help="generate, query, and analyze Experiment 00")
    p.add_argument("--n-states", type=int, default=20)
    p.add_argument("--permutations", type=int, default=3)
    p.add_argument("--seed", type=int, default=20261001)
    p.add_argument("--out-dir", default="runs/exp00")
    _add_server_args(p)
    p.set_defaults(func=cmd_exp00)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "n_states", 1) < 1:
        parser.error("--n-states must be >= 1")
    if getattr(args, "permutations", 1) < 1:
        parser.error("--permutations must be >= 1")
    args.func(args)


if __name__ == "__main__":
    main()
