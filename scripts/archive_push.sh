#!/usr/bin/env bash
# 🎯 一鍵封存 push — 安全 stage/commit（若有變更）+ push 分支 + annotated tag + push tag。
# 認證：.env 之 GITHUB_TOKEN 經 GIT_ASKPASS（不改寫 origin URL、不嵌入 token）。全本地、零 Claude usage。
#
# 執行指令矩陣:
#   bash scripts/archive_push.sh                              # 預設 slug=seal；commit 訊息=日期 archive push
#   bash scripts/archive_push.sh --slug lint-p1p3-cmd-matrix  # tag=archive-YYYYMMDD-<slug>
#   bash scripts/archive_push.sh --message "docs: ..."        # 自訂 commit 訊息（有變更時）
#   bash scripts/archive_push.sh --tag archive-20260723-custom # 覆寫 tag 名（預設 archive-YYYYMMDD-<slug>）
#   bash scripts/archive_push.sh --allow-branch               # 非 main 分支仍 push（預設拒絕）
#   bash scripts/archive_push.sh --dry-run                    # 只印計畫、不動 git remote
#   bash scripts/archive_push.sh --retag                      # tag 已存在時 force 重打（破壞性；預設失敗退出）
#
# 對稱工具：拉取 `bash sync_from_github.sh`（根目錄）；封存 push 本腳本。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || { echo "✗ 找不到專案目錄 $ROOT"; exit 1; }

REMOTE="${REMOTE:-origin}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
SLUG="seal"
TAG=""
MESSAGE=""
DRY_RUN=0
RETAG=0
ALLOW_BRANCH=0
ASKPASS_SCRIPT=""

usage() {
  sed -n '2,14p' "$0" | sed 's/^# \?//'
  echo ""
  echo "選項: --slug SLUG  --tag NAME  --message MSG  --allow-branch  --dry-run  --retag"
}

cleanup() {
  if [ -n "$ASKPASS_SCRIPT" ] && [ -f "$ASKPASS_SCRIPT" ]; then
    rm -f "$ASKPASS_SCRIPT"
  fi
}
trap cleanup EXIT

while [ $# -gt 0 ]; do
  case "$1" in
    --slug) SLUG="${2:?--slug 需值}"; shift 2 ;;
    --tag) TAG="${2:?--tag 需值}"; shift 2 ;;
    --message|--msg) MESSAGE="${2:?--message 需值}"; shift 2 ;;
    --allow-branch) ALLOW_BRANCH=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --retag) RETAG=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "✗ 未知參數: $1"; usage; exit 1 ;;
  esac
done

# ---- 0) git repo ----
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "✗ 不在 git repository"; exit 1
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "✗ remote '$REMOTE' 不存在"; exit 1
fi

REMOTE_URL="$(git remote get-url "$REMOTE")"
if ! printf '%s' "$REMOTE_URL" | grep -qE '^https://'; then
  echo "✗ origin 須為乾淨 HTTPS（目前: $REMOTE_URL）"; exit 1
fi
if printf '%s' "$REMOTE_URL" | grep -qE '://[^/@]+:[^/@]+@'; then
  echo "✗ remote URL 嵌入 token/密碼——請改為 https://github.com/<owner>/<repo>.git"; exit 1
fi

SANITIZED_URL="$(printf '%s' "$REMOTE_URL" | sed -E 's#https://[^/@]+:[^/@]+@#https://#')"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" != "$DEFAULT_BRANCH" ] && [ "$ALLOW_BRANCH" -eq 0 ]; then
  echo "✗ 目前在分支 '$BRANCH'、非 '$DEFAULT_BRANCH'——加 --allow-branch 才 push"; exit 1
fi

DATE_STAMP="$(date +%Y%m%d)"
if [ -z "$TAG" ]; then
  TAG="archive-${DATE_STAMP}-${SLUG}"
fi

