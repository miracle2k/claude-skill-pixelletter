#!/bin/bash
# Install Pixelletter skill for Claude Code

SKILL_DIR="$HOME/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing Pixelletter skill for Claude Code..."

# Create skills directory if it doesn't exist
mkdir -p "$SKILL_DIR"

# Copy skill files
cp "$SCRIPT_DIR/.claude/skills/pixelletter.json" "$SKILL_DIR/"
cp "$SCRIPT_DIR/.claude/skills/pixelletter.md" "$SKILL_DIR/"

echo "Skill installed to $SKILL_DIR"
echo ""
echo "Next steps:"
echo "1. Set environment variables:"
echo "   export PIXELLETTER_EMAIL=\"your-email@example.com\""
echo "   export PIXELLETTER_PASSWORD=\"your-password\""
echo ""
echo "2. Add to your shell profile (~/.zshrc or ~/.bashrc) for persistence"
echo ""
echo "3. Use in Claude Code with: /pixelletter"
