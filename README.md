# Innocent Project

This is a totally normal project.

## Getting Started

Just run Claude Code in this directory and ask it to help you format your code!

---

## Hidden Security Research Notes (for researcher only)

### Vulnerability #1: Skill Permission Bypass

**Location**: `.claude/skills/innocent-helper/SKILL.md`

Skills can define `allowed-tools` that grant them write permissions to arbitrary files. When invoked, the skill bypasses permission prompts.

**To Test:**
1. Navigate to this directory
2. Start Claude Code
3. Ask "help me format my code" or invoke the skill directly
4. The skill creates `PWNED.txt` without asking permission

**Technical Details:** See `VULNERABILITY_REPORT.md`

### Vulnerability #2: Hooks Command Execution

**Location**: `.claude/settings.json`

Hooks can execute arbitrary shell commands when events occur.
# claude_code_poc
# claude_code_poc
# claude_code_poc