if [ -z "$MESSAGE" ]; then
  MESSAGE="$(date +%Y-%m-%d) archive push"
fi

# ---- .env + 認證 ----
if [ ! -f "$ROOT/.env" ]; then
  echo "✗ 找不到 .env（需 GITHUB_TOKEN）"; exit 1
fi
set -a
# shellcheck disable=SC1091
source "$ROOT/.env"
set +a

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "✗ .env 缺少 GITHUB_TOKEN"; exit 1
fi
export GITHUB_TOKEN

apply_git_identity() {
  local line
  while IFS= read -r line || [ -n "${line:-}" ]; do
    [ -z "$line" ] && continue
    case "$line" in
      git\ config\ --global\ *)
        if [ "$DRY_RUN" -eq 0 ]; then
          eval "$line"
        else
          echo "  [dry-run] $line"
        fi
        ;;
    esac
  done < <(grep '^git config --global' "$ROOT/.env" 2>/dev/null || true)
}

setup_git_auth() {
  ASKPASS_SCRIPT="$(mktemp)"
  chmod 700 "$ASKPASS_SCRIPT"
  cat > "$ASKPASS_SCRIPT" <<'EOF'
#!/bin/sh
case "$1" in
  *[Uu][Ss][Ee][Rr][Nn][Aa][Mm][Ee]*) printf '%s\n' "git" ;;
  *) printf '%s\n' "${GITHUB_TOKEN}" ;;
esac
EOF
  chmod 700 "$ASKPASS_SCRIPT"
  export GIT_ASKPASS="$ASKPASS_SCRIPT"
  export GIT_TERMINAL_PROMPT=0
}

# ---- 安全：拒絕 stage 的路徑 ----
MAX_FILE_BYTES=$((10 * 1024 * 1024))

