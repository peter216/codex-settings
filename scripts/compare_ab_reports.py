#!/usr/bin/env python3
"""Compare two logging A/B harness report JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: report must be a JSON object")
    return data


def _metrics(report: dict[str, Any]) -> dict[str, Any]:
    metrics = report.get("metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    return metrics


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_comparison(report_a: dict[str, Any], report_b: dict[str, Any]) -> dict[str, Any]:
    metrics_a = _metrics(report_a)
    metrics_b = _metrics(report_b)

    a_rate = _as_float(metrics_a.get("logs_per_ten_sec"))
    b_rate = _as_float(metrics_b.get("logs_per_ten_sec"))
    a_num = _as_int(metrics_a.get("num_logs"))
    b_num = _as_int(metrics_b.get("num_logs"))
    a_dur = _as_float(metrics_a.get("duration_seconds"))
    b_dur = _as_float(metrics_b.get("duration_seconds"))

    phases_a = metrics_a.get("logs_by_phase", {})
    phases_b = metrics_b.get("logs_by_phase", {})
    if not isinstance(phases_a, dict):
        phases_a = {}
    if not isinstance(phases_b, dict):
        phases_b = {}

    all_phases = sorted(set(phases_a.keys()) | set(phases_b.keys()))
    phase_deltas = []
    for phase in all_phases:
        a_val = _as_int(phases_a.get(phase))
        b_val = _as_int(phases_b.get(phase))
        phase_deltas.append(
            {
                "phase": phase,
                "a": a_val,
                "b": b_val,
                "delta": b_val - a_val,
            }
        )

    better_variant = "tie"
    if b_rate > a_rate:
        better_variant = "B"
    elif a_rate > b_rate:
        better_variant = "A"

    return {
        "run_a": {
            "run_id": report_a.get("run_id", ""),
            "variant": report_a.get("variant", "A"),
            "logs_per_ten_sec": a_rate,
            "num_logs": a_num,
            "duration_seconds": a_dur,
        },
        "run_b": {
            "run_id": report_b.get("run_id", ""),
            "variant": report_b.get("variant", "B"),
            "logs_per_ten_sec": b_rate,
            "num_logs": b_num,
            "duration_seconds": b_dur,
        },
        "delta": {
            "logs_per_ten_sec": round(b_rate - a_rate, 4),
            "num_logs": b_num - a_num,
            "duration_seconds": round(b_dur - a_dur, 4),
        },
        "winner_by_rate": better_variant,
        "phase_deltas": phase_deltas,
    }


def print_text(summary: dict[str, Any]) -> None:
    run_a = summary["run_a"]
    run_b = summary["run_b"]
    delta = summary["delta"]
    winner = summary["winner_by_rate"]

    print("A/B Comparison Summary")
    print(
        f"A ({run_a['variant']}:{run_a['run_id']}): "
        f"rate={run_a['logs_per_ten_sec']:.2f}, logs={run_a['num_logs']}, dur={run_a['duration_seconds']:.2f}s"
    )
    print(
        f"B ({run_b['variant']}:{run_b['run_id']}): "
        f"rate={run_b['logs_per_ten_sec']:.2f}, logs={run_b['num_logs']}, dur={run_b['duration_seconds']:.2f}s"
    )
    print(
        f"Delta (B-A): rate={delta['logs_per_ten_sec']:.2f}, "
        f"logs={delta['num_logs']}, dur={delta['duration_seconds']:.2f}s, winner={winner}"
    )
    print("Phase deltas (B-A):")
    for row in summary["phase_deltas"]:
        print(f"  {row['phase']}: A={row['a']} B={row['b']} delta={row['delta']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two logging A/B harness reports.")
    parser.add_argument("--a", required=True, help="Path to report A JSON.")
    parser.add_argument("--b", required=True, help="Path to report B JSON.")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    report_a = _load_report(Path(args.a))
    report_b = _load_report(Path(args.b))
    summary = build_comparison(report_a, report_b)

    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_text(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
