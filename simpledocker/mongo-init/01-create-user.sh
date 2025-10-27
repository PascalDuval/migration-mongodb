#!/bin/bash
echo "🔐 Initialisation de la base MongoDB..."

mongosh <<EOF
use FirstTry
db.createUser({
  user: 'appuser',
  pwd: 'apppass',
  roles: [{ role: 'readWrite', db: 'FirstTry' }]
})
EOF