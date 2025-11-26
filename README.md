# OpenAI Codex CLI Settings and Custom Prompts

A curated collection of configurations and custom prompts for [OpenAI Codex CLI](https://github.com/openai/codex), designed to enhance your development workflow with various model providers and reusable prompt templates.

> For Claude Code settings, agents and custom commands, please refer [feiskyer/claude-code-settings](https://github.com/feiskyer/claude-code-settings).

## Overview

This repository provides:

- **Flexible Configuration**: Support for multiple model providers (LiteLLM/Copilot proxy, ChatGPT subscription, Azure OpenAI, OpenRouter, ModelScope, Kimi)
- **Custom Prompts**: Reusable prompt templates for common development tasks
- **Best Practices**: Pre-configured settings optimized for development workflows
- **Easy Setup**: Simple installation and configuration process

## Quick Start

### Installation

```bash
# Backup existing Codex configuration (if any)
mv ~/.codex ~/.codex.bak

# Clone this repository to ~/.codex
git clone https://github.com/feiskyer/codex-settings.git ~/.codex

# Or symlink if you prefer to keep it elsewhere
ln -s /path/to/codex-settings ~/.codex
```

### Basic Configuration

The default `config.toml` uses LiteLLM as a gateway. To use it:

1. Install LiteLLM and Codex CLI:

   ```bash
   pip install -U 'litellm[proxy]'
   npm install -g @openai/codex
   ```

1. Create a LiteLLM config file (full example [litellm_config.yaml](litellm_config.yaml)):

   ```yaml
   general_settings:
     master_key: sk-dummy
   litellm_settings:
     drop_params: true
   model_list:
   - model_name: gpt-5
     litellm_params:
       model: github_copilot/gpt-5
       extra_headers:
         editor-version: "vscode/1.104.3"
         editor-plugin-version: "copilot-chat/0.26.7"
         Copilot-Integration-Id: "vscode-chat"
         user-agent: "GitHubCopilotChat/0.26.7"
         x-github-api-version: "2025-04-01"
   ```

1. Start LiteLLM proxy:

   ```bash
   litellm --config ~/.codex/litellm_config.yaml
   # Runs on http://localhost:4000 by default
   ```

1. Run Codex:

   ```bash
   codex
   ```

## Configuration Files

### Main Configuration

- [config.toml](config.toml): Default configuration using LiteLLM gateway
  - Model: `gpt-5` via `model_provider = "github"` (Copilot proxy on http://localhost:4000)
  - Approval policy: `on-request`; reasoning summary: `detailed`; reasoning effort: `high`; raw agent reasoning visible
  - MCP servers: `claude` (local), `exa` (hosted), `chrome` (DevTools over `npx`)

### Alternative Configurations

Located in `configs/` directory:

- [OpenAI ChatGPT](configs/chatgpt.toml): Use ChatGPT subscription provider
- [Azure OpenAI](configs/azure.toml): Use Azure OpenAI service provider
- [Github Copilot](configs/github-copilot.toml): Use Github Copilot via LiteLLM proxy
- [OpenRouter](configs/openrouter.toml): Use OpenRouter provider
- [Model Scope](configs/modelscope.toml): Use ModelScope provider
- [Kimi](configs/kimi.toml): Use Moonshot Kimi provider

To use an alternative config:

```bash
# Take ChatGPT for example
cp ~/.codex/configs/chatgpt.toml config.toml
codex
```

## Custom Prompts

Custom prompts are stored in the `prompts/` directory. Access them via the `/prompts:` slash menu in Codex.

### Github Spec Kit Workflow

**Github Spec Kit** - Unified interface for Spec-Driven Development.

To use it, run the following command to initialize your project:

```sh
uvx --from git+https://github.com/github/spec-kit.git specify init .
```

Alternatively, you can also copy [.specify](.specify) to your project root directory.

Available commands:

- `/prompts:constitution` - Create or update the project constitution from interactive or provided principle inputs.
- `/prompts:specify` - Create or update the feature specification from a natural language feature description.
- `/prompts:clarify` - Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions.
- `/prompts:plan` - Execute the implementation planning workflow using the plan template to generate design artifacts.
- `/prompts:tasks` - Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
- `/prompts:analyze` - Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md.
- `/prompts:implement` - Execute the implementation plan by processing and executing all tasks defined in tasks.md.

### Kiro Spec Workflow

**Kiro Workflow** - Complete feature development from spec to execution. The Kiro commands provide a structured workflow for feature development:

1. `/prompts:kiro-spec-creator [feature]` - Create comprehensive specs with requirements and EARS acceptance criteria in `.kiro/specs/`
2. `/prompts:kiro-feature-designer [feature]` - Create design documents with research and architecture based on requirements
3. `/prompts:kiro-task-planner [feature]` - Generate actionable, test-driven implementation task lists from designs
4. `/prompts:kiro-task-executor [feature] [task]` - Execute specific implementation tasks from feature specifications
5. `/prompts:kiro-assistant [question]` - Quick development assistance with a relaxed, developer-focused approach

### Other Prompts

- `/prompts:deep-reflector` - Analyze development sessions to extract learnings, patterns, and improvements for future interactions.
- `/prompts:insight-documenter [breakthrough]` - Capture and document significant technical breakthroughs into reusable knowledge assets.
- `/prompts:instruction-reflector` - Analyze and improve Codex instructions in AGENTS.md based on conversation history.
- `/prompts:github-issue-fixer [issue-number]` - Systematically analyze, plan, and implement fixes for GitHub issues with PR creation.
- `/prompts:github-pr-reviewer [pr-number]` - Perform thorough GitHub pull request code analysis and review.
- `/prompts:ui-engineer [requirements]` - Create production-ready frontend solutions with modern UI/UX standards.
- `/prompts:prompt-creator [requirements]` - Create Codex custom prompts with proper structure and best practices.

### Creating Custom Prompts

1. Create a new `.md` file in `~/.codex/prompts/`
2. Use argument placeholders:
   - `$1` to `$9`: Positional arguments
   - `$ARGUMENTS`: All arguments joined by spaces
   - `$$`: Literal dollar sign
3. Restart Codex to load new prompts

## Configuration Options

### Approval Policies

- `untrusted`: Prompt for untrusted commands (recommended)
- `on-failure`: Only prompt when sandbox commands fail
- `on-request`: Model decides when to ask
- `never`: Auto-approve all commands (use with caution)

### Sandbox Modes

- `read-only`: Can read files, no writes or network
- `workspace-write`: Can write to workspace, network configurable
- `danger-full-access`: Full system access (use in containers only)

### Reasoning Settings

For reasoning-capable models (o3, gpt-5):

- **Effort**: `minimal`, `low`, `medium`, `high`
- **Summary**: `auto`, `concise`, `detailed`, `none`

### Shell Environment

Control which environment variables are passed to subprocesses:

```toml
[shell_environment_policy]
inherit = "all"  # all, core, none
exclude = ["AWS_*", "AZURE_*"]  # Exclude patterns
set = { CI = "1" }  # Force-set values
```

## Advanced Features

### Profiles

Define multiple configuration profiles:

```toml
[profiles.fast]
model = "gpt-4o-mini"
approval_policy = "never"
model_reasoning_effort = "low"

[profiles.reasoning]
model = "o3"
approval_policy = "on-failure"
model_reasoning_effort = "high"
```

Use with: `codex --profile reasoning`

### MCP Servers

Extend Codex with Model Context Protocol servers:

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@latest"]

[mcp_servers.claude]
command = "claude"
args = ["mcp", "serve"]
```

## Project Documentation

Codex automatically reads `AGENTS.md` files in your project to understand context. Please always create one in your project root with `/init` command on your first codex run.

## References

- [Codex CLI Official Docs](https://developers.openai.com/codex/cli/)
- [Codex GitHub Repository](https://github.com/openai/codex)
- [LiteLLM Documentation](https://docs.litellm.ai/)

## Contributing

Contributions welcome! Feel free to:

- Add new custom prompts
- Share alternative configurations
- Improve documentation
- Report issues and suggest features

## LICENSE

This project is released under MIT License - See [LICENSE](LICENSE) for details.
