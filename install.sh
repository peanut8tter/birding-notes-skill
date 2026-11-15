#!/usr/bin/env bash
# 把 skills/ 下的 5 个 skill 软链到 AI 助手的 skills 目录。
# 遵循开放的 Agent Skills 标准（SKILL.md），适用于 Codex、Claude Code、WorkBuddy、Cursor 等。
#
# 用法:
#   ./install.sh                  默认: ~/.agents/skills（Codex 等通用标准位置）
#   ./install.sh claude           ~/.claude/skills
#   ./install.sh workbuddy        ~/.workbuddy/skills
#   ./install.sh codex            ~/.codex/skills（Codex 旧版位置）
#   ./install.sh all              以上全部
#   ./install.sh /自定义/路径      任意目录
#   可同时写多个: ./install.sh agents claude
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"

dest_for() {
  case "$1" in
    agents)    echo "$HOME/.agents/skills" ;;
    claude)    echo "$HOME/.claude/skills" ;;
    workbuddy) echo "$HOME/.workbuddy/skills" ;;
    codex)     echo "$HOME/.codex/skills" ;;
    /*|~*)     echo "$1" ;;
    *) echo "未知目标: $1" >&2; exit 1 ;;
  esac
}

install_to() {
  local DEST="$1"
  mkdir -p "$DEST"
  for d in "$HERE"/skills/*/; do
    name="$(basename "$d")"
    target="$DEST/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "  跳过 $name：$target 已存在且不是软链（请手动处理，避免覆盖）"
      continue
    fi
    ln -sfn "${d%/}" "$target"
    echo "  linked $name"
  done
}

TARGETS=("$@"); [ ${#TARGETS[@]} -eq 0 ] && TARGETS=(agents)
[ "${TARGETS[0]}" = "all" ] && TARGETS=(agents claude workbuddy codex)

for t in "${TARGETS[@]}"; do
  D="$(dest_for "$t")"; echo "→ $D"; install_to "$D"
done

echo ""
echo "AviList 数据: $HERE/assets/avilist_species.json"
echo "安装完成。下一步：打开你的 AI 助手，说「初始化观鸟笔记」，它会一步步问你 Notion token 等信息。"
echo "（若你的助手不支持 skills，把本仓库的 AGENTS.md 放进项目即可，见 README。）"
