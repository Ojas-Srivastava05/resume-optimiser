#!/usr/bin/env bash
# Commit tracked state files and push with rebase retries (handles parallel workflow races).
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: git-push-state.sh <commit-message> <path>..." >&2
  exit 1
fi

MSG="$1"
shift
BRANCH="${GITHUB_REF_NAME:-main}"

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

git add "$@" || true
if git diff --staged --quiet; then
  echo "No changes to commit."
  exit 0
fi

for attempt in 1 2 3 4 5; do
  git fetch origin "$BRANCH"
  git diff --staged --quiet || git commit -m "$MSG"
  if git pull --rebase --autostash origin "$BRANCH"; then
    if git push origin "HEAD:$BRANCH"; then
      echo "State pushed (attempt $attempt)."
      exit 0
    fi
  fi
  git rebase --abort 2>/dev/null || true
  git fetch origin "$BRANCH"
  git reset --soft "origin/$BRANCH"
  git add "$@" || true
  echo "Retrying state push (attempt $attempt)..."
  sleep $((attempt * 2))
done

echo "Failed to push state after 5 attempts." >&2
exit 1
