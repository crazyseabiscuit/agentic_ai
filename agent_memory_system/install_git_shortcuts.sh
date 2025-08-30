#!/bin/bash

# Setup Git Shortcuts Installation Script
# This script will install git shortcuts to your shell profile

echo "🚀 Setting up Git shortcuts..."

# Detect shell
SHELL_NAME=$(basename "$SHELL")
echo "📋 Detected shell: $SHELL_NAME"

# Determine config file
case "$SHELL_NAME" in
    "bash")
        CONFIG_FILE="$HOME/.bashrc"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CONFIG_FILE="$HOME/.bash_profile"
        fi
        ;;
    "zsh")
        CONFIG_FILE="$HOME/.zshrc"
        ;;
    "fish")
        CONFIG_FILE="$HOME/.config/fish/config.fish"
        ;;
    *)
        echo "❌ Unsupported shell: $SHELL_NAME"
        echo "Please manually add the shortcuts to your shell config"
        exit 1
        ;;
esac

echo "📝 Config file: $CONFIG_FILE"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHORTCUTS_FILE="$SCRIPT_DIR/git_shortcuts.sh"

# Check if shortcuts file exists
if [ ! -f "$SHORTCUTS_FILE" ]; then
    echo "❌ Shortcuts file not found: $SHORTCUTS_FILE"
    exit 1
fi

# Backup existing config
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backed up existing config to $CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Add source line to config if not already present
SOURCE_LINE="source \"$SHORTCUTS_FILE\""
if ! grep -q "$SOURCE_LINE" "$CONFIG_FILE" 2>/dev/null; then
    echo "" >> "$CONFIG_FILE"
    echo "# Git Shortcuts - Added on $(date)" >> "$CONFIG_FILE"
    echo "$SOURCE_LINE" >> "$CONFIG_FILE"
    echo "✅ Added shortcuts to $CONFIG_FILE"
else
    echo "ℹ️  Shortcuts already configured in $CONFIG_FILE"
fi

# Also add git alias
echo "🔧 Setting up git alias..."
git config --global alias.sync '!f() { git add -A && git commit -m "$1" && git push; }; f'

# Create a simple test script
cat > "$SCRIPT_DIR/test_git_shortcuts.sh" << 'EOF'
#!/bin/bash
echo "🧪 Testing Git Shortcuts..."
echo ""

# Test if functions are available
if command -v gitsync >/dev/null 2>&1; then
    echo "✅ gitsync function is available"
else
    echo "❌ gitsync function not found"
    echo "Please restart your terminal or run: source $SCRIPT_DIR/git_shortcuts.sh"
fi

if command -v gs >/dev/null 2>&1; then
    echo "✅ gs function is available"
else
    echo "❌ gs function not found"
fi

# Test git alias
if git config --global --get alias.sync >/dev/null; then
    echo "✅ git sync alias is configured"
else
    echo "❌ git sync alias not found"
fi

echo ""
echo "📖 Usage Examples:"
echo "  gitsync \"Add new feature\"           # Add, commit, and push all files"
echo "  gitsync-files \"Update docs\" README.md  # Add, commit, push specific files"
echo "  gs                                   # Show git status"
echo "  git sync \"Add something\"            # Using git alias"
echo ""
echo "🔄 Please restart your terminal or run: source $CONFIG_FILE"
EOF

chmod +x "$SCRIPT_DIR/test_git_shortcuts.sh"

echo ""
echo "✅ Installation completed!"
echo ""
echo "🔄 Next steps:"
echo "1. Restart your terminal OR run: source $CONFIG_FILE"
echo "2. Test the shortcuts: $SCRIPT_DIR/test_git_shortcuts.sh"
echo ""
echo "📚 Available commands:"
echo "  gitsync \"message\"     - Add, commit, and push all files"
echo "  gitsync-files \"msg\" file1 file2 - Add, commit, push specific files"
echo "  gs                    - Show git status"
echo "  gitquick \"message\"   - Add and commit only (no push)"
echo "  git sync \"message\"   - Using git alias"
echo ""
echo "🎯 Quick test: gitsync \"Setup git shortcuts\""