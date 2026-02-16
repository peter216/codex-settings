# AGENTS.md

## Specific Instructions

### Logging and Debugging

Activation & Scope

Trigger keyword: log-on

When the user includes the keyword log-on, enter Logging Mode for the remainder of this subthread unless explicitly turned off.

Logging Mode applies only to this subthread and should not be assumed elsewhere.

Logging Mode — Core Behavior

When Logging Mode is active, you MUST:

Log carefully during all actions

Briefly describe what you are doing and why, before or alongside the result.

Prefer concise, structured logs over prose.

Make reasoning visible but bounded

Summarize reasoning steps at a high level.

Do not include hidden chain-of-thought; instead provide:

assumptions

checks performed

confidence level where relevant

Acknowledge uncertainty explicitly

If information is incomplete, say so.

If you are making an inference, label it clearly.

Preserve continuity

Treat prior logs in this subthread as state.

Do not silently drop constraints or earlier decisions.

Logging Format (Lightweight, Sticky)

Use this format whenever practical:

[LOG]
Intent:
Action:
Checks:
Result:
Confidence: X%

The log may be shortened for trivial steps, but must still be present.

If a step is skipped, say why.

Priority Handling

Logging Mode takes precedence over:

verbosity minimization

stylistic brevity defaults

If a higher-priority system constraint conflicts, log the conflict instead of silently complying.

Deactivation

Logging Mode remains active until the user says:

log-off

or explicitly requests no logging

Self-Check (Internal Reminder)

Before responding while Logging Mode is active, ask:

"Have I logged my intent and actions clearly for this step?"

If not, revise before responding.

### .codexlog and TRACE Log Level

- This section pertains to the log file `.codexlog` and is active whenever Logging Mode is active, unless the level is explicitly changed by specifying `log-level <LEVEL>`, which will take effect for the rest of the subthread unless changed again.
- Log the initial user request and every subsequent user interaction. This includes prompts back to the user and the user's response.
- Record every step (including failures and retries) in `/home/peter216/git/www/.codexlog` at `TRACE` level (JSON lines preferred) by default; include `ts`, `level`, `message`, `details`, and `output` fields. These fields should be presented in the same way that they are in the chat output with log-on in effect.
- Include steps even if they are not included in the user-facing chat for brevity. If this results in more than 10 logs a minute, stop and request permission to adjust so we can tune the logging frequency.
- The `details` field should capture the `intent`, `action`, `checks`, `reasoning`, and `confidence` for each step, while `output` should capture the result or response.
  - The format of the details field should be the same as the structured log format described in the Logging and Debugging section, except as a JSON object rather than free-form text.

```json
{
  "intent": "Briefly describe the intent for this step",
  "action": "Describe the action taken",
  "checks": "List any checks performed",
  "reasoning": "Summarize the reasoning steps",
  "confidence": "Provide a confidence level if relevant"
}
```

- If a step is skipped, log the omitted items and reason for skipping in the `details` field.
- If confidence level is 65% or below, include the alternative paths considered and the rationale for the chosen path in the `details` field.
- Ensure `.codexlog` entries are at least as detailed as the chat, include captured outputs, and truncate any field to 200 characters when necessary.
- Continue writing to `.codexlog` as part of normal logging unless you are explicitly instructed to stop logging there.
- Structure each entry so automated parsing can easily extract the fields (e.g., newline-delimited JSON objects).
- This TRACE-level logging instruction is permanent until the instructions in this file (or another file in `/home/peter216/git/ai/codex-settings`) are updated to change it.

### Debug count trend file prompt_log.csv

- Maintain `/home/peter216/git/ai/codex-settings/tmp/prompt_log.csv` with columns `PROMPT_ID,BEGIN_TIME,END_TIME,NUM_LOGS,LOGS_PER_TEN_SEC`.
- Ensure the directory `/home/peter216/git/ai/codex-settings/tmp` exists and the CSV file has a header row before appending.
- Use `/home/peter216/git/ai/codex-settings/scripts/finalize_prompt.py` as the mandatory completion path to append prompt telemetry and emit the final `.codexlog` completion event.
- For benchmark or A/B runs, calculate step counts and log-rate metrics only from the current run scope (explicit run ID and/or begin-end window), deliberately excluding tasks/decisions from previous runs so results are unbiased.
- Recommended pattern:
  - At prompt start: write start time to `/tmp/last_prompt_start.txt`.
  - Before returning control: run `python /home/peter216/git/ai/codex-settings/scripts/finalize_prompt.py --begin-time \"$(cat /tmp/last_prompt_start.txt)\"`.
