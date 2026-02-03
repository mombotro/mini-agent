# Pushing to Private GitHub Repository

## Quick Steps

### 1. Create Private GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the **+** icon in the top right → **New repository**
3. Fill in:
   - **Repository name**: `ollama-agent-memory` (or your preferred name)
   - **Description**: "Ollama agent with persistent memory and growing soul"
   - **Visibility**: ⚠️ **Private** (important!)
   - **Initialize**: Leave all checkboxes unchecked (we already have files)
4. Click **Create repository**

### 2. Push Your Code

GitHub will show you commands. Use these in your terminal:

```bash
cd "C:\Users\mom\Documents\tools\agent"

# Add the remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/ollama-agent-memory.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example** (if your username is `juleah`):
```bash
git remote add origin https://github.com/juleah/ollama-agent-memory.git
git branch -M main
git push -u origin main
```

### 3. Verify Upload

1. Go to your repository URL
2. You should see all the files:
   - README.md
   - simple_agent.py
   - simple_memory.py
   - config.py
   - etc.

✓ **Note**: Your `memory_store/` folder and personal `soul.md` are NOT uploaded (they're in `.gitignore`)

## Authentication

If prompted for credentials:

### Option A: Personal Access Token (Recommended)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Ollama Agent"
4. Select scopes: `repo` (full control)
5. Generate and copy the token
6. Use the token as your password when pushing

### Option B: GitHub CLI

```bash
# Install GitHub CLI (if not already installed)
winget install GitHub.cli

# Authenticate
gh auth login

# Push using gh
gh repo create ollama-agent-memory --private --source=. --remote=origin --push
```

### Option C: SSH Key

If you prefer SSH:
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Copy your public key
cat ~/.ssh/id_ed25519.pub

# Use SSH URL instead
git remote add origin git@github.com:YOUR-USERNAME/ollama-agent-memory.git
git push -u origin main
```

## Future Updates

After making changes, push updates with:

```bash
cd "C:\Users\mom\Documents\tools\agent"

# Stage changes
git add simple_agent.py simple_memory.py config.py README.md

# Or stage everything (respects .gitignore)
git add .

# Commit
git commit -m "Description of your changes"

# Push
git push
```

## Important Notes

⚠️ **Privacy**: Your `memory_store/` and `soul.md` files are excluded from git via `.gitignore`. These contain your personal conversations and should NOT be pushed to GitHub.

✓ **What IS pushed**:
- Source code (simple_agent.py, simple_memory.py)
- Configuration template (config.py)
- Documentation (README.md, quick_start.md)
- Dependencies (requirements-simple.txt)

✗ **What is NOT pushed**:
- Your personal memories (memory_store/)
- Your soul.md file
- Python cache files (__pycache__)
- Test scripts (test_*.py)

## Cloning on Another Computer

To use your agent on another machine:

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/ollama-agent-memory.git
cd ollama-agent-memory

# Install dependencies
pip install ollama

# Pull Ollama model
ollama pull llama3.2:1b

# Run the agent
python simple_agent.py
```

The agent will start fresh (no memories) on the new machine. This is by design for privacy.

## Troubleshooting

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR-USERNAME/ollama-agent-memory.git
```

### "Updates were rejected"
```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### "Authentication failed"
- Use a Personal Access Token instead of password
- Or set up GitHub CLI: `gh auth login`

### Want to include soul.md in the repo?
Edit `.gitignore` and comment out the soul.md line:
```bash
# # soul.md
```

Then:
```bash
git add soul.md
git commit -m "Add soul.md"
git push
```

## Quick Reference

```bash
# Check status
git status

# See what's changed
git diff

# View commit history
git log --oneline

# See remote URL
git remote -v

# Pull latest changes
git pull

# Push changes
git push
```

---

**Next Steps**: After pushing to GitHub, you can access your code from anywhere, share it with others (if you make it public), or clone it to other machines!
