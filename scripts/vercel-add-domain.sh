#!/bin/sh
# vercel-add-domain.sh — 把域名登记为 Vercel 项目域名（custom domain）
#
# 为什么不用 `vercel alias set`：alias 建的是部署级别名，项目若开了
# ssoProtection=all_except_custom_domains，alias 域名会被拦到 Vercel 登录页。
# 只有项目域名（custom domain）在 SSO 豁免范围内。
#
# 用法: ./vercel-add-domain.sh <project-name> <domain>
# 依赖: vercel CLI 已登录（token 读自本地 CLI 配置）；curl；python3（解析 JSON）
set -eu

PROJECT="${1:?usage: vercel-add-domain.sh <project> <domain>}"
DOMAIN="${2:?usage: vercel-add-domain.sh <project> <domain>}"

AUTH_JSON="$HOME/Library/Application Support/com.vercel.cli/auth.json"
TOKEN="$(python3 -c "import json;print(json.load(open('$AUTH_JSON'))['token'])")"

# teamId 在项目 link 文件里（先 `vercel link` 或从 .vercel/project.json 读）
PROJECT_JSON="$(pwd)/.vercel/project.json"
if [ -f "$PROJECT_JSON" ]; then
  TEAM_ID="$(python3 -c "import json;print(json.load(open('$PROJECT_JSON'))['orgId'])")"
else
  echo "缺少 .vercel/project.json，请先在项目目录执行 vercel link" >&2
  exit 1
fi

echo "==> POST /v10/projects/$PROJECT/domains  name=$DOMAIN"
curl -sS -X POST "https://api.vercel.com/v10/projects/$PROJECT/domains?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$DOMAIN\"}" | python3 -m json.tool

echo "==> 验证（应看到 verified: true；证书签发需几分钟）"
curl -sS "https://api.vercel.com/v9/projects/$PROJECT/domains/$DOMAIN?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print('verified:', d.get('verified'))"

echo "==> 最后 curl -I https://$DOMAIN 确认公网 200（不是 Vercel 登录页）"
