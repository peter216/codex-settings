# Scripts: A/B Logging Harness and Report Comparison

This directory contains scripts for running reproducible A/B checks on logging behavior and comparing results.

## Scripts

- `logging_ab_harness.py`
  - Runs a deterministic multi-step workload.
  - Emits structured TRACE logs with a per-run `run_id`.
  - Produces run metrics (`num_logs`, `logs_per_ten_sec`, per-phase counts).
  - Restores `.codexlog` and `prompt_log.csv` to their pre-run content, so each run starts clean.

- `compare_ab_reports.py`
  - Compares two harness report JSON files (A vs B).
  - Prints a summary delta and per-phase differences.
  - Supports both human-readable text and JSON output.

- `finalize_prompt.py` (related utility)
  - Appends one prompt-level telemetry row to `tmp/prompt_log.csv`.
  - Writes a completion trace event to `.codexlog`.

## Quick Start

Run variant A and write a report:

```bash
python /home/peter216/git/ai/codex-settings/scripts/logging_ab_harness.py \
  --variant A \
  --sleep 0.05 \
  --report-file /tmp/codex-ab-report-A.json
```

Run variant B and write a report:

```bash
python /home/peter216/git/ai/codex-settings/scripts/logging_ab_harness.py \
  --variant B \
  --sleep 0.05 \
  --report-file /tmp/codex-ab-report-B.json
```

Compare A vs B (text):

```bash
python /home/peter216/git/ai/codex-settings/scripts/compare_ab_reports.py \
  --a /tmp/codex-ab-report-A.json \
  --b /tmp/codex-ab-report-B.json \
  --format text
```

Compare A vs B (JSON):

```bash
python /home/peter216/git/ai/codex-settings/scripts/compare_ab_reports.py \
  --a /tmp/codex-ab-report-A.json \
  --b /tmp/codex-ab-report-B.json \
  --format json
```

## Idempotency and Isolation

`logging_ab_harness.py` is designed to be repeatable:

- Uses a temporary fixture directory per run.
- Tags generated logs with a unique `run_id`.
- Computes metrics only from the current run scope.
- Restores `.codexlog` and `prompt_log.csv` to their original content after the run.

This allows reliable A/B checks without contamination from previous runs.

## Key Options

### `logging_ab_harness.py`

- `--variant`: label run as `A`, `B`, or any custom identifier.
- `--sleep`: delay between steps in seconds (default `0.2`).
- `--report-file`: optional path to save the JSON report.
- `--codexlog`: override `.codexlog` location.
- `--prompt-log`: override `prompt_log.csv` location.

### `compare_ab_reports.py`

- `--a`: report file path for variant A.
- `--b`: report file path for variant B.
- `--format`: `text` or `json`.

## Example A/B Trial Loop

```bash
python /home/peter216/git/ai/codex-settings/scripts/logging_ab_harness.py --variant A --sleep 0.10 --report-file /tmp/ab-A.json
python /home/peter216/git/ai/codex-settings/scripts/logging_ab_harness.py --variant B --sleep 0.10 --report-file /tmp/ab-B.json
python /home/peter216/git/ai/codex-settings/scripts/compare_ab_reports.py --a /tmp/ab-A.json --b /tmp/ab-B.json --format text
```

## Optional: Prompt Finalization Utility

If you also want prompt-level trend logging:

```bash
date -u +%Y-%m-%dT%H:%M:%S%:z > /tmp/last_prompt_start.txt
python /home/peter216/git/ai/codex-settings/scripts/finalize_prompt.py \
  --begin-time "$(cat /tmp/last_prompt_start.txt)"
```

This writes one row to `/home/peter216/git/ai/codex-settings/tmp/prompt_log.csv`.
