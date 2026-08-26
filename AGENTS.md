# Workspace Rule: Permanent Automatic GitHub & Render Sync

Every time any code change, UI change, bug fix, feature addition, deletion, or file modification is made in this workspace (`karigar-setu`):

1. Automatically commit and push changes:
   - `git add -A`
   - Create a clear, meaningful commit message.
   - `git commit -m "<commit message>"`
   - `git push origin main`
   - If remote is ahead, automatically `git pull --rebase origin main` and push again.
2. After every push, output:
   - ✅ GitHub Updated
   - **Commit message**: `<message>`
   - **Commit ID**: `<commit_hash>`
   - **Render auto-deployment status**: Triggered & Verified (`https://karigar-setu.onrender.com/`)
