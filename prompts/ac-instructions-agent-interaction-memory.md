# ac-instructions-agent-interaction-memory

Description: Memory for AI agent interaction patterns, feedback expectations, and communication best practices
Applies to: **/*
Source: awesome-copilot/instructions/agent-interaction-memory.instructions.md

Codex note: Converted from GitHub Copilot file-scoped instructions. Invoke manually or copy relevant guidance into your project's AGENTS.md for automatic application.

# Agent Interaction Memory

Patterns for effective AI assistant communication and user experience.

## Provide Progress Feedback During Long Operations

When running long processes (API calls, searches, file operations taking >30 seconds):

- Emit progress updates every ~60 seconds
- Include estimated percentage complete when possible
- State current operation phase clearly
- Use terminal output or status messages to confirm activity

Example feedback pattern:
```
[1m elapsed] Reading file 5 of 20 (25%)...
[2m elapsed] Processing search results (60%)...
[3m elapsed] Finalizing output (90%)...
```

This prevents user uncertainty about whether the agent is stuck or still working.
