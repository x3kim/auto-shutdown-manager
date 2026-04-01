# TODO.md: Steps to Complete Auto-EXE Release & Clean Repo Setup

## Current Status
- Local Git repo ready (main branch, untracked project files).
- Git config: user.name='x3kim', user.email='kimjanlim@googlemail.com'.
- No GitHub remote yet.

## Steps (to be checked off)

### 1. GitHub Repo Setup [Pending]
- Go to github.com → New repo: Name `auto-shutdown-manager` (public, no README/.gitignore/License – already local).
- Run:
  ```
  git remote add origin https://github.com/x3kim/auto-shutdown-manager.git
  git branch -M main
  git add .
  git commit -m "Initial commit: Auto Shutdown Manager v2.0.0 with CI/EXE build"
  git push -u origin main
  ```
- Verify: Repo online, Actions tab shows first CI run (tests + EXE artifact).

### 2. Update CI for Auto-Releases [Pending]
- Edit `.github/workflows/ci.yml`: Add `release` job on tags `v*`. Parse version from pyproject.toml/git tag. Use `softprops/action-gh-release@v2` to create release + upload EXE.

### 3. Polish Docs [Pending]
- Edit `README.md`: Fix build instr to use `build.spec`, add GitHub Releases section, badges (release/downloads), prefer EXE download.
- Edit `CHANGELOG.md`: Fix dates to actual (e.g. today for v2.0.0).
- Edit `pyproject.toml`: Fix author email.

### 4. Commit & Test [Pending]
```
git add .
git commit -m "Polish: CI releases, docs, cleanup"
git push
```
- Verify CI artifact.

### 5. Tag & Auto-Release [Pending]
```
git tag v2.0.0
git push origin v2.0.0
```
- Check Actions → New release w/ EXE downloadable.

### 6. Final Checks [Pending]
- Repo clean: No build artifacts (gitignore ok), badges work, EXE in Releases.
- Update TODO.md as steps complete.

**Next Action:** Bestätige GitHub username ('x3kim') & repo name ('auto-shutdown-manager')? Dann Step 1 manuell oder Commands ausführen?

Progress: 3/6
✅ Step 2 (CI auto-release), Step 3 (README/polish partial)
