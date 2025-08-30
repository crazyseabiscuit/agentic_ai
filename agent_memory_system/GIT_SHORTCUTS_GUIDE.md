# Git 快捷命令使用指南

## 🚀 快速开始

### 方法1: 运行安装脚本 (推荐)
```bash
cd agent_memory_system
./install_git_shortcuts.sh
```

### 方法2: 手动加载
```bash
source git_shortcuts.sh
```

## 📋 可用命令

### 🔥 主要命令

#### `gitsync "commit message"`
- **功能**: 添加所有文件 → 提交 → 推送到远程仓库
- **示例**: `gitsync "Add memory system feature"`

#### `gitsync-files "commit message" file1 file2`
- **功能**: 添加指定文件 → 提交 → 推送到远程仓库
- **示例**: `gitsync-files "Update docs" README.md config.py`

### 🔧 辅助命令

#### `gs`
- **功能**: 显示简洁的git状态
- **示例**: `gs`

#### `gitquick "commit message"`
- **功能**: 添加所有文件 → 提交 (不推送)
- **示例**: `gitquick "Save progress"`

#### `git sync "commit message"`
- **功能**: git alias版本，与gitsync相同
- **示例**: `git sync "Add something"`

## 🎯 使用场景

### 日常开发
```bash
# 完成功能开发后
gitsync "Implement user authentication"

# 只更新文档
gitsync-files "Update README" README.md

# 快速保存进度
gitquick "WIP: working on API"
```

### 团队协作
```bash
# 提交代码审查
gitsync "Fix: resolve merge conflicts"

# 紧急修复
gitsync "Hotfix: fix critical bug"

# 文档更新
gitsync-files "Add API documentation" docs/api.md
```

## ⚙️ 自定义配置

### 修改默认行为
编辑 `git_shortcuts.sh` 文件：

```bash
# 修改gitsync函数，添加更多检查
gitsync() {
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        echo "🔄 Found uncommitted changes..."
    fi
    
    # 添加文件
    git add -A
    
    # 提交
    git commit -m "$1"
    
    # 推送前检查网络
    if ping -c 1 github.com > /dev/null 2>&1; then
        git push
    else
        echo "⚠️  Network issues, skipping push"
    fi
}
```

### 添加新的快捷命令
```bash
# 查看最近的提交
gitrecent() {
    git log --oneline -10
}

# 撤销最后一次提交
gitundo() {
    git reset --hard HEAD~1
}

# 清理未跟踪的文件
gitclean() {
    git clean -fd
}
```

## 🔍 故障排除

### 命令未找到
```bash
# 重新加载配置
source ~/.bashrc  # 或 ~/.zshrc

# 或手动加载
source /path/to/git_shortcuts.sh
```

### 权限问题
```bash
chmod +x git_shortcuts.sh
chmod +x install_git_shortcuts.sh
```

### Git配置问题
```bash
# 检查git配置
git config --list

# 设置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 🎨 高级用法

### 结合项目工作流
```bash
# 创建项目特定的快捷命令
project-sync() {
    if [ "$1" = "dev" ]; then
        gitsync "Development update: $2"
    elif [ "$1" = "prod" ]; then
        gitsync "Production release: $2"
    else
        gitsync "$1"
    fi
}

# 使用示例
project-sync dev "Add new API endpoints"
project-sync prod "Deploy version 1.2.0"
```

### 自动化脚本
```bash
#!/bin/bash
# auto_sync.sh - 自动同步脚本

# 检查是否有更改
if [ -n "$(git status --porcelain)" ]; then
    echo "🔄 Found changes, auto-syncing..."
    gitsync "Auto-sync: $(date)"
else
    echo "✅ No changes to sync"
fi
```

## 📚 最佳实践

### 提交信息规范
```bash
# 好的提交信息
gitsync "feat: add user authentication"
gitsync "fix: resolve login bug"
gitsync "docs: update README installation"
gitsync "style: format code with black"
gitsync "refactor: improve memory system performance"

# 避免的提交信息
gitsync "update"        # 太模糊
gitsync "fix bug"       # 不具体
gitsync "work"          # 无意义
```

### 使用前检查
```bash
# 检查将要提交的更改
gs

# 检查特定文件状态
git status filename.py

# 查看差异
git diff
```

## 🔄 升级和维护

### 更新快捷命令
```bash
# 编辑快捷命令文件
nano git_shortcuts.sh

# 重新加载
source git_shortcuts.sh
```

### 备份配置
```bash
# 备份git配置
git config --global --list > git_config_backup.txt

# 备份快捷命令
cp git_shortcuts.sh git_shortcuts.sh.backup
```

## 🎉 总结

这些Git快捷命令将显著提高你的开发效率：

- **`gitsync`** - 一键完成添加、提交、推送
- **`gitsync-files`** - 选择性文件同步
- **`gs`** - 快速查看状态
- **`gitquick`** - 本地提交暂存

开始使用这些命令，享受更高效的Git工作流程！