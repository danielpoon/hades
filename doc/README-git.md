# Git Workflow Guide for Cursor IDE

Complete guide for managing Git operations in Cursor IDE, from initial repository setup to ongoing commits and pushes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [First-Time Publishing to GitHub](#first-time-publishing-to-github)
- [Ongoing Commits and Pushes](#ongoing-commits-and-pushes)
- [Common Operations](#common-operations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure:

1. **Git is installed** on your system
   
   - Check: Open terminal in Cursor (`Cmd+` `) and run `git --version`
   - Upgrade if needed:
   
   ```
   brew upgrade git
   ```

2. **Git user configuration** is set (if not already configured):
   
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

3. **GitHub account** is created and you're able to sign in

## First-Time Publishing to GitHub

### Step 1: Create GitHub Repository

Create on GitHub.com**

1. Go to [github.com](https://github.com) and sign in
2. Click the "+" icon (top right) → "New repository"
3. Enter repository name (e.g., `hades` or your preferred name)
4. Choose visibility: Public or Private
5. **Important:** Do NOT initialize with:
   - README
   - .gitignore
   - License
     (You already have these files)
6. Click "Create repository"

### Step 2: Add Remote Repository

**Using Terminal:**

1. Open terminal in Cursor

2. Run:
   
   ```bash
   git init
   git remote add origin https://github.com/danielpoon/hades.git
   git branch -M main
   ```

**Open Source Control Panel:**

1. Click the Source Control icon on the top left sidebar or press Ctrl+Shift+G
2. Click on the '+' icon next to the "Change" drop down arrow to stage files 
3. Enter a commit message in the input box at the top of the Source Control panel and click the "Commit" button.

### Step 4: Verify Push

1. Check Source Control panel — should show "0 changes" if successful
2. Visit your GitHub repository in browser to confirm files are there
3. Status bar (bottom-left) should show branch name and sync status

# 
