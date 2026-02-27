# Contributing to My Claude Skills

This guide explains how to add new skills to this marketplace.

## Quick Start

1. Create a new skill directory:

   ```bash
   mkdir skills/your-skill-name
   ```

2. Create `SKILL.md` with frontmatter:

   ```markdown
   ---
   name: your-skill-name
   description: Clear description of what this skill does and when to use it
   ---

   # Your Skill Name

   [Instructions for Claude to follow when using this skill]
   ```

3. Update `.claude-plugin/marketplace.json`:

   ```json
   {
     "plugins": [
       {
         "name": "your-skill-name",
         "version": "1.0.0",
         "description": "Brief description",
         "source": "./skills/your-skill-name",
         "strict": false,
         "skills": ["./skills/your-skill-name"]
       }
     ]
   }
   ```

4. Test locally:

   ```bash
   /plugin marketplace add /tmp/my-claude-skills
   /plugin install your-skill-name@my-claude-skills
   ```

5. Commit and push:
   ```bash
   git add .
   git commit -m "feat(skills): add your-skill-name"
   git push
   ```

## Skill Structure

### Basic Skill (SKILL.md only)

```
skills/your-skill/
└── SKILL.md
```

### Advanced Skill (with resources)

```
skills/your-skill/
├── SKILL.md
├── scripts/          # Executable code (Python, Bash, etc.)
│   └── helper.py
├── references/       # Documentation to load as needed
│   └── api-docs.md
└── assets/          # Files used in output (templates, images)
    └── template.html
```

## SKILL.md Format

### Frontmatter Fields

```yaml
---
name: skill-name # Optional: defaults to directory name
description: What this skill does and when to use it. Claude uses this to decide when to load the skill automatically.
argument-hint: [issue-number] # Optional: shown during autocomplete
disable-model-invocation: true # Optional: prevent Claude from auto-loading (manual /invoke only)
user-invocable: false # Optional: hide from / menu (Claude-only skills)
allowed-tools: Read, Grep, Glob # Optional: tools Claude can use without permission
model: haiku # Optional: model to use (sonnet, opus, haiku)
context: fork # Optional: run in isolated subagent
agent: Explore # Optional: subagent type when context=fork
---
```

### Body Guidelines

- Use imperative/infinitive form ("Create" not "Creates" or "Creating")
- Keep under 500 lines (split into references if longer)
- Include concrete examples
- Reference bundled resources clearly
- Focus on procedural knowledge Claude doesn't have

### String Substitutions

Skills support dynamic values:

- `$ARGUMENTS` - All arguments passed to the skill
- `$ARGUMENTS[0]` or `$0` - First argument
- `$ARGUMENTS[1]` or `$1` - Second argument
- `${CLAUDE_SESSION_ID}` - Current session ID

Example:

```markdown
Fix GitHub issue $0 in the $1 component.
```

### Dynamic Context Injection

Use `` !`command` `` to run shell commands before Claude sees the content:

```markdown
## Pull request context

- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`

Summarize this pull request...
```

The command output replaces the placeholder before Claude receives the prompt.

### Progressive Disclosure

Keep SKILL.md concise by moving detailed content to reference files:

```markdown
# Quick Start

Basic usage instructions here.

## Advanced Features

- **Feature A**: See [FEATURE_A.md](references/FEATURE_A.md)
- **Feature B**: See [FEATURE_B.md](references/FEATURE_B.md)
```

## Bundled Resources

### Scripts (`scripts/`)

Use for code that would be repeatedly rewritten:

```python
# scripts/process_data.py
#!/usr/bin/env python3
"""Helper script for data processing."""

def main():
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

Reference in SKILL.md:

````markdown
Run the processing script:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/process_data.py input.txt
```
````

````

### References (`references/`)

Use for documentation Claude should load as needed:

```markdown
# references/api-docs.md

## API Endpoints

### GET /users
Returns list of users...
````

Reference in SKILL.md:

```markdown
For complete API documentation, see [API Docs](references/api-docs.md).
```

### Assets (`assets/`)

Use for files that go into the output:

```
assets/
├── template.html
├── logo.png
└── boilerplate/
    ├── index.html
    └── style.css
```

Reference in SKILL.md:

````markdown
Copy the template:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/assets/template.html output.html
```
````

````

## Best Practices

### Description Writing

The `description` field is crucial for skill triggering. Include:

1. **What it does**: "Generates commit messages"
2. **When to use**: "Use when the user asks to create a commit"
3. **Key triggers**: "Triggers on: 'commit', 'commit message', 'generate commit'"

Example:
```yaml
description: Intelligent git commit message generator. Use when the user asks to create a commit, generate a commit message, or wants help writing a good commit message. Analyzes git diff output and repository commit history to generate conventional commit messages that follow the project's style and best practices.
````

### Skill Invocation Control

Choose who can invoke your skill:

| Frontmatter                      | You invoke | Claude invokes | Use case                          |
| -------------------------------- | ---------- | -------------- | --------------------------------- |
| (default)                        | ✓          | ✓              | General-purpose skills            |
| `disable-model-invocation: true` | ✓          | ✗              | Manual workflows (deploy, commit) |
| `user-invocable: false`          | ✗          | ✓              | Background knowledge only         |

