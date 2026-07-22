#!/usr/bin/env bash
set -e

# ------------------------------------------------------------
# Sync Claude Memory (conversation artifacts) to the Git repo
# ------------------------------------------------------------
# Conversation ID whose memory you want to sync. Update if needed.
CONV_ID="06f7d0ed-cc69-4584-b3d4-c29470b51617"

# Source directory (Claude memory location)
SRC="/home/giga/.gemini/antigravity-ide/brain/${CONV_ID}"
# Destination inside the repository – keep under a dedicated folder
DEST="$(pwd)/memory"

# Ensure destination exists
mkdir -p "${DEST}"

# Copy all files (preserve structure). Exclude any .git directories that might exist inside the source.
rsync -av --exclude='.git' "${SRC}/" "${DEST}/"

# Commit and push if there are changes
git add memory
if ! git diff-index --quiet HEAD --; then
  git commit -m "Sync Claude memory (conversation ${CONV_ID})"
  git push origin main
else
  echo "No changes to sync."
fi