- Each time you finish fulfilling a prompt (i.e., before handing control back), append a row with:
 1. A unique `PROMPT_ID` (e.g., `prompt-<timestamp>`),
 2. `BEGIN_TIME` and `END_TIME` in UTC ISO format,
 3. `NUM_LOGS`: how many `.codexlog` entries you created during that prompt (parsed from `ts` >= `BEGIN_TIME`),
 4. `LOGS_PER_TEN_SEC`: `NUM_LOGS / max(1, duration_seconds / 10)` to represent logging density.
- This CSV logging is required for every prompt and persists until someone edits this section or another relevant file in `/home/peter216/git/ai/codex-settings`.

### Asking Questions

- When you need more information to complete a task, ask the user a disambiguating question.
- Challenge the user's assumptions if they seem incorrect or incomplete, but do so respectfully and with the goal of clarifying the task.
- If the user's request is vague, ask for specific details (e.g., "When you say 'optimize the code', do you mean improving runtime performance, reducing memory usage, enhancing readability, or something else?").
- If there are multiple ways to interpret the request, outline the options and ask the user to choose (e.g., "I see two possible approaches to this problem: A and B. Approach A would involve X, Y, Z, while Approach B would involve M, N, O. Which one would you prefer?").
- Call out any hidden risks or implications of the user's request that they may not have considered (e.g., "Just to clarify, if I proceed with this action, it will also affect X and Y. Is that okay?").
- If you are unsure about the user's intent, ask for confirmation before proceeding (e.g., "I want to make sure I understand your request correctly. You want me to do X, is that right?").
- Preference is that you understand the goal as well as the task, so that fruitful dialogue can occur about how to best achieve the user's underlying goal, rather than just executing a task that may be suboptimal or even counterproductive.

### Bash Environment Secrets

- This applies any time Codex operates as an agent in a Bash environment, not only for Python tasks.
- Before loading secret-backed environment variables, run: `source /home/peter216/.function/gopass.function` in the same shell session.
- Load required variables with `gopassget` at runtime (example: `export FDC_API_KEY="$(gopassget FDC_API_KEY)"`).
- Example for GitHub CLI auth in agent shells: `source /home/peter216/.function/gopass.function; export GITHUB_TOKEN="$(gh auth token --hostname github.com)"`.
- To see what secrets are available in gopass, run: `gopass list --flat
- Do not load secrets beginning with a . unless specifically directed, as these are typically meant to be hidden and not used in agent contexts.
- Never hardcode or print secret values in logs/output; load only what is required for the current command.

### Python

#### Package Management

- Use `/home/peter216/.local/bin/uv` only for managing virtual environments.
- `/home/peter216/bin/uvp` wraps `uv` with the current `PROJECT_NAME` (from the nearest `.uv/pyproject.toml`) and the parent directory of the active virtualenv, so run it inside an activated `uv` environment when you need to add/remove/list packages or run project-scoped commands.
- `/home/peter216/bin/uv_setup.sh` bootstraps a new `uv` project: it initializes the project folder, creates the `.uv` symlink, spins up a `.venv`, syncs any `pyproject.toml`/`requirements*.txt` metadata, and adds `ipython` as a dev dependency.
- `auto_venv.sh` walks up from the current directory to find the closest `.uv/.venv`, activates it, exports `PROJECT_NAME`, and loads any `.env`/`.loadenv` variables while keeping track of the ones it manages.
- `~/.bashrc` ensures `~/.local/bin`, `~/.uv/.venv/bin`, and other user toolchains are early on your PATH, sources helper scripts (including `auto_venv.sh`/`uvp`), and arranges `PROMPT_COMMAND` to rerun `auto_venv` plus path deduping every prompt unless `NOAUTOENV=1`.

## Repository Structure

```plaintext
.
├── configs
├── policy
├── prompts
└── skills
    ├── autonomous-skill
    │   ├── scripts
    │   └── templates
    ├── claude-skill
    │   └── references
    ├── kiro-skill
    │   └── helpers
    ├── nanobanana-skill
    ├── spec-kit-skill
    │   ├── helpers
    │   └── scripts
    └── youtube-transcribe-skill
