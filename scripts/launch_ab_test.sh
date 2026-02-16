#!/bin/bash

source /home/peter216/.function/logging.function

TIMESTAMP=$(date -Iseconds)
BRANCH_A="${BRANCH_A:-before_optimization}"
BRANCH_B="${BRANCH_B:-after_optimization}"
SLEEP_DURATION="${SLEEP_DURATION:-0.20}"
TESTNAME="${1:-$TIMESTAMP-$BRANCH_A-$BRANCH_B-$SLEEP_DURATION}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/ab_test_results/${TESTNAME}}"
CODEXLOG_PREFIX="codexlog-${TESTNAME}"
PROMPTLOG_PREFIX="promptlog-${TESTNAME}"

log_info "Starting A/B test with name: ${TESTNAME}"
log_action "Creating output directory: ${OUTPUT_DIR})"
mkdir -p "${OUTPUT_DIR}"
log_success "Created output directory: ${OUTPUT_DIR}"
log_action "Checking out before_optimization branch for AGENTS.md"
git checkout ${BRANCH_A} AGENTS.md
log_success "Checked out ${BRANCH_A} branch for AGENTS.md"
log_action "Running logging_ab_harness for before_optimization variant"
python /home/peter216/git/ai/codex-settings/scripts/logging_ab_harness.py \
  --variant A \
  --sleep ${SLEEP_DURATION} \
  --codexlog ${OUTPUT_DIR}/${CODEXLOG_PREFIX}-A.log \
  --prompt-log ${OUTPUT_DIR}/${PROMPTLOG_PREFIX}-A.log \
  --report-file ${OUTPUT_DIR}/${REPORTFILE_PREFIX}-A.json
log_success "Completed logging_ab_harness for variant A"
log_action "Checking out after_optimization branch for AGENTS.md"
git checkout ${BRANCH_B} AGENTS.md
log_success "Checked out ${BRANCH_B} branch for AGENTS.md"
log_action "Running logging_ab_harness for after_optimization variant"
python /home/peter216/git/ai/codex-settings/scripts/logging_ab_harness.py \
  --variant B \
  --sleep ${SLEEP_DURATION} \
  --codexlog ${OUTPUT_DIR}/${CODEXLOG_PREFIX}-B.log \
  --prompt-log ${OUTPUT_DIR}/${PROMPTLOG_PREFIX}-B.log \
  --report-file ${OUTPUT_DIR}/${REPORTFILE_PREFIX}-B.json
log_success "Completed logging_ab_harness for variant B"
log_action "Comparing A/B test results for ${TESTNAME}"
python /home/peter216/git/ai/codex-settings/scripts/compare_ab_reports.py --a ${OUTPUT_DIR}/${REPORTFILE_PREFIX}-A.json --b ${OUTPUT_DIR}/${REPORTFILE_PREFIX}-B.json --format text > ${OUTPUT_DIR}/ab-comparison-${TESTNAME}.txt
log_info "A/B test comparison results (text format): $(cat ${OUTPUT_DIR}/ab-comparison-${TESTNAME}.txt)"
python /home/peter216/git/ai/codex-settings/scripts/compare_ab_reports.py --a ${OUTPUT_DIR}/${REPORTFILE_PREFIX}-A.json --b ${OUTPUT_DIR}/${REPORTFILE_PREFIX}-B.json --format json > ${OUTPUT_DIR}/ab-comparison-${TESTNAME}.json
log_info "A/B test comparison results (JSON format): $(cat ${OUTPUT_DIR}/ab-comparison-${TESTNAME}.json)"
log_success "Completed A/B test with name: ${TESTNAME}"