**Reference content** (conventions, patterns, style guides) should use defaults so Claude applies them automatically.

**Task content** (deployments, commits, side effects) should set `disable-model-invocation: true` so you control timing.

### Keep It Concise

- Challenge every paragraph: "Does Claude really need this?"
- Prefer examples over explanations
- Move detailed content to reference files
- Assume Claude is already smart

### Set Appropriate Freedom

- **High freedom**: Text-based instructions for flexible tasks
- **Medium freedom**: Pseudocode with parameters
- **Low freedom**: Specific scripts for fragile operations

### Running Skills in Subagents

Add `context: fork` to run a skill in isolation. The skill content becomes the task prompt:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

When this runs:

- Creates isolated context (no conversation history)
- Skill content becomes the subagent's task
- `agent` field determines execution environment (Explore, Plan, general-purpose, or custom)
- Results return to main conversation

Use `context: fork` for:

- Research tasks that need focused exploration
- Operations that shouldn't access conversation history
- Tasks requiring specific agent capabilities

### Enable Extended Thinking

Include the word "ultrathink" anywhere in your skill content to enable extended thinking mode for complex reasoning tasks.

### What NOT to Include

Don't create these files:

- README.md (use the main repo README)
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- User-facing documentation

Skills are for AI agents, not humans.

### Skill Discovery and Loading

**Context loading behavior:**

- **Default skills**: Description always in context, full content loads when invoked
- **`disable-model-invocation: true`**: Description not in context, full content loads when you invoke
- **`user-invocable: false`**: Description always in context, full content loads when Claude invokes

**Automatic discovery:**

Claude Code automatically discovers skills from nested `.claude/skills/` directories. If you're editing `packages/frontend/src/component.tsx`, Claude also looks in `packages/frontend/.claude/skills/`. This supports monorepo setups where packages have their own skills.

**Skill priority:**

When skills share the same name: enterprise > personal > project. Plugin skills use `plugin-name:skill-name` namespace to avoid conflicts.

## Testing Your Skill

1. **Add marketplace locally**:

   ```bash
   /plugin marketplace add /tmp/my-claude-skills
   ```

2. **Install your skill**:

   ```bash
   /plugin install your-skill-name@my-claude-skills
   ```

3. **Test with real queries**:
   - Ask questions that should trigger the skill
   - Verify Claude loads and follows the instructions
   - Check that bundled resources are accessible

4. **Iterate**:
   - Update SKILL.md based on testing
   - Refresh marketplace: `/plugin marketplace update my-claude-skills`
   - Reinstall: `/plugin install your-skill-name@my-claude-skills --force`

## Validation

Before committing, validate your skill:

```bash
# Check JSON syntax
python3 -m json.tool .claude-plugin/marketplace.json

# Check SKILL.md frontmatter
head -5 skills/your-skill/SKILL.md

# Verify required fields
grep "name:" skills/your-skill/SKILL.md
grep "description:" skills/your-skill/SKILL.md
```

## Example Skills to Study

Look at existing skills for patterns:

- **commit-generator**: Simple skill with no bundled resources
- Check [anthropics/skills](https://github.com/anthropics/skills) for more examples:
  - **docx**: Complex skill with scripts and references
  - **mcp-builder**: Skill with extensive reference documentation
  - **pdf**: Skill with helper scripts

## Marketplace Configuration

### Adding a Plugin Entry

In `.claude-plugin/marketplace.json`:

```json
{
  "name": "my-claude-skills",
  "owner": {
    "name": "Your Name"
  },
  "metadata": {
    "description": "Personal collection of Claude Code skills",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "skill-name",
      "version": "1.0.0",
      "description": "Brief description for marketplace listing",
      "source": "./skills/skill-name",
      "strict": false,
      "skills": ["./skills/skill-name"]
    }
  ]
}
```

### Field Explanations

- `name`: Plugin identifier (kebab-case)
- `version`: Semantic version (MAJOR.MINOR.PATCH) - increment when updating the skill
- `description`: Brief description for marketplace listing
- `source`: Relative path to skill directory
- `strict`: Set to `false` to let marketplace define everything
- `skills`: Array of paths to skill directories

### Version Management

Follow semantic versioning for skills:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to skill behavior or interface
  - Changed argument format
  - Removed functionality
  - Changed output format that breaks existing workflows

- **MINOR** (1.0.0 → 1.1.0): New features, backward-compatible
  - Added new capabilities
  - New optional arguments
  - Enhanced functionality

- **PATCH** (1.0.0 → 1.0.1): Bug fixes, improvements
  - Fixed errors
  - Improved descriptions
  - Performance improvements

When updating a skill:

1. Update the `version` field in marketplace.json
2. Test the changes thoroughly
3. Document changes in commit message

## Commit Message Convention

Follow conventional commits:

```bash
feat(skills): add new-skill-name
fix(commit-generator): improve message formatting
docs: update contributing guide
refactor(skills): reorganize skill structure
```

## Questions?

- Check [Marketplace Documentation](https://code.claude.com/docs/en/plugin-marketplaces#create-and-distribute-a-plugin-marketplace)
- Review [Creating Skills Guide](https://code.claude.com/docs/en/skills)
- Study [anthropics/skills](https://github.com/anthropics/skills) examples
