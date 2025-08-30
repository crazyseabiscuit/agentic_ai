#!/bin/bash

# Git sync function - add, commit, and push in one command
gitsync() {
    if [ -z "$1" ]; then
        echo "Usage: gitsync \"commit message\""
        echo "Example: gitsync \"Add memory system feature\""
        return 1
    fi
    
    echo "🔄 Adding all files to staging area..."
    git add -A
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to add files"
        return 1
    fi
    
    echo "📝 Committing with message: \"$1\""
    git commit -m "$1"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to commit"
        return 1
    fi
    
    echo "⬆️  Pushing to remote..."
    git push
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to push"
        return 1
    fi
    
    echo "✅ Successfully synced to git!"
}

# Git sync with specific files
gitsync-files() {
    if [ -z "$2" ]; then
        echo "Usage: gitsync-files \"commit message\" file1 file2 ..."
        echo "Example: gitsync-files \"Update docs\" README.md config.py"
        return 1
    fi
    
    message="$1"
    shift
    
    echo "🔄 Adding specified files to staging area..."
    git add "$@"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to add files"
        return 1
    fi
    
    echo "📝 Committing with message: \"$message\""
    git commit -m "$message"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to commit"
        return 1
    fi
    
    echo "⬆️  Pushing to remote..."
    git push
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to push"
        return 1
    fi
    
    echo "✅ Successfully synced selected files to git!"
}

# Git status with cleaner output
gs() {
    echo "📊 Git Status:"
    git status --short
}

# Quick add and commit (no push)
gitquick() {
    if [ -z "$1" ]; then
        echo "Usage: gitquick \"commit message\""
        return 1
    fi
    
    git add -A && git commit -m "$1"
    echo "✅ Files added and committed locally"
}

# Add to current shell
echo "✅ Git shortcuts loaded!"
echo "Available commands:"
echo "  gitsync \"message\"     - Add, commit, and push all files"
echo "  gitsync-files \"msg\" file1 file2 - Add, commit, push specific files"
echo "  gs                    - Show git status"
echo "  gitquick \"message\"   - Add and commit only (no push)"