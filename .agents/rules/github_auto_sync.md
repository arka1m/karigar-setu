# Rule: Permanent Automatic GitHub & Render Sync

Always enforce automatic Git commit & push behavior after any modification in this workspace (`karigar-setu`).

## Instructions
1. After every successful code change, UI change, bug fix, feature addition, deletion, or file modification:
   - Run `git add -A`
   - Create a clear, meaningful commit message
   - Commit and push to `origin/main` (`git push origin main`)
   - If GitHub remote is ahead, automatically run `git pull --rebase origin main`, resolve safe conflicts, and push again.
2. After every push, output ONLY:
   - ✅ GitHub Updated
   - **Commit message**: `<message>`
   - **Commit ID**: `<commit_id>`
   - **Render auto-deployment status**: Triggered & Verified (`https://karigar-setu.onrender.com/`)
3. Keep this behavior permanently enabled for this project until explicitly told to disable it.
