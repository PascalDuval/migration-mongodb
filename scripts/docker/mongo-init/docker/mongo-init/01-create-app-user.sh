Nouveau
+41
-0

#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${MONGO_APP_USER:-}" || -z "${MONGO_APP_PASSWORD:-}" ]]; then
  echo "⚠️  Variables MONGO_APP_USER et MONGO_APP_PASSWORD requises pour créer l'utilisateur applicatif." >&2
  exit 1
fi

app_db="${MONGO_APP_DATABASE:-${MONGO_INITDB_DATABASE:-test}}"
auth_source="${MONGO_APP_AUTH_SOURCE:-$app_db}"
roles_csv="${MONGO_APP_ROLES:-readWrite,dbOwner}"

IFS=',' read -ra raw_roles <<< "$roles_csv"
roles=()
for role in "${raw_roles[@]}"; do
  trimmed="$(echo "$role" | xargs)"
  [[ -z "$trimmed" ]] && continue
  roles+=("{ role: \"$trimmed\", db: \"$app_db\" }")
done

if [[ ${#roles[@]} -eq 0 ]]; then
  roles=("{ role: \"readWrite\", db: \"$app_db\" }" "{ role: \"dbOwner\", db: \"$app_db\" }")
fi

roles_js=$(IFS=','; printf "%s" "${roles[*]}")

cat <<EOJS | mongosh --quiet
const appDb = "$app_db";
const authSource = "$auth_source";
const targetUser = "$MONGO_APP_USER";
const targetPwd = "$MONGO_APP_PASSWORD";
const roles = [$roles_js];

const authDb = db.getSiblingDB(authSource);
if (authDb.getUser(targetUser)) {
  print(`🔁 Utilisateur ${MONGO_APP_USER} déjà présent dans ${authSource}, aucune modification.`);
} else {
  authDb.createUser({ user: targetUser, pwd: targetPwd, roles });
  print(`✅ Utilisateur ${MONGO_APP_USER} créé avec les rôles ${roles_csv} (authSource=${authSource}, db=${appDb}).`);
}
EOJS