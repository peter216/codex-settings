---
name: azure-role-selector
description: When user is asking for guidance for which role to assign to an identity given desired permissions, this agent helps them understand the role that will meet the requirements with least privilege access and how to apply that role.
---
# Azure Role Selector

Use this skill to find the least-privilege Azure role for a set of permissions and provide the commands and Bicep snippet to assign it.

## Preferred MCP Tools

If the Azure MCP tools are available, prefer them in this order:

1. `Azure MCP/documentation` to identify the minimal built-in role that matches the requested permissions.
2. `Azure MCP/extension_cli_generate` to generate a custom role definition if no built-in role fits.
3. `Azure MCP/extension_cli_generate` again to produce CLI commands for role assignment.
4. `Azure MCP/bicepschema` and `Azure MCP/get_bestpractices` to craft a Bicep role assignment snippet.

## Execution Notes

- Favor built-in roles unless the requirements cannot be met.
- When creating a custom role, include only the requested permissions.
- Provide both CLI and Bicep outputs when possible.

## Bundled Assets

- `LICENSE.txt` documents the original skill license.
