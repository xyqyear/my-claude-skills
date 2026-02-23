# My Claude Skills

Personal collection of Claude Code skills for enhanced development workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add <your-github-username>/my-claude-skills
```

Or if testing locally:

```bash
/plugin marketplace add /path/to/my-claude-skills
```

## Available Skills

### commit-generator

Intelligent git commit message generator that analyzes staged changes and creates conventional commit messages.

**Installation:**
```bash
/plugin install commit-generator@my-claude-skills
```

**Usage:**
Simply ask Claude to create a commit or generate a commit message:
- "Create a commit for these changes"
- "Generate a commit message"
- "Help me write a good commit message"

The skill will analyze your staged changes, review your commit history to match your project's style, and generate a well-formatted conventional commit message.

## Adding Your Own Skills

1. Create a new directory under `skills/`:
   ```bash
   mkdir skills/my-new-skill
   ```

2. Create a `SKILL.md` file with frontmatter:
   ```markdown
   ---
   name: my-new-skill
   description: Description of when to use this skill
   ---

   # Skill instructions here
   ```

3. Update `.claude-plugin/marketplace.json` to include your new skill

4. Commit and push to your repository

## Structure

```
my-claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace configuration
├── skills/
│   └── commit-generator/
│       └── SKILL.md              # Skill definition
└── README.md
```

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [Creating Skills Guide](https://code.claude.com/docs/en/plugins)
- [Marketplace Distribution](https://code.claude.com/docs/en/distribute-plugins)
