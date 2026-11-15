#!/usr/bin/env bash
# 把 skills/ 下的 4 个 skill 软链到 WorkBuddy / Claude Code 的 skills 目录
# 用法: ./install.sh            (默认 WorkBuddy)
#       ./install.sh claude     (Claude Code)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
case "${1:-workbuddy}" in
  claude) DEST="$HOME/.claude/skills" ;;
  *)      DEST="$HOME/.workbuddy/skills" ;;
esac
mkdir -p "$DEST"
for d in "$HERE"/skills/*/; do
  name="$(basename "$d")"
  ln -sfn "$d" "$DEST/$name"
  echo "linked $name -> $DEST/$name"
done
echo "AviList 数据: $HERE/assets/avilist_species.json"
echo "下一步: cp config.example.json config.json 并填写; export NOTION_TOKEN=ntn_xxx"