```

## Development Workflow

### Working with Agents, Prompts, Instructions, and Skills

All agent files (`*.agent.md`), prompt files (`*.prompt.md`), and instruction files (`*.instructions.md`) must include proper markdown front matter. Agent Skills are folders containing a `SKILL.md` file with frontmatter and optional bundled assets:

#### Agent Files (*.agent.md)

- Must have `description` field (wrapped in single quotes)
- File names should be lower case with words separated by hyphens
- Recommended to include `tools` field
- Strongly recommended to specify `model` field

#### Prompt Files (*.prompt.md)

- Must have `agent` field (value should be `'agent'` wrapped in single quotes)
- Must have `description` field (wrapped in single quotes, not empty)
- File names should be lower case with words separated by hyphens
- Recommended to specify `tools` if applicable
- Strongly recommended to specify `model` field

#### Instruction Files (*.instructions.md)

- Must have `description` field (wrapped in single quotes, not empty)
- Must have `applyTo` field specifying file patterns (e.g., `'**.js, **.ts'`)
- File names should be lower case with words separated by hyphens

#### Agent Skills (skills/*/SKILL.md)

- Each skill is a folder containing a `SKILL.md` file
- SKILL.md must have `name` field (lowercase with hyphens, matching folder name, max 64 characters)
- SKILL.md must have `description` field (wrapped in single quotes, 10-1024 characters)
- Folder names should be lower case with words separated by hyphens
- Skills can include bundled assets (scripts, templates, data files)
- Bundled assets should be referenced in the SKILL.md instructions
- Asset files should be reasonably sized (under 5MB per file)
- Skills follow the [Agent Skills specification](https://agentskills.io/specification)

### Adding New Resources

When adding a new agent, prompt, instruction, or skill:

**For Agents, Prompts, and Instructions:**

1. Create the file with proper front matter
2. Add the file to the appropriate directory
3. Update the README.md by running: `npm run build`
4. Verify the resource appears in the generated README

**For Skills:**

1. Run `$skill-creator` to scaffold a new skill folder

Before committing:

- Ensure all markdown front matter is correctly formatted
- Verify file names follow the lower-case-with-hyphens convention
- Run `npm run build` to update the README
- **Always run `bash scripts/fix-line-endings.sh`** to normalize line endings (CRLF → LF)
- Check that your new resource appears correctly in the README

## Code Style Guidelines

### Markdown Files

- Use proper front matter with required fields
- Keep descriptions concise and informative
- Wrap description field values in single quotes
- Use lower-case file names with hyphens as separators

### JavaScript/Node.js Scripts

- Located in `eng/` and `scripts/` directories
- Follow Node.js ES module conventions (`.mjs` extension)
- Use clear, descriptive function and variable names

## Pull Request Guidelines

When creating a pull request:

1. **README updates**: New files should automatically be added to the README when you run `npm run build`
2. **Front matter validation**: Ensure all markdown files have the required front matter fields
3. **File naming**: Verify all new files follow the lower-case-with-hyphens naming convention
4. **Build check**: Run `npm run build` before committing to verify README generation
5. **Line endings**: **Always run `bash scripts/fix-line-endings.sh`** to normalize line endings to LF (Unix-style)
6. **Description**: Provide a clear description of what your agent/prompt/instruction does
7. **Testing**: If adding a collection, run `npm run collection:validate` to ensure validity

### Pre-commit Checklist

Before submitting your PR, ensure you have:

- [ ] Run `bash scripts/fix-line-endings.sh` to normalize line endings
- [ ] Verified that all new files have proper front matter
- [ ] Tested that your contribution works with GitHub Copilot
- [ ] Checked that file names follow the naming convention

### Code Review Checklist

For prompt files (*.prompt.md):

- [ ] Has markdown front matter
- [ ] Has `agent` field (value should be `'agent'` wrapped in single quotes)
- [ ] Has non-empty `description` field wrapped in single quotes
- [ ] File name is lower case with hyphens
- [ ] Includes `model` field (strongly recommended)

For instruction files (*.instructions.md):

- [ ] Has markdown front matter
- [ ] Has non-empty `description` field wrapped in single quotes
- [ ] Has `applyTo` field with file patterns
- [ ] File name is lower case with hyphens

For agent files (*.agent.md):

- [ ] Has markdown front matter
- [ ] Has non-empty `description` field wrapped in single quotes
- [ ] File name is lower case with hyphens
- [ ] Includes `model` field (strongly recommended)
- [ ] Considers using `tools` field

For skills (skills/*/):

- [ ] Folder contains a SKILL.md file
- [ ] SKILL.md has markdown front matter
- [ ] Has `name` field matching folder name (lowercase with hyphens, max 64 characters)
- [ ] Has non-empty `description` field wrapped in single quotes (10-1024 characters)
- [ ] Folder name is lower case with hyphens
- [ ] Any bundled assets are referenced in SKILL.md
- [ ] Bundled assets are under 5MB per file

## License

MIT License - see [LICENSE](LICENSE) for details
