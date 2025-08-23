#!/bin/bash
set -euo pipefail

REPO="ASaid-ASaid/ictgroup_website"

echo "This script helps you set required GitHub secrets for CI and Fly deploy."
echo "It will print the commands and will run them if 'gh' is installed and you confirm."

cat <<'CMD'
# Recommended secrets to set (replace <value> with your secret):
gh secret set FLY_API_TOKEN --repo $REPO --body "<fly_api_token>"
gh secret set SUPABASE_URL --repo $REPO --body "https://your-project.supabase.co"
gh secret set SUPABASE_ANON_KEY --repo $REPO --body "<anon_key>"
gh secret set SUPABASE_SERVICE_ROLE_KEY --repo $REPO --body "<service_role_key>"
gh secret set DATABASE_URL --repo $REPO --body "postgresql://user:pass@host:5432/dbname"
CMD

if command -v gh >/dev/null 2>&1; then
  read -p "gh is installed. Do you want to run these commands now? (y/N) " -r
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    gh secret set FLY_API_TOKEN --repo "$REPO"
    gh secret set SUPABASE_URL --repo "$REPO"
    gh secret set SUPABASE_ANON_KEY --repo "$REPO"
    gh secret set SUPABASE_SERVICE_ROLE_KEY --repo "$REPO"
    gh secret set DATABASE_URL --repo "$REPO"
    echo "Secrets set (you were prompted for each value)."
  else
    echo "Aborted. Run the printed gh commands manually."
  fi
else
  echo "gh CLI not found. Copy the printed commands and run them locally once you have gh installed and are authenticated."
fi
