#!/usr/bin/env python3
"""Finalize prompt telemetry in one mandatory path.

This script appends one metrics row to prompt_log.csv and writes a structured
TRACE record to .codexlog to confirm finalization.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CODEXLOG = Path("/home/peter216/git/www/.codexlog")
DEFAULT_PROMPT_LOG = Path("/home/peter216/git/ai/codex-settings/tmp/prompt_log.csv")
CSV_HEADER = "PROMPT_ID,BEGIN_TIME,END_TIME,NUM_LOGS,LOGS_PER_TEN_SEC\n"
MAX_FIELD_LEN = 200


def _truncate(value: str) -> str:
    return value[:MAX_FIELD_LEN]


def _truncate_details(details: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in details.items():
        if isinstance(value, str):
            output[key] = _truncate(value)
        else:
            output[key] = value
    return output


def _parse_iso(ts: str) -> datetime:
    parsed = datetime.fromisoformat(ts)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _ensure_prompt_log_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        path.write_text(CSV_HEADER, encoding="utf-8")
        return

    with path.open("r", encoding="utf-8") as f:
        first_line = f.readline()
    if first_line.strip() != CSV_HEADER.strip():
        with path.open("r", encoding="utf-8") as f:
            existing = f.read()
        path.write_text(CSV_HEADER + existing, encoding="utf-8")


def _collect_metrics(codexlog_path: Path, begin: datetime, end: datetime) -> tuple[int, int]:
    num_logs = 0
    malformed_lines = 0

    if not codexlog_path.exists():
        return 0, 0

    for raw in codexlog_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            malformed_lines += 1
            continue

        ts_value = record.get("ts")
        if not isinstance(ts_value, str):
            malformed_lines += 1
            continue

        try:
            ts = _parse_iso(ts_value)
        except ValueError:
            malformed_lines += 1
            continue

        if begin <= ts <= end:
            num_logs += 1

    return num_logs, malformed_lines


def _append_prompt_csv(path: Path, row: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(row)


def _append_codexlog(
    codexlog_path: Path,
    level: str,
    message: str,
    details: dict[str, Any],
    output: str,
) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": _truncate(level),
        "message": _truncate(message),
        "details": _truncate_details(details),
        "output": _truncate(output),
    }
    codexlog_path.parent.mkdir(parents=True, exist_ok=True)
    with codexlog_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_csv_header(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8") as f:
        first = f.readline().strip()
    return first == CSV_HEADER.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize prompt metrics and trace logs.")
    parser.add_argument("--begin-time", required=True, help="ISO timestamp of prompt start (UTC preferred).")
    parser.add_argument("--prompt-id", default="", help="Optional prompt id; generated if omitted.")
    parser.add_argument("--codexlog", default=str(DEFAULT_CODEXLOG), help="Path to .codexlog JSONL file.")
    parser.add_argument("--prompt-log", default=str(DEFAULT_PROMPT_LOG), help="Path to prompt_log.csv.")
    parser.add_argument("--min-rate", type=float, default=0.0, help="Optional minimum logs/10s threshold.")
    parser.add_argument("--dry-run", action="store_true", help="Compute and print metrics without writing files.")
    args = parser.parse_args()

    codexlog_path = Path(args.codexlog)
    prompt_log_path = Path(args.prompt_log)

    try:
        begin = _parse_iso(args.begin_time)
    except ValueError as exc:
        _append_codexlog(
            codexlog_path,
            "TRACE",
            "finalize_prompt skipped: invalid begin-time",
            {
                "intent": "Finalize prompt telemetry",
                "action": "Rejected invalid begin-time",
                "checks": "datetime.fromisoformat failed",
                "reasoning": f"Cannot compute prompt metrics: {exc}",
                "confidence": "95%",
            },
            "",
        )
        return 2

    end = datetime.now(timezone.utc)
    num_logs, malformed_lines = _collect_metrics(codexlog_path, begin, end)
    duration_seconds = max((end - begin).total_seconds(), 1.0)
    logs_per_ten = num_logs / (duration_seconds / 10.0)
    prompt_id = args.prompt_id or f"prompt-{begin.strftime('%Y%m%dT%H%M%S')}"
    row = (
        f"{prompt_id},"
        f"{begin.isoformat(timespec='seconds')},"
        f"{end.isoformat(timespec='seconds')},"
        f"{num_logs},"
        f"{logs_per_ten:.2f}\n"
    )

    if args.dry_run:
        print(row.strip())
        return 0

    try:
        _ensure_prompt_log_file(prompt_log_path)
        _append_prompt_csv(prompt_log_path, row)
        header_ok = _read_csv_header(prompt_log_path)
    except Exception as exc:
        _append_codexlog(
            codexlog_path,
            "TRACE",
            "finalize_prompt failed: prompt_log write error",
            {
                "intent": "Finalize prompt telemetry",
                "action": "Attempted prompt_log append",
                "checks": "write/permissions failed",
                "reasoning": f"prompt_log write failed: {exc}",
                "confidence": "90%",
            },
            "",
        )
        return 3

    min_rate = float(args.min_rate)
    threshold_note = ""
    if min_rate > 0.0 and logs_per_ten < min_rate:
        threshold_note = f"rate_below_threshold({logs_per_ten:.2f}<{min_rate:.2f})"

    _append_codexlog(
        codexlog_path,
        "TRACE",
        "finalize_prompt completed",
        {
            "intent": "Finalize prompt telemetry",
            "action": "Appended prompt_log row and completion event",
            "checks": (
                f"header_ok={header_ok}; malformed_codexlog_lines={malformed_lines}; "
                f"duration_s={duration_seconds:.1f}"
            ),
            "reasoning": "Single completion path reduces skipped telemetry writes.",
            "confidence": "92%",
        },
        f"{row.strip()}{'; ' + threshold_note if threshold_note else ''}",
    )

    print(row.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