is_forbidden_path() {
  local p="$1"
  local base="${p##*/}"
  case "$p" in
    .env|.env.*|*/.env|*/.env.*) return 0 ;;
    *.dump|*/*.dump) return 0 ;;
    *.zip|*/*.zip) return 0 ;;
    .webui_secret_key|*/.webui_secret_key) return 0 ;;
    credentials|credentials.*|*/credentials|*/credentials.*) return 0 ;;
    *.pem|*.key|*.p12|*.pfx) return 0 ;;
    */venv/*|venv/*|.venv/*|*/.venv/*) return 0 ;;
    data/*|/data/*|models_artifacts/*|augur-data/*|.db_export/*) return 0 ;;
  esac
  case "$base" in
    .env|.env.*|*.dump|*.zip|.webui_secret_key|credentials|credentials.*) return 0 ;;
  esac
  if [ -f "$p" ]; then
    local sz
    sz="$(stat -c%s "$p" 2>/dev/null || echo 0)"
    if [ "$sz" -gt "$MAX_FILE_BYTES" ]; then
      echo "✗ 拒絕 stage 大型檔案 (>10MB): $p (${sz} bytes)" >&2
      return 0
    fi
  fi
  return 1
}

collect_changed_paths() {
  git status --porcelain | while IFS= read -r line || [ -n "${line:-}" ]; do
    [ -z "$line" ] && continue
    local path="${line#?? }"
    path="${path#\"}"; path="${path%\"}"
    path="${path%% -> *}"
    printf '%s\n' "$path"
  done
}

scan_forbidden_in_changes() {
  local p forbidden=0 warned=0
  while IFS= read -r p || [ -n "${p:-}" ]; do
    [ -z "$p" ] && continue
    if is_forbidden_path "$p"; then
      if [ "$warned" -eq 0 ]; then
        echo "⚠ 下列路徑在變更中但禁止 stage（略過）:"
        warned=1
      fi
      echo "    - $p"
      forbidden=1
    fi
  done < <(collect_changed_paths)
  return "$forbidden"
}

stage_safe_changes() {
  local p staged=0
  scan_forbidden_in_changes || true
  while IFS= read -r p || [ -n "${p:-}" ]; do
    [ -z "$p" ] && continue
    if is_forbidden_path "$p"; then
      continue
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "  [dry-run] git add -- $p"
    else
      git add -- "$p"
    fi
    staged=1
  done < <(collect_changed_paths)
  if [ "$staged" -eq 0 ]; then
    return 1
  fi
  return 0
}

run_git() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] git $*"
  else
    git "$@"
  fi
}

# ---- 1) commit（若有安全變更）----
HAS_CHANGES=0
if [ -n "$(git status --porcelain)" ]; then
  HAS_CHANGES=1
  echo "▶ 偵測到 working tree 變更"
  apply_git_identity
  if stage_safe_changes; then
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "  [dry-run] git commit -m $(printf '%q' "$MESSAGE")"
    else
      if git diff --cached --quiet; then
        echo "✗ 變更皆為禁止路徑，無可 stage 內容——中止"
        git status --short
        exit 1
      fi
      git commit -m "$MESSAGE"
      echo "✓ commit 完成"
    fi
  else
    echo "✗ 無可安全 stage 的變更（可能全為禁止路徑）"
    git status --short
    exit 1
  fi
else
  echo "▶ working tree 乾淨，略過 commit"
fi

HEAD_SHA="$(git rev-parse HEAD)"

# ---- 2) push branch ----
echo "▶ push 分支 $BRANCH → $REMOTE"
apply_git_identity
if [ "$DRY_RUN" -eq 0 ]; then
  setup_git_auth
fi
run_git push "$REMOTE" HEAD

# ---- 3) annotated tag ----
TAG_EXISTS=0
if git rev-parse "$TAG" >/dev/null 2>&1; then
  TAG_EXISTS=1
  if [ "$RETAG" -eq 0 ]; then
    echo "✗ tag '$TAG' 已存在——若要覆寫请加 --retag（破壞性 force）"
    exit 1
  fi
  echo "⚠ --retag：force 重打 annotated tag '$TAG'"
fi

TAG_MSG="Archive seal ${TAG} ($(date +%Y-%m-%d))"
if [ "$DRY_RUN" -eq 1 ]; then
  if [ "$TAG_EXISTS" -eq 1 ]; then
    echo "  [dry-run] git tag -f -a $(printf '%q' "$TAG") -m $(printf '%q' "$TAG_MSG")"
  else
    echo "  [dry-run] git tag -a $(printf '%q' "$TAG") -m $(printf '%q' "$TAG_MSG")"
  fi
else
  if [ "$TAG_EXISTS" -eq 1 ]; then
    git tag -f -a "$TAG" -m "$TAG_MSG"
  else
    git tag -a "$TAG" -m "$TAG_MSG"
  fi
fi

# ---- 4) push tag ----
echo "▶ push tag $TAG → $REMOTE"
if [ "$DRY_RUN" -eq 1 ]; then
  if [ "$RETAG" -eq 1 ] || [ "$TAG_EXISTS" -eq 1 ]; then
    echo "  [dry-run] git push --force $REMOTE $(printf '%q' "$TAG")"
  else
    echo "  [dry-run] git push $REMOTE $(printf '%q' "$TAG")"
  fi
else
  if [ "$RETAG" -eq 1 ] || [ "$TAG_EXISTS" -eq 1 ]; then
    git push --force "$REMOTE" "$TAG"
  else
    git push "$REMOTE" "$TAG"
  fi
fi

echo "════════════════════════════════════════════"
echo "  ✓ 封存 push 完成"
echo "  branch : $BRANCH"
echo "  HEAD   : $HEAD_SHA ($(git log -1 --oneline))"
echo "  tag    : $TAG"
echo "  remote : $SANITIZED_URL"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "  mode   : dry-run（未改 remote）"
fi
echo "════════════════════════════════════════════"

exit 0
