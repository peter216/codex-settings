# ac-prompt-dataverse-python-quickstart

Description: Generate Python SDK setup + CRUD + bulk + paging snippets using official patterns.
Source: awesome-copilot/prompts/dataverse-python-quickstart.prompt.md

Codex note: Converted from a GitHub Copilot prompt. Invoke with /prompts:ac-prompt-dataverse-python-quickstart.

You are assisting with Microsoft Dataverse SDK for Python (preview).
Generate concise Python snippets that:
- Install the SDK (pip install PowerPlatform-Dataverse-Client)
- Create a DataverseClient with InteractiveBrowserCredential
- Show CRUD single-record operations
- Show bulk create and bulk update (broadcast + 1:1)
- Show retrieve-multiple with paging (top, page_size)
- Optionally demonstrate file upload to a File column
Keep code aligned with official examples and avoid unannounced preview features.
