#!/usr/bin/env bash
# Creates a throwaway git repo with a (FAKE) leaked token, then "removes" it.
set -euo pipefail
rm -rf leaky-repo && mkdir leaky-repo && cd leaky-repo
git init -q && git config user.email demo@uis.no && git config user.name "DAT250 Demo"
# Fake token built at runtime so this script itself doesn't trip scanners
FAKE="ghp_$(head -c 200 /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c 36)"
cat > config.py <<PY
GITHUB_TOKEN = "$FAKE"
DEBUG = True
PY
git add . && git commit -qm "add config"
# "Fix" it the wrong way: delete the line in a new commit
echo 'DEBUG = True' > config.py
git commit -qam "remove token"
echo "Repo ready. Current config.py:"; cat config.py
