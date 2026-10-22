#!/usr/bin/env bash
# Dependency confusion, fully offline and harmless.
# Two local "indexes": the company's internal one and a "public" one an attacker controls.
set -euo pipefail
rm -rf build internal-index public-index venv && mkdir -p build internal-index public-index
python3 -m venv venv && . venv/bin/activate && pip install -q setuptools wheel

make_pkg () {   # name version message outdir
  d="build/$1-$2"; mkdir -p "$d/uis_internal_utils"
  cat > "$d/pyproject.toml" <<TOML
[project]
name = "$1"
version = "$2"
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
TOML
  echo "print('$3')" > "$d/uis_internal_utils/__init__.py"
  pip wheel -q --no-deps --no-build-isolation -w "$4" "$d"
}

make_pkg uis-internal-utils 1.2.0  "internal package (legit)"            internal-index
make_pkg uis-internal-utils 99.0.0 "!! attacker package would run here !!" public-index

# (same venv)
echo; echo ">>> pip install uis-internal-utils   (both sources configured, like --extra-index-url)"
pip install -q --no-index --find-links internal-index --find-links public-index uis-internal-utils
python -c "import uis_internal_utils" ; pip show uis-internal-utils | grep Version

echo; echo ">>> Fix: pin the exact version (better: hashes, or a single proxying index)"
pip install -q --force-reinstall --no-index --find-links internal-index --find-links public-index "uis-internal-utils==1.2.0"
python -c "import uis_internal_utils" ; pip show uis-internal-utils | grep Version
