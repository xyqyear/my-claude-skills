---
name: commit-generator
description: Intelligent git commit message generator. Use when the user asks to create a commit, generate a commit message, or wants help writing a good commit message. Analyzes git diff output and repository commit history to generate conventional commit messages that follow the project's style and best practices.
---

# Git Commit Message Generator

Generate high-quality, conventional commit messages by analyzing staged changes and repository history.

## Quick Start

When the user asks to create a commit or generate a commit message:

1. **Gather context** (run in parallel):
   ```bash
   git status
   git diff --cached
   git log --oneline -10
   ```

2. **Analyze the changes**:
   - Identify the type of change (feat, fix, refactor, docs, style, test, chore)
   - Determine the scope (component/module affected)
   - Understand the impact and purpose

3. **Generate the commit message** following this format:
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```

## Commit Message Structure

### Type
Choose the most appropriate type:

- **feat**: New feature for the user
- **fix**: Bug fix
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (formatting, whitespace)
- **test**: Adding or updating tests
- **chore**: Changes to build process, dependencies, or tooling
- **perf**: Performance improvement
- **ci**: CI/CD configuration changes
- **build**: Changes to build system or dependencies
- **revert**: Reverts a previous commit

### Scope
The scope should be the name of the component/module affected (optional but recommended):
- Examples: `api`, `auth`, `ui`, `database`, `parser`, `config`

### Subject
- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters
- Be specific and concise

### Body (optional)
- Explain the "what" and "why", not the "how"
- Wrap at 72 characters
- Separate from subject with blank line
- Use bullet points for multiple items

### Footer (optional)
- Reference issues: `Closes #123` or `Fixes #456`
- Breaking changes: `BREAKING CHANGE: description`

## Examples

### Simple feature
```
feat(auth): add JWT token refresh mechanism

Implement automatic token refresh to improve user experience
by preventing unexpected logouts during active sessions.

Closes #234
```

### Bug fix
```
fix(parser): handle null values in JSON response

Previously crashed when API returned null in optional fields.
Now gracefully handles null values with default fallbacks.
```

### Refactoring
```
refactor(database): migrate from PyYAML to ruamel.yaml

Replace PyYAML with ruamel.yaml for better YAML 1.2 support
and improved round-trip preservation of comments and formatting.

Closes #9
```

### Multiple changes
```
chore(deps): update dependencies and remove unused packages

- Remove unused backend dependencies
- Update pytest to 8.x
- Update FastAPI to latest stable version
```

## Best Practices

1. **Read the repository's commit history** to match the existing style
2. **Be specific**: "fix login bug" → "fix(auth): prevent session timeout on page refresh"
3. **Focus on user impact**: Explain what changed from the user's perspective
4. **Keep it atomic**: One logical change per commit
5. **Use present tense**: "add feature" not "added feature"
6. **Reference issues**: Always link to issue numbers when applicable

## Workflow

1. Review `git status` to see what files are staged
2. Review `git diff --cached` to understand the actual changes
3. Review `git log` to understand the project's commit message style
4. Identify the primary purpose of the changes
5. Draft a commit message following the format above
6. Present the message to the user for approval
7. If approved, execute: `git commit -m "$(cat <<'EOF'\n<message>\nEOF\n)"`

## Anti-patterns to Avoid

- ❌ Vague messages: "update code", "fix stuff", "changes"
- ❌ Too technical: Focus on what changed, not implementation details
- ❌ Too long subjects: Keep under 50 characters
- ❌ Missing type prefix: Always include type (feat, fix, etc.)
- ❌ Past tense: Use "add" not "added"
- ❌ Combining unrelated changes: Keep commits focused

## Notes

- Always use HEREDOC syntax for multi-line commit messages to preserve formatting
- Don't commit unless the user explicitly asks
- If changes span multiple concerns, suggest splitting into multiple commits
- For large changesets, focus the message on the primary change
