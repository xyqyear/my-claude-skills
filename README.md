# My Claude Skills

Personal collection of Claude Code skills for enhanced development workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add xyqyear/my-claude-skills
```

Or if testing locally:

```bash
/plugin marketplace add /path/to/my-claude-skills
```

## Available Skills

### cite

Academic citation finder — look up papers by title and get BibTeX entries via Semantic Scholar and DBLP.

**Installation:**

```bash
/plugin install cite@my-claude-skills
```

**Usage:**

- `/cite Attention Is All You Need`
- `/cite BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding`
- Provide multiple titles separated by semicolons or newlines

The skill queries Semantic Scholar first, then falls back to DBLP for any failures. It verifies returned papers match the intended query and retries with disambiguation (author, year) if needed.

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
│   └── <skill-name>/
│       └── SKILL.md              # Skill definition
└── README.md
```

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [Creating Skills Guide](https://code.claude.com/docs/en/plugins)
- [Marketplace Distribution](https://code.claude.com/docs/en/distribute-plugins)
