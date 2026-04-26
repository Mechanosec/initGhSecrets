#!/bin/bash
set -euo pipefail

REPO="6037-Title/admin-backend"
ENVIRONMENT="prod"
SECRETS_FILE="secrets.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is required"
  exit 1
fi

echo "Clearing all secrets in:"
echo "  Repo: $REPO"
echo "  Environment: $ENVIRONMENT"
echo

# Видаляємо всі секрети (без --confirm)
for secret in $(gh secret list --repo "$REPO" --env "$ENVIRONMENT" --json name -q '.[].name'); do
  echo "→ Deleting secret: $secret"
  gh secret delete "$secret" --repo "$REPO" --env "$ENVIRONMENT"
done

echo
echo "Adding new secrets from $SECRETS_FILE:"
jq -r '.[] | @base64' "$SECRETS_FILE" | while read -r entry; do
  key=$(echo "$entry" | base64 --decode | jq -r '.name')
  value=$(echo "$entry" | base64 --decode | jq -r '.value')

  echo "→ Setting secret: $key"
  gh secret set "$key" \
    --repo "$REPO" \
    --env "$ENVIRONMENT" \
    -b"$value"
done

echo
echo "Done."
