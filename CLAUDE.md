# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal Claude Code skills marketplace. It contains custom skills that extend Claude's capabilities for specific workflows. Each skill is a self-contained directory under `skills/` with a `SKILL.md` file that provides instructions for Claude to follow.

## Repository Structure

```
my-claude-skills/
├── .claude-plugin/
│   └── marketplace.json    # Marketplace configuration with skill metadata
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md        # Skill definition (required)
│       ├── scripts/        # Optional: executable helpers
│       ├── references/     # Optional: detailed documentation
│       └── assets/         # Optional: templates, files
├── CONTRIBUTING.md         # Comprehensive skill development guide
└── README.md              # User-facing documentation
```

## Adding or Updating Skills

When adding a new skill or updating an existing one:

1. **Create/update the skill directory** under `skills/<skill-name>/`
2. **Write SKILL.md** with YAML frontmatter and instructions
3. **Update `.claude-plugin/marketplace.json`**:
   - Add new plugin entry with `name`, `version`, `description`, `source`, and `skills` fields
   - Increment `version` following semantic versioning when updating existing skills
4. **Update this CLAUDE.md file** to reflect any architectural changes or new patterns

## Skill Development Guidelines

### SKILL.md Structure

Every skill requires a `SKILL.md` with:

- **Frontmatter**: YAML metadata between `---` markers
  - `name`: Skill identifier (becomes `/skill-name` command)
  - `description`: When Claude should use this skill (critical for auto-invocation)
  - Optional: `disable-model-invocation`, `user-invokable`, `argument-hint`, `compatibility`, `license`, `metadata`
- **Body**: Instructions Claude follows when skill is invoked
  - Use imperative form ("Create" not "Creates")
  - Keep under 500 lines (move details to `references/`)
  - Include concrete examples
  - Focus on procedural knowledge

### Version Management

Each skill in `marketplace.json` has its own `version` field. Increment the version when updating a skill.

### Testing Skills Locally

```bash
# Add marketplace locally
/plugin marketplace add /path/to/my-claude-skills

# Install a skill
/plugin install <skill-name>@my-claude-skills

# Update after changes
/plugin marketplace update my-claude-skills
/plugin install <skill-name>@my-claude-skills --force
```

## Key Files

- **CONTRIBUTING.md**: Complete reference for skill development (frontmatter fields, string substitutions, dynamic context injection, subagents, etc.)
- **.claude-plugin/marketplace.json**: Single source of truth for all skills and their versions
- **README.md**: User-facing installation and usage instructions

## Important Notes

- Skills are for AI agents, not humans - write instructions for Claude, not documentation for users
- The `description` field in frontmatter is critical - it determines when Claude auto-loads the skill
- Use `disable-model-invocation: true` for skills with side effects (deploy, commit) that users should trigger manually
- Keep SKILL.md focused - move detailed references to separate files in `references/`
- Always validate JSON syntax after editing marketplace.json: `python3 -m json.tool .claude-plugin/marketplace.json`
