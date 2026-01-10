# AGENTS.md

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
