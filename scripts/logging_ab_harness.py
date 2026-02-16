#!/usr/bin/env python3
"""Deterministic A/B harness for codex logging behavior.

This harness intentionally creates a multi-step, granular workload and computes
metrics only from events tagged with the current run ID. It restores all
tracked files to their pre-run state so each execution starts from scratch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


DEFAULT_WORKSPACE = Path("/home/peter216/git/www")
DEFAULT_CODEXLOG = DEFAULT_WORKSPACE / ".codexlog"
DEFAULT_PROMPT_LOG = Path("/home/peter216/git/ai/codex-settings/tmp/prompt_log.csv")


@dataclass
class Snapshot:
    path: Path
    existed: bool
    content: bytes


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(ts: datetime) -> str:
    return ts.isoformat(timespec="seconds")


def _read_snapshot(path: Path) -> Snapshot:
    if path.exists():
        return Snapshot(path=path, existed=True, content=path.read_bytes())
    return Snapshot(path=path, existed=False, content=b"")


def _restore_snapshot(snapshot: Snapshot) -> None:
    snapshot.path.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.existed:
        snapshot.path.write_bytes(snapshot.content)
    elif snapshot.path.exists():
        snapshot.path.unlink()


def _truncate(value: str, max_len: int = 200) -> str:
    return value[:max_len]


def _emit_log(
    codexlog: Path,
    run_id: str,
    phase: str,
    message: str,
    details: dict[str, Any],
    output: str = "",
) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": "TRACE",
        "message": _truncate(message),
        "details": {
            "run_id": run_id,
            "phase": phase,
            "intent": _truncate(str(details.get("intent", ""))),
            "action": _truncate(str(details.get("action", ""))),
            "checks": _truncate(str(details.get("checks", ""))),
            "reasoning": _truncate(str(details.get("reasoning", ""))),
            "confidence": _truncate(str(details.get("confidence", ""))),
            "directive": _truncate(
                "Exclude tasks/decisions from previous runs; calculate metrics only for this run_id."
            ),
        },
        "output": _truncate(output),
    }
    codexlog.parent.mkdir(parents=True, exist_ok=True)
    with codexlog.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _workload_steps() -> list[tuple[str, Callable[[Path], str]]]:
    def step01_create_layout(root: Path) -> str:
        for rel in ("src", "tests", "docs", "data"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        return "created dirs: src/tests/docs/data"

    def step02_seed_files(root: Path) -> str:
        (root / "src" / "calc.py").write_text(
            "def add(a, b):\n    return a + b\n\n\ndef scale(values, factor):\n    return [v * factor for v in values]\n",
            encoding="utf-8",
        )
        (root / "tests" / "test_calc.py").write_text(
            "from src.calc import add, scale\n\n\ndef test_add():\n    assert add(2, 3) == 5\n\n\ndef test_scale():\n    assert scale([1, 2], 3) == [3, 6]\n",
            encoding="utf-8",
        )
        (root / "docs" / "notes.md").write_text(
            "# Notes\n\n- TODO: add negative tests\n- TODO: add boundary tests\n",
            encoding="utf-8",
        )
        (root / "data" / "payload.json").write_text(
            json.dumps({"name": "fixture", "values": [1, 2, 3], "enabled": True}, indent=2) + "\n",
            encoding="utf-8",
        )
        return "seeded calc.py/test_calc.py/notes.md/payload.json"

    def step03_count_lines(root: Path) -> str:
        total = 0
        for p in root.rglob("*"):
            if p.is_file():
                total += sum(1 for _ in p.open("r", encoding="utf-8"))
        return f"total_lines={total}"

    def step04_find_todos(root: Path) -> str:
        count = 0
        for p in root.rglob("*.md"):
            text = p.read_text(encoding="utf-8")
            count += text.count("TODO")
        return f"todo_count={count}"

    def step05_update_payload(root: Path) -> str:
        payload_path = root / "data" / "payload.json"
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        payload["run_tag"] = "ab-test"
        payload["values"] = [v * 2 for v in payload["values"]]
        payload_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return "payload updated with run_tag and doubled values"

    def step06_add_negative_test(root: Path) -> str:
        test_path = root / "tests" / "test_calc.py"
        with test_path.open("a", encoding="utf-8") as f:
            f.write("\n\ndef test_add_negative():\n    assert add(-2, -4) == -6\n")
        return "appended negative test case"

    def step07_hash_source(root: Path) -> str:
        digest = _sha256(root / "src" / "calc.py")
        return f"calc.py_sha256={digest[:16]}"

    def step08_verify_imports(root: Path) -> str:
        content = (root / "tests" / "test_calc.py").read_text(encoding="utf-8")
        ok = "from src.calc import add, scale" in content
        return f"import_check={ok}"

    def step09_materialize_manifest(root: Path) -> str:
        manifest = []
        for p in sorted(root.rglob("*")):
            if p.is_file():
                manifest.append(str(p.relative_to(root)))
        (root / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return f"manifest_files={len(manifest)}"

    def step10_remove_todo_line(root: Path) -> str:
        notes = (root / "docs" / "notes.md").read_text(encoding="utf-8").splitlines()
        filtered = [line for line in notes if "boundary" not in line]
        (root / "docs" / "notes.md").write_text("\n".join(filtered) + "\n", encoding="utf-8")
        return "removed one TODO line from notes.md"

    def step11_recount_todos(root: Path) -> str:
        text = (root / "docs" / "notes.md").read_text(encoding="utf-8")
        return f"todo_count_after_edit={text.count('TODO')}"

    def step12_cleanup_artifacts(root: Path) -> str:
        manifest = root / "data" / "manifest.json"
        if manifest.exists():
            manifest.unlink()
        return "deleted transient manifest.json"

    return [
        ("create_layout", step01_create_layout),
        ("seed_files", step02_seed_files),
        ("count_lines", step03_count_lines),
        ("find_todos", step04_find_todos),
        ("update_payload", step05_update_payload),
        ("add_negative_test", step06_add_negative_test),
        ("hash_source", step07_hash_source),
        ("verify_imports", step08_verify_imports),
        ("materialize_manifest", step09_materialize_manifest),
        ("remove_todo_line", step10_remove_todo_line),
        ("recount_todos", step11_recount_todos),
        ("cleanup_artifacts", step12_cleanup_artifacts),
    ]


def _collect_run_metrics(codexlog: Path, run_id: str, begin: datetime, end: datetime) -> dict[str, Any]:
    total = 0
    by_phase: dict[str, int] = {}
    for line in codexlog.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = rec.get("ts")
        if not isinstance(ts, str):
            continue
        try:
            ts_parsed = datetime.fromisoformat(ts)
        except ValueError:
            continue
        if ts_parsed < begin or ts_parsed > end:
            continue
        details = rec.get("details", {})
        if not isinstance(details, dict):
            continue
        if details.get("run_id") != run_id:
            continue
        total += 1
        phase = str(details.get("phase", "unknown"))
        by_phase[phase] = by_phase.get(phase, 0) + 1

    duration = max((end - begin).total_seconds(), 1.0)
    return {
        "num_logs": total,
        "duration_seconds": round(duration, 2),
        "logs_per_ten_sec": round(total / (duration / 10.0), 2),
        "logs_by_phase": by_phase,
    }


def run_harness(workspace: Path, codexlog: Path, prompt_log: Path, variant: str, sleep_s: float) -> dict[str, Any]:
    run_id = f"ab-{variant}-{uuid.uuid4().hex[:10]}"
    begin = _utc_now()

    codexlog_snapshot = _read_snapshot(codexlog)
    prompt_snapshot = _read_snapshot(prompt_log)
    fixture_root = Path(tempfile.mkdtemp(prefix=f"codex-ab-{variant}-"))

    report: dict[str, Any] = {
        "run_id": run_id,
        "variant": variant,
        "begin_time": begin.isoformat(),
        "directive": "Exclude tasks and decisions from previous test runs from all step calculations.",
        "steps": [],
        "status": "running",
    }

    try:
        _emit_log(
            codexlog,
            run_id,
            "start",
            "A/B harness run started",
            {
                "intent": "Start deterministic granular workload",
                "action": "Initialize run markers and fixture",
                "checks": "Snapshots captured for codexlog and prompt_log",
                "reasoning": "Need reproducible and unbiased A/B comparisons",
                "confidence": "95%",
            },
            f"fixture={fixture_root}",
        )

        steps = _workload_steps()
        for idx, (name, fn) in enumerate(steps, start=1):
            step_phase = f"step_{idx:02d}_{name}"
            _emit_log(
                codexlog,
                run_id,
                step_phase,
                f"Step {idx} started",
                {
                    "intent": f"Execute workload step {idx}",
                    "action": f"Invoke {name}",
                    "checks": "Fixture available and writable",
                    "reasoning": "Granular state transitions provide better A/B observability",
                    "confidence": "92%",
                },
            )

            output = fn(fixture_root)
            report["steps"].append({"index": idx, "name": name, "output": output})

            _emit_log(
                codexlog,
                run_id,
                step_phase,
                f"Step {idx} completed",
                {
                    "intent": f"Record output for step {idx}",
                    "action": f"Store result of {name}",
                    "checks": "Output captured and non-empty",
                    "reasoning": "Step-level telemetry supports per-change comparisons",
                    "confidence": "93%",
                },
                output,
            )

            if sleep_s > 0:
                time.sleep(sleep_s)

        end = _utc_now()
        metrics = _collect_run_metrics(codexlog, run_id, begin, end)
        report.update(
            {
                "end_time": end.isoformat(),
                "metrics": metrics,
                "status": "completed",
            }
        )

        _emit_log(
            codexlog,
            run_id,
            "end",
            "A/B harness run completed",
            {
                "intent": "Finalize workload run",
                "action": "Compute run-scoped metrics",
                "checks": "Filtered events only by run_id and time window",
                "reasoning": "Explicit run scoping prevents prior-run bias in step counts",
                "confidence": "94%",
            },
            json.dumps(metrics),
        )

        return report
    finally:
        shutil.rmtree(fixture_root, ignore_errors=True)
        _restore_snapshot(codexlog_snapshot)
        _restore_snapshot(prompt_snapshot)
        report["post_state_restored"] = True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic granular A/B logging harness.")
    parser.add_argument("--variant", default="A", help="Variant label for A/B comparisons (e.g., A or B).")
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="Workspace root for pre-state capture.")
    parser.add_argument("--codexlog", default=str(DEFAULT_CODEXLOG), help="Path to .codexlog JSONL file.")
    parser.add_argument("--prompt-log", default=str(DEFAULT_PROMPT_LOG), help="Path to prompt_log.csv.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Optional delay between steps (seconds).")
    parser.add_argument(
        "--report-file",
        default="",
        help="Optional report output path. If omitted, report is printed to stdout only.",
    )
    args = parser.parse_args()

    report = run_harness(
        workspace=Path(args.workspace),
        codexlog=Path(args.codexlog),
        prompt_log=Path(args.prompt_log),
        variant=args.variant,
        sleep_s=max(0.0, args.sleep),
    )

    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report_file:
        report_path = Path(args.report_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
