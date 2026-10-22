#!/usr/bin/env bash
set -u

# Pick a compiler that actually works on this machine.
# On macOS, prefer Apple clang (cc / clang from the Xcode Command Line Tools)
# over a Homebrew gcc, whose fixincludes-patched <stdio.h> breaks after an
# Xcode/SDK update with: fatal error: _stdio.h: No such file or directory.
# Override by exporting CC yourself, e.g.  CC=gcc-14 bash run_demo.sh
if [ -z "${CC:-}" ]; then
  for cand in cc clang gcc; do
    if command -v "$cand" >/dev/null 2>&1; then CC="$cand"; break; fi
  done
fi
: "${CC:?No C compiler found. Install Xcode CLT:  xcode-select --install}"
echo ">>> using compiler: $CC  ($($CC --version | head -1))"
echo

# Remove any stale binaries so the demo can never run an old build by mistake.
rm -f overflow overflow_asan overflow_rs

"$CC" -O0 -fno-stack-protector -o overflow overflow.c
echo ">>> normal input";            ./overflow alice
echo; echo ">>> 9 characters: one byte too many"; ./overflow AAAAAAAAB
echo; echo ">>> longer input, built with AddressSanitizer (-fsanitize=address)"
"$CC" -O0 -g -fsanitize=address -o overflow_asan overflow.c
./overflow_asan AAAAAAAAAAAAAAAAAAAA 2>&1 | grep -E "ERROR|WRITE|#1 " | head -3

if command -v rustc >/dev/null; then
  echo; echo ">>> Rust version"; rustc -O -o overflow_rs overflow.rs && ./overflow_rs AAAAAAAAB
fi